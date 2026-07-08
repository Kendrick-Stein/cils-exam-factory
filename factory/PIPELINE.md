# Paper Generation Pipeline (S0–S7)

Source of truth for generating one **session** (a dated batch) of practice papers. Default: exam `cils`, levels `A1,A2,B1,B2,C1`, session = today's local date.

## Actors

| Role | Claude Code | Codex / other harness |
|---|---|---|
| **Orchestrator** | main conversation running `/genpapers` | main context following `AGENTS.md` |
| **corpus-hunter** | Agent tool, role file `.claude/agents/corpus-hunter.md` | same prompt run in-context |
| **item-writer** | Agent tool, role file `.claude/agents/item-writer.md` | same prompt run in-context |
| **blind-solver** | Agent tool, role file `.claude/agents/blind-solver.md` — **fresh context, gets ONLY `paper.md`, no web tools** | fresh `codex exec --sandbox read-only` subprocess |
| **format-auditor** | Agent tool, role file `.claude/agents/format-auditor.md` | same prompt run in-context |

Levels are independent: run S1–S5 for different levels in parallel where the harness allows; S6–S7 run once per session at the end.

## Item ID convention

Paper shows plain per-prova numbering (fidelity with real papers). Internally, every objective item has a qualified ID: `L<prova>.<n>` (comprensione della lettura), `S<prova>.<n>` (analisi delle strutture di comunicazione), `W<n>` (produzione scritta task n). Example: `S2.5` = strutture, prova 2, item 5. `answers.md`, blind-solver output and manifests use qualified IDs.

## Stages

### S0 — Scaffold (orchestrator)
- Create `papers/<date>/<LEVEL>/`; write `manifest.yaml` stub: `exam`, `level`, `session`, `title` (from `exam.yaml` `level_name` + "· Esercitazione"), `status: draft`, empty `sources`, `pipeline.generator`, `pipeline.template`.
- Load the level's entry in `factory/exams/cils/exam.yaml` and its template `factory/exams/cils/templates/<LEVEL>.md`.

### S1 — Corpus (corpus-hunter)
- **Input:** the level's `testo` slots from `exam.yaml`; `factory/corpus/sources.yaml`; `factory/corpus/cefr-criteria.md`.
- **Work:** for each text slot, find up to 2 candidate authentic texts (different publishers when possible), fetch, clean to plain prose (drop nav/ads/captions), record `{url, title, publisher, published?, accessed}`, grade CEFR per the criteria (cite concrete grammar/lexis evidence), propose the adapted length.
- **Output:** `papers/<date>/<LEVEL>/sources.md` — one section per slot: metadata block + cleaned text + CEFR verdict + adaptation note.
- **Gate (orchestrator):** every slot has ≥1 accepted candidate matching genre + target CEFR + length band. Missing slots → re-run S1 for those slots with different sources (max 2 attempts), else abort level (`status: draft`, `reason: corpus`).
- **Manifest:** append `{stage: corpus, at}` and the accepted entries under `sources:` (with `used_in`, `adapted: true`, `words_used` filled at S2).

### S2 — Authoring (item-writer)
- **Input:** template, `sources.md`, `factory/exams/cils/style-guide.md`, `factory/validation/checklist.md` (item-quality section).
- **Work:** fill the template **exactly** — item counts, points, durations and consegna wording are immutable; adapt each text to its length band, ending with the attribution line «Testo adattato da: *Titolo*, Publisher, URL, consultato il GG/MM/AAAA»; write the answers part: chiavi table (`Item | Risposta | Spiegazione`, explanations 1–3 lines with a short 中文 note on the tricky point), one 范文 per writing task (inside the required word range, level-appropriate, followed by 3–5 "espressioni utili"), and the **Glossario da ricordare** (15–25 rows: Parola/Espressione | Categoria | 中文 | EN | Esempio dal testo).
- **Output:** complete `paper.md` + `answers.md` (front-matter per plan schema) + `key.json` (machine-readable key: `{"L1.1": "B", …, "L3": "A-D-…", "S1.1": "la", …}`) for mechanical reconciliation.
- **Gate (orchestrator, mechanical):** per-prova item counts match `exam.yaml`; no unreplaced `{{slots}}`; attribution present per text; writing word ranges printed; points sums correct.

