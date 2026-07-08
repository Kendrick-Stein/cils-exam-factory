---
name: make-paper
description: Repo-local Codex entrypoint for generating CILS practice papers when the user says Make Paper, genpapers, make paper, or 生成试卷.
---

# Make Paper

Use this skill when the user asks for `Make Paper`, `genpapers`, `make paper`, `/genpapers`, or 生成试卷 in this repository.

This is a Codex-facing entrypoint for the same factory used by Claude. Treat `AGENTS.md` as the harness-level instruction file, then read `factory/PIPELINE.md` before doing any generation work. The pipeline is the source of truth: run S0 through S7 for each requested level.

Defaults:
- exam: `cils`
- levels: `A1,A2,B1,B2,C1`
- session date: today's local date unless the user provides one; use `YYYY-MM-DD-rN` for a same-day revision session that preserves published-paper immutability

Core workflow:
1. Read `factory/PIPELINE.md`, `AGENTS.md`, and the relevant CILS exam config/template files referenced by the pipeline.
2. Run S0-S7 for the requested levels, unless the user passes `--no-publish`.
3. Keep S3 blind validation isolated. Use the deterministic helper to copy ONLY the student `paper.md` into `/tmp/cils-blind-<date>-<LEVEL>/paper.md`, then run the solver against that isolated file:

   ```bash
   python3 scripts/blind_validation.py prepare --paper-dir papers/<date>/<LEVEL>
   codex exec --sandbox read-only "You are a candidate taking a CILS exam. Solve the paper at /tmp/cils-blind-<date>-<LEVEL>/paper.md using ONLY that file. Return: (1) answers as a JSON object {\"item_id\": \"answer\"}, (2) a list of item_ids you consider ambiguous or unanswerable, with one-line reasons. Do not open any other file or the web."
   ```

4. Save blind output to a file and reconcile it mechanically before any repair prompt:

   ```bash
   python3 scripts/blind_validation.py reconcile --paper-dir papers/<date>/<LEVEL> --blind-output <blind-output.txt> --report papers/<date>/<LEVEL>/blind-validation.json --write-manifest
   ```

   Any mismatch or flag is a failing item and must go back through S4 repair; do not mark the level publishable until the reconcile report passes, S5 format audit passes, and S5b quality audit passes.

5. Before S6, run the deterministic format and quality gates:

   ```bash
   python3 scripts/format_audit.py --session <date> --levels <levels> --report papers/<date>/format-audit.json --write-manifest
   ```

   ```bash
   python3 scripts/paper_quality_audit.py --session <date> --levels <levels> --report papers/<date>/quality-audit.json --write-manifest
   ```

   Repair any failures before publishing. The format gate checks student-paper structure and leakage; the quality gate checks official-style student-paper separation, declared variant/source policy, reading length, B2/C1 item depth, and cross-level source reuse.

6. For S6, run:

   ```bash
   python3 scripts/build_site.py
   ```

7. For S7, publish only after checking manifests: each staged level must be `status: published`, with 100% blind agreement, zero flags, quality PASS, and format PASS. Stage those publishable paper directories plus `docs/`, then commit and push. Skip this step when `--no-publish` is present.

Useful status check before build/publish:

```bash
python3 scripts/paper_status.py --session <date> --levels A1,A2,B1,B2,C1
```

Do not expose the blind solver to anything except `paper.md`. Preserve the hard rules in `CLAUDE.md`: blind-solver isolation, publish gates, published-paper immutability, source attribution, and never committing `reference/`.
