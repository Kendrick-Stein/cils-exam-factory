# Paper Generation Pipeline (S0–S7)

Source of truth for generating one **session** (a dated batch) of practice papers. Default: exam `cils`, levels `A1,A2,B1,B2,C1`, session = today's local date. Use a revision session such as `YYYY-MM-DD-r2` when regenerating the same day without overwriting a published `YYYY-MM-DD` session.

## Actors

| Role | Claude Code | Codex / other harness |
|---|---|---|
| **Orchestrator** | main conversation running `/genpapers` | main context following `AGENTS.md` |
| **corpus-hunter** | Agent tool, role file `.claude/agents/corpus-hunter.md` | same prompt run in-context |
| **item-writer** | Agent tool, role file `.claude/agents/item-writer.md` | same prompt run in-context |
| **blind-solver** | Agent tool, role file `.claude/agents/blind-solver.md` — **fresh context, gets ONLY `paper.md`, no web tools** | fresh `codex exec --sandbox read-only` subprocess |
| **format-auditor** | deterministic `scripts/format_audit.py` gate | same local command |
| **quality-auditor** | deterministic `scripts/paper_quality_audit.py` gate | same local command |

Levels are independent: run S1–S5 for different levels in parallel where the harness allows; S6–S7 run once per session at the end.

## Item ID convention

Paper shows plain per-prova numbering (fidelity with real papers). Internally, every objective item has a qualified ID: `L<prova>.<n>` (comprensione della lettura), `S<prova>.<n>` (analisi delle strutture di comunicazione), `W<n>` (produzione scritta task n). Example: `S2.5` = strutture, prova 2, item 5. `answers.md`, blind-solver output and manifests use qualified IDs.

## Stages

### S0 — Scaffold (orchestrator)
- Preflight: if `papers/<date>/<LEVEL>/manifest.yaml` already exists with `status: published`, refuse to overwrite it. Use a new date or a same-day revision session such as `YYYY-MM-DD-r2`.
- Create `papers/<date>/<LEVEL>/`; write `manifest.yaml` stub: `exam`, `level`, `session`, `title` (from `exam.yaml` `level_name` + "· Esercitazione"), `status: draft`, empty `sources`, `pipeline.generator`, `pipeline.template`.
- Load the level's entry in `factory/exams/cils/exam.yaml` and its template `factory/exams/cils/templates/<LEVEL>.md`.

### S1 — Corpus (corpus-hunter)
- **Input:** the level's `testo` slots from `exam.yaml`; `factory/corpus/sources.yaml`; `factory/corpus/cefr-criteria.md`.
- **Work:** for each text slot, find up to 2 candidate authentic texts (different publishers when possible), fetch, clean to plain prose (drop nav/ads/captions), record `{url, title, publisher, published?, accessed}`, grade CEFR per the criteria (cite concrete grammar/lexis evidence), propose the adapted length.
- **Output:** `papers/<date>/<LEVEL>/sources.md` — one section per slot: metadata block + cleaned text + CEFR verdict + adaptation note.
- **Gate (orchestrator):** every slot has ≥1 accepted candidate matching genre + target CEFR + length band. Missing slots → re-run S1 for those slots with different sources (max 2 attempts), else abort level (`status: draft`, `reason: corpus`).
- **Manifest:** append `{stage: corpus, at}` and the accepted entries under `sources:` (with `used_in`, `adapted: true`, `words_used` filled at S2).