### S3 — Blind validation (blind-solver, isolation is the point)
- **Input:** `paper.md` ONLY. No `answers.md`, no `sources.md`, no web access, no other repo files. Mechanics: run `python3 scripts/blind_validation.py prepare --paper-dir papers/<date>/<LEVEL>` to copy `paper.md` alone into an isolated dir outside the repo (`/tmp/cils-blind-<session>-<level>/`) and hand the solver only that path — or paste the paper text into the prompt.
- **Work:** solve every objective item → JSON `{"L1.1": "B", ...}` with per-item confidence (`hi|med|lo`); flag list `{item_id, reason}` for anything ambiguous, unanswerable from the text alone, with overlapping options, or with more than one defensible answer. For writing tasks: verify the consegna is self-contained and the word range is printed (do not write essays).
- **Output:** returned to orchestrator (stored under `papers/<date>/<LEVEL>/` only if debugging; not required).

### S4 — Reconcile (orchestrator + item-writer)
- Compare key vs blind answers with `python3 scripts/blind_validation.py reconcile --paper-dir papers/<date>/<LEVEL> --blind-output <file> --report papers/<date>/<LEVEL>/blind-validation.json --write-manifest`. **Failing item** = mismatch with the key **or** any ambiguity flag (flags fail even when the answer matches).
- For each failing item: item-writer gets the item, the blind-solver's answer/reasoning, and must repair it (fix stem/distractors/text reference — or replace the item) keeping counts/points/consegne identical.
- Re-validate: fresh blind-solver on the **affected prove only** (send those prova blocks with their texts).
- **Gate:** 100% agreement on objective items and 0 flags within **max 2 repair rounds**; otherwise `status: draft`, `reason: validation`, continue with other levels.
- **Manifest:** append each `blind_validation` (with `agreement: "n/m"`, `flags`) and `reconcile` (with `round`, `fixed_items`) entry; set `validation:` block with final numbers.

### S5 — Format audit (format-auditor)
- **Input:** `paper.md`, `answers.md`, template, `exam.yaml`, `factory/validation/checklist.md` (format section), style-guide.
- **Work:** line-by-line checklist verdict (PASS/FAIL + fix list): structure order, headings, counts, point statements, durations, word ranges, attribution lines, answers/glossario completeness, markdown conventions (consegne as blockquotes, tables well-formed).
- Orchestrator applies fixes; one re-audit if anything failed. PASS required.
- **Manifest:** append `{stage: format_audit, result}`; on PASS set `status: published`.

### S6 — Build (deterministic)
- `python3 scripts/build_site.py` (add `--no-pdf` only for previews). The builder enforces the publish gate for `status: published` manifests: validation pass, 100% blind agreement, zero flags, zero mismatches, and latest `format_audit` result pass. Verify exit 0 and that `docs/papers/<date>/<LEVEL>/` contains paper/answers in html+pdf+md for every published level.
- Optional status audit before publish: `python3 scripts/paper_status.py --session <date> --levels A1,A2,B1,B2,C1` reports publishable levels and the next missing stage for drafts.

### S7 — Publish
- Stage only publishable levels plus docs: `git add papers/<date>/<published-levels> docs && git commit -m "feat(papers): <date> <levels>" && git push`. Skipped with `--no-publish`. Draft levels are excluded by the build and must not be staged as a completed session; report them explicitly to the user. Never force-push; published sessions are immutable (corrections = new session).

## Failure summary

| Stage | Retry | On final failure |
|---|---|---|
| S1 corpus | 2 attempts per missing slot | level → draft (`reason: corpus`) |
| S2 gates | 1 rewrite | level → draft (`reason: authoring`) |
| S3/S4 | ≤2 repair rounds | level → draft (`reason: validation`) |
| S5 | 1 re-audit | level → draft (`reason: format`) |
| S6 | fix build env, retry once | stop before publish, report |

A drafted level never blocks the others; the session publishes whatever passed all gates.

## Extensibility

`--exam <name>` switches every read to `factory/exams/<name>/` (exam.yaml, templates, style-guide, analysis). The pipeline, roles, checklist mechanics and build layer are exam- and language-agnostic.
