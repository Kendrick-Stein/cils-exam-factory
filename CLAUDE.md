# CILS Exam Factory

Generates CILS-style Italian practice papers (A1–C1, **no listening/oral**) from authentic web texts, validates them with independent blind-solving, and publishes them to GitHub Pages.

## The one command

`/genpapers [levels] [date] [--no-publish]` → orchestration in `.claude/skills/genpapers/SKILL.md`.
Everything pipeline-critical lives under `factory/` — read `factory/PIPELINE.md` first; it is the source of truth for the workflow.

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
| `scripts/build_site.py` | `papers/` → `docs/` (HTML + PDF + index); `docs/` is the GitHub Pages root |
| `papers/<date>/<LEVEL>/` | Generated output + `manifest.yaml` (provenance) |
| `reference/` | LOCAL copies of official papers — gitignored, **never commit or republish** |
| `notes/` | Design specs & implementation plans |

## Hard rules

1. **Blind-solver isolation:** blind-solver agents receive ONLY `paper.md` — never `answers.md`, `sources.md`, or web access.
2. **Publish gate:** a paper is publishable only when blind-solve agreement is 100% on objective items, 0 ambiguity flags, and format audit is PASS. Otherwise `manifest.yaml` keeps `status: draft` and the build skips it.
3. **Immutability:** published papers never change; corrections go into a new dated session.
4. **Authenticity:** every source text is a real published text, adapted with credit («Testo adattato da: …») and logged in the manifest.
5. **Copyright:** nothing from `reference/` may be committed, and source texts are used only as attributed adapted excerpts within level norms.

## Conventions

- Session dir = `YYYY-MM-DD` (local date of generation). One session may contain multiple levels.
- Commits: `feat(papers): <date> <levels>` for generated content; `feat(cils): …` for exam config; `feat:`/`fix:`/`docs:` otherwise.
- After generation: `python3 scripts/build_site.py`, commit `papers/` + `docs/` together, push (that is the publish step).
- Adding a new exam (CELI, DELF, JLPT…): create `factory/exams/<exam>/` mirroring the CILS layout; pipeline, agents and scripts are exam-agnostic.
