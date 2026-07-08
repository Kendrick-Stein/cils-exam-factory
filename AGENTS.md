# Agent instructions (Codex CLI and other harnesses)

This repo is an exam-paper factory. When asked to generate papers ("genpapers", "生成试卷", "make paper"):

1. Read `factory/PIPELINE.md` and run stages S0–S7 for each requested level (default: `A1,A2,B1,B2,C1`, exam CILS, session = today's date).
2. If your harness has no subagent tool, run stages sequentially in one context, **except blind validation (S3), which must be independent**. Run it as a fresh subprocess with no shared context:

   ```bash
   codex exec --sandbox read-only "You are a candidate taking a CILS exam. Solve the paper at papers/<date>/<LEVEL>/paper.md using only that file. Return: (1) answers as a JSON object {\"item_id\": \"answer\"}, (2) a list of item_ids you consider ambiguous or unanswerable, with one-line reasons. Do not open any other file or the web."
   ```

3. File formats (front-matter, `manifest.yaml` schema, `docs/` layout) are defined in `notes/plans/2026-07-08-cils-exam-factory.md`; quality gates in `factory/validation/checklist.md`.
4. Build + publish: `python3 scripts/build_site.py`, then `git add papers docs && git commit && git push`.
5. The **Hard rules** in `CLAUDE.md` apply verbatim: blind-solver isolation, publish gates, immutability of published papers, source attribution, and never committing `reference/`.
