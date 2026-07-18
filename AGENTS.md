# Agent instructions (Codex CLI and other harnesses)

This repo is an exam-paper factory. When asked to generate papers (`/genpapers`, `Make Paper`, "genpapers", "生成试卷", "make paper"):

1. Read `factory/PIPELINE.md` and run stages S0–S7 for each requested level (default: `A1,A2,B1,B2,C1`, exam CILS, session = today's date; use `YYYY-MM-DD-rN` for a same-day revision session).
2. If your harness has no subagent tool, run stages sequentially in one context, **except blind validation (S3), which must be independent**. Use the helper to copy only the student paper into an isolated directory outside the repo, then run a fresh subprocess with no shared context:

   ```bash
   python3 scripts/blind_validation.py prepare --paper-dir papers/<date>/<LEVEL>
   codex exec --sandbox read-only "You are a candidate taking a CILS exam. Solve the paper at /tmp/cils-blind-<date>-<LEVEL>/paper.md using ONLY that file. Return: (1) answers as a JSON object {\"item_id\": \"answer\"}, (2) a list of item_ids you consider ambiguous or unanswerable, with one-line reasons. Do not open any other file or the web."
   python3 scripts/blind_validation.py reconcile --paper-dir papers/<date>/<LEVEL> --blind-output <blind-output.txt> --report papers/<date>/<LEVEL>/blind-validation.json --write-manifest
   ```

3. File formats (front-matter, `manifest.yaml` schema, `docs/` layout) are defined in `notes/plans/2026-07-08-cils-exam-factory.md`; quality gates in `factory/validation/checklist.md`.
4. Before build/publish, run `python3 scripts/format_audit.py --session <date> --levels <levels> --report papers/<date>/format-audit.json --write-manifest`, then `python3 scripts/paper_quality_audit.py --session <date> --levels <levels> --report papers/<date>/quality-audit.json --write-manifest`, and repair every failure.
5. Build + publish: `python3 scripts/build_site.py`, then stage only levels whose manifests passed the publish gate (`status: published`, blind agreement 100%, zero flags, quality PASS, format PASS) plus `docs/`; commit and push, then merge the working branch into `main` and push `main` (Pages deploys from `main`'s `docs/`). Publishing is automatic once the gates pass (user directive 2026-07-18) — do not wait for confirmation. Draft or failed levels may remain in the worktree, but do not publish them as a completed session.
6. The **Hard rules** in `CLAUDE.md` apply verbatim: blind-solver isolation, publish gates, immutability of published papers, source attribution, and never committing `reference/`.
