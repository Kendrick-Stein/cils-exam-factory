# Quality gates

Two audiences: **item-writer** (write to these rules), **blind-solver/format-auditor** (fail anything that breaks them). A paper publishes only with zero open failures (see `factory/PIPELINE.md` S4–S5).

## A. Item quality (objective items)

1. **Unique defensible answer**, derivable from the paper alone — no outside knowledge, no trivia, no "cultura generale" shortcuts.
2. **Distractors** are plausible but wrong *for a reason locatable in the text*; same part of speech / comparable length as the key; no joke options.
3. Options are **mutually exclusive**; no synonyms of each other; no "tutte le precedenti"; no absolute giveaways (*sempre/mai*) that flag the key.
4. **Vero/Falso**: decidable strictly from the text; falsi built on real contrasts (numbers, agents, causes), not on nitpicks; no double negation beyond level.
5. **Cloze grammaticale** (open): exactly **one** form fits the gap (check gender/number/elision alternatives — if «l'»/«la» both work, re-cut the gap). **Cloze lessicale MC**: distractors same POS, all grammatical in the slot, only the key semantically right.
6. **Riordino/abbinamento**: unique valid solution; sequence signalled by connectives/anaphora, not by guesswork; matching has the exact distractor count the template states.
7. Items follow **text order** where the real paper does (MC comprehension); one item ↔ one text passage (no item answerable from another item).
8. Where the official paper provides an **esempio (0)**, the template's example slot is filled with a genuinely trivial case.
9. **Writing tasks**: consegna self-contained, word range printed, topic doable with level grammar/lexis; no cultural insider knowledge.
10. **Cloze verbi — one forced tense per gap** (the recurring blind-validation killer): every gap must be pinned by an explicit marker — hard past anchor up front («Domenica scorsa», «Nel 2019»); «ogni giorno/sempre/mentre» for imperfetto; explicit «Adesso/Oggi» pivot before any present gap; passato remoto only with a printed cue (cleft «Fu … che»); «In questi anni / Finora / fino a oggi» to force passato prossimo. A solver who can defend two tenses = failed item.
11. **Auxiliary/clitic boundary**: the whole verb form (aux + participle, reflexive clitic) sits **inside** the gap; never pre-print «ho»/«mi» before the blank. No essere-aux passato prossimo with unspecified-gender subject (participle agreement would admit two forms).
12. **No free-variant open gaps**: è/viene passive (use perfect passive or active), infinito passato (aver/avere), «di cui/del quale», bare vs articulated preposition, open quantifiers — restructure so exactly one surface form fits, or key every variant with `||`.
13. **Trasformazioni (C1 S4)**: the printed starter forces the structure (e.g. «QUALORA» → congiuntivo); the key lists ALL meaning-preserving rewrites with `||` — synonym choice is a correct answer, not a defect.

## B. Paper format (auditor checklist — verdict PASS/FAIL per line)

1. Front-matter valid (`exam, level, level_name, session, kind`).
2. Section order, titles, durations and per-section point statements match `exam.yaml`.
3. **Item counts per prova exactly** as `exam.yaml`; point sums correct (incl. scaling notes, e.g. B1 strutture 24→20).
4. Consegne verbatim from the template (no improvised instructions); consegne rendered as blockquotes.
5. Source attribution lines are absent from `paper.md`; every source is traceable in `manifest.yaml`; authored text length stays inside the band in `exam.yaml`.
6. No unreplaced `{{slots}}`, no English/中文 in `paper.md` (Italian only); items numbered per prova starting at 1 (esempio = 0).
7. `answers.md`: chiavi table complete with qualified IDs (`L1.1`…), one spiegazione per item (with 中文 note), 范文 per writing task **within the printed word range** (count the words), 3–5 espressioni utili per 范文, Glossario 15–25 rows with all 5 columns filled.
8. Markdown mechanics: tables well-formed, gaps rendered `__(n)__`, options as `A. / B. / C. (/ D.)` lines, no broken headings.
9. Manifest: sources listed with url/publisher/accessed/used_in; stages log present; `validation` block filled; `status` correct.

## C. Reconcile policy (orchestrator)

- Failing item = blind-solver mismatch **or** any ambiguity flag (a flag fails the item even when answers agree).
- Repairs keep counts/points/consegne identical; re-validate affected prove with a **fresh** blind-solver; max 2 rounds, then `status: draft`.

## D. Deterministic quality audit

Run `python3 scripts/paper_quality_audit.py --session <date> --levels <levels> --report papers/<date>/quality-audit.json --write-manifest` before build/publish.

The audit must PASS with zero issues. It checks:
- `paper.md` keeps study aids out of the student copy; explanations, 范文, 中文 notes and glossario belong only in `answers.md`.
- `manifest.yaml` declares `quality.variant_profile`, `quality.source_policy: excerpt-first`, `quality.source_attribution: manifest-only`, and a bounded `quality.max_rewrite`.
- `manifest.yaml` contains every `exam.yaml` text slot used by the level, including sub-slots such as `T3a` for microtexts, and each source declares `words_used`.
- Reading texts meet the `exam.yaml` length bands after authoring, not only in `sources.md`.
- Structure-analysis texts with configured `testo.parole` also meet the `exam.yaml` length bands; C1 transformation P4 uses one continuous administrative/institutional text, not unrelated sentences.
- Student copies do not print visible `Testo adattato da` source lines; source credit stays in `manifest.yaml`.
- B2/C1 reading items include enough interpretation/inference/purpose/causal framing and are not only direct numeric lookup.
- Source URLs are not reused across levels in the same session unless explicitly justified with `allow_cross_level_reuse: true`.
- B2/C1 student copies follow the current official-paper convention of not printing inline per-prova scoring statements.
