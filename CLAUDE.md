# CILS Exam Factory

Generates CILS-style Italian practice papers (A1–C1, **no listening**; produzione orale is included as a self-study section with memorizable model answers in the chiavi — user directive 2026-07-18) from authentic web texts, validates them with independent blind-solving, and publishes them to GitHub Pages.

## The one command

`/genpapers [levels] [date] [--no-publish]` → orchestration in `.claude/skills/genpapers/SKILL.md`.
Everything pipeline-critical lives under `factory/` — read `factory/PIPELINE.md` first; it is the source of truth for the workflow.

Codex users can invoke the same factory as `Make Paper` / `genpapers`; that entrypoint is documented in `AGENTS.md` and `.codex/skills/make-paper/SKILL.md`.

## Execution mode (recommended: Codex executes, Claude orchestrates)

User directive (2026-07-08): **Claude Code only plans, gates, owns manifests, builds and publishes; heavy stages run on Codex** when cost or Claude subagent limits matter.

- **Unit of work = one prova** (user directive 2026-07-13): authoring/repair tasks each cover a single prova (input: one text + prova spec → output: one fragment JSON); `scripts/assemble_paper.py` assembles fragments into `paper.md`/`answers.md`/`key.json` locally — no LLM ever emits template skeleton text.
- **Executor tiering** (same directive — don't send everything to the strongest executor): local scripts for assembly/audits/reconcile; cheap models (Codex low / Sonnet) for blind solving and corpus; strong models (Codex high / Opus) only for hard B2/C1 prove and 2nd-round repairs. Matrix in `.claude/skills/genpapers/SKILL.md`.
- Stage task dispatch to Codex: `node "$(ls -d ~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs | tail -1)" task --background --write "<prova prompt>"` → poll `status <job-id>`, fetch `result <job-id>`.
- S3 blind validation: fresh `codex exec --sandbox read-only` (or a fresh Sonnet blind-solver) on an isolated `/tmp/cils-blind-…/paper.md` copy — whole paper or `--prova` extract; repairs re-validate only the affected prove via `blind_validation.py merge-output`.
- Repairs always use a FRESH agent per prova — never resume the original authoring agent (transcript replay dominates cost).

## Map

| Path | What it is |
|---|---|
| `factory/PIPELINE.md` | Runtime workflow S0–S7 (source of truth) |
| `factory/exams/cils/exam.yaml` | Structure, item counts, points, timing per level |
| `factory/exams/cils/templates/*.md` | Paper skeletons with **verbatim consegne** — never improvise instruction wording |
| `factory/exams/cils/analysis/*.md` | Evidence extracted from official dic-2024 papers |
| `factory/exams/cils/style-guide.md` | Layout & wording conventions from the real papers |
| `factory/corpus/sources.yaml`, `cefr-criteria.md` | Where texts come from; how CEFR level is graded |
| `factory/validation/checklist.md` | Quality gates |
| `scripts/assemble_paper.py` | Merges per-prova `fragments/*.json` into `paper.md` + `answers.md` + `key.json` (no LLM) |
| `scripts/format_audit.py` | Deterministic paper-format, section-order, leakage and key-file audit |
| `scripts/paper_quality_audit.py` | Deterministic official-style, difficulty, length and cross-level reuse audit |
| `scripts/build_site.py` | `papers/` → `docs/` (PDF only + index; HTML is a render intermediate); `docs/` is the GitHub Pages root |
| `papers/<date>/<LEVEL>/` | Generated output + `manifest.yaml` (provenance) |
| `reference/` | LOCAL copies of official papers — gitignored, **never commit or republish** |
| `notes/` | Design specs & implementation plans |

## Hard rules

1. **Blind-solver isolation:** blind-solver agents receive ONLY `paper.md` — never `answers.md`, `sources.md`, or web access.
2. **Publish gate:** a paper is publishable only when blind-solve agreement is 100% on objective items, 0 ambiguity flags, quality audit is PASS, and format audit is PASS. Otherwise `manifest.yaml` keeps `status: draft` and the build skips it.
3. **Immutability:** published papers never change; corrections go into a new dated or same-day revision session.
4. **Authenticity:** every source text is a real published text; adaptations are logged and credited in `manifest.yaml`, not printed as source lines in the student paper.
5. **Copyright:** nothing from `reference/` may be committed, and source texts are used only as manifest-attributed adapted excerpts within level norms.

## Conventions

- Session dir = `YYYY-MM-DD` (local date of generation) or `YYYY-MM-DD-rN` for a same-day revision that preserves immutability. One session may contain multiple levels.
- Commits: `feat(papers): <date> <levels>` for generated content; `feat(cils): …` for exam config; `feat:`/`fix:`/`docs:` otherwise.
- After generation: run `python3 scripts/format_audit.py --session <date> --levels <levels> --report papers/<date>/format-audit.json --write-manifest`, then `python3 scripts/paper_quality_audit.py --session <date> --levels <levels> --report papers/<date>/quality-audit.json --write-manifest`, then `python3 scripts/build_site.py`, commit `papers/` + `docs/` together, push (that is the publish step).
- Adding a new exam (CELI, DELF, JLPT…): create `factory/exams/<exam>/` mirroring the CILS layout; pipeline, agents and scripts are exam-agnostic.