### S2 — Authoring (item-writer, **one task per prova**) + deterministic assembly
- **Granularity:** one authoring task per prova — input is ONE source text (its slot section of `sources.md`) + that prova's spec from `exam.yaml` + checklist §A + the list of `{{SLOT}}` names to fill; output is ONE fragment `papers/<date>/<LEVEL>/fragments/<ID>.json` (`{"prova", "slots", "answer_slots", "key", "glossario_candidates"}`). Writing tasks (`W.json`) and the Glossario (`GLOSSARIO.json`, built from the per-prova candidates) are small fragments of their own. The LLM never emits covers, consegne, durations, answer sheets or section skeletons — those are immutable template text.
- **Assembly (no LLM):** `python3 scripts/assemble_paper.py --paper-dir papers/<date>/<LEVEL>` merges the fragments into `paper.md` + `answers.md` + `key.json`, strips template comments, and fails listing every unfilled slot / duplicate key ID.
- **Answers content per fragment:** chiavi rows with qualified IDs + spiegazione 1–3 lines (short 中文 note on the tricky point); the writing fragment carries one 范文 per task inside the printed word range + 3–5 espressioni utili; glossario 15–25 rows.
- **Gate (orchestrator, mechanical):** assembler exit 0; counts/points/section order via `format_audit.py`; manifest source entries complete (`words_used` from the writers' replies, `quality` block); source credit only in `manifest.yaml`.
- **Manifest:** the orchestrator owns `manifest.yaml` (fragment writers run in parallel and never touch it).

### S3 — Blind validation (blind-solver, isolation is the point)
- **Input:** `paper.md` ONLY. No `answers.md`, no `sources.md`, no web access, no other repo files. Mechanics: run `python3 scripts/blind_validation.py prepare --paper-dir papers/<date>/<LEVEL>` to copy `paper.md` alone into an isolated dir outside the repo (`/tmp/cils-blind-<session>-<level>/`) and hand the solver only that path — or paste the paper text into the prompt. For per-prova re-validation add `--prova L3,S2`: only those self-contained prova blocks are extracted into their own isolated dir.
- **Work:** solve every objective item → JSON `{"L1.1": "B", ...}` with per-item confidence (`hi|med|lo`); flag list `{item_id, reason}` for anything ambiguous, unanswerable from the text alone, with overlapping options, or with more than one defensible answer. For writing tasks: verify the consegna is self-contained and the word range is printed (do not write essays).
- **Output:** returned to orchestrator (stored under `papers/<date>/<LEVEL>/` only if debugging; not required).

### S4 — Reconcile (orchestrator + item-writer, **per prova**)
- Compare key vs blind answers with `python3 scripts/blind_validation.py reconcile --paper-dir papers/<date>/<LEVEL> --blind-output <file> --report papers/<date>/<LEVEL>/blind-validation.json --write-manifest`. **Failing item** = mismatch with the key **or** any ambiguity flag (flags fail even when the answer matches).
- **Repair unit = the prova; executor = a FRESH item-writer** (never resume the original authoring agent: transcript replay is the dominant token cost). It receives only the failing prova's fragment + its source text + the defect list (blind answer/reasoning per item); it may fix stems/keys/distractors **or change how an item tests the text**, keeping counts/points/consegna fixed, then rewrites that fragment. Orchestrator re-runs `assemble_paper.py`.
- Re-validate the **affected prove only**: `prepare --prova <ids>` → fresh solver on the extract → `python3 scripts/blind_validation.py merge-output --base <previous full blind-output> --patch <partial output> --out <merged>` → full `reconcile` on the merged file (local diff — no re-solving of untouched prove).
- **Gate:** 100% agreement on objective items and 0 flags within **max 2 repair rounds**; otherwise `status: draft`, `reason: validation`, continue with other levels.
- **Manifest:** append each `blind_validation` (with `agreement: "n/m"`, `flags`) and `reconcile` (with `round`, `fixed_items`) entry; set `validation:` block with final numbers.

### S5 — Format audit (format-auditor)
- **Input:** `paper.md`, `answers.md`, `key.json`, `manifest.yaml`, template, `exam.yaml`, `factory/validation/checklist.md` (format section), style-guide.
- **Work:** run `python3 scripts/format_audit.py --session <date> --levels <levels> --report papers/<date>/format-audit.json --write-manifest`. It checks required files, front matter/session/level consistency, official-style cover and answer-sheet markers, section order, prova heading counts, source attribution kept out of `paper.md`, B2/C1 inline point leakage, study-aid leakage, and valid `key.json`.
- Orchestrator applies fixes; one re-audit if anything failed. PASS required.
- **Manifest:** append `{stage: format_audit, result}`; keep `status: draft` until S5b quality audit also passes.

### S5b — Quality audit (deterministic)
- **Input:** `paper.md`, `manifest.yaml`, `exam.yaml`, and the whole session's manifests.
- **Work:** run `python3 scripts/paper_quality_audit.py --session <date> --levels <levels> --report papers/<date>/quality-audit.json --write-manifest`.
- **Gate:** PASS required. The audit checks official-style student-paper separation, reading and structure text length bands, C1 P4 continuous-text shape, B2/C1 item-depth signals, declared variant/source policy, source slot coverage/`words_used`, and cross-level source reuse. Any failure keeps the affected level in `draft` until repaired and re-audited.
- **Manifest:** append `{stage: quality_audit, result, issues}`; keep `quality.audit_result: pass`. Only after blind validation, format audit and quality audit all pass may the orchestrator set `status: published`.

### S6 — Build (deterministic)
- `python3 scripts/build_site.py` (add `--no-pdf` only for previews). The builder enforces the publish gate for `status: published` manifests: validation pass, 100% blind agreement, zero flags, zero mismatches, latest `quality_audit` result pass, and latest `format_audit` result pass. Verify exit 0 and that `docs/papers/<date>/<LEVEL>/` contains `paper.pdf` and `answers.pdf` for every published level (the site publishes PDFs only; md sources stay in `papers/`).
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
| S5b | repair, re-audit | level → draft (`reason: quality`) |
| S6 | fix build env, retry once | stop before publish, report |

A drafted level never blocks the others; the session publishes whatever passed all gates.

## Extensibility

`--exam <name>` switches every read to `factory/exams/<name>/` (exam.yaml, templates, style-guide, analysis). The pipeline, roles, checklist mechanics and build layer are exam- and language-agnostic.
