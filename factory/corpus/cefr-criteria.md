# CEFR grading criteria for candidate texts (Italian)

How corpus-hunter decides whether a fetched text fits the target level. Verdict = rubric judgment + anchor comparison + quantitative sanity check. When in doubt, grade harder (a too-difficult text is worse than re-fetching).

## 1. Rubric per level

| Level | Grammar the text may assume | Lexis | Syntax |
|---|---|---|---|
| **A1** | presente indicativo, articoli, c'è/ci sono, possessivi base | vita quotidiana concreta (casa, cibo, orari, famiglia); quasi solo Vocabolario di base | frasi semplici, coordinate con "e/ma"; ≤ ~12 parole/frase in media |
| **A2** | passato prossimo, futuro semplice, riflessivi, dovere/potere/volere, imperativo (istruzioni) | quotidiano allargato (lavoro, viaggi, servizi); VdB dominante | coordinate + subordinate semplici (perché, quando, se) |
| **B1** | imperfetto vs passato prossimo, condizionale, pronomi combinati, stare+gerundio, congiuntivo presente ricorrente ma non dominante | cronaca corrente; ≤ ~5% fuori dal lessico comune | subordinate causali/temporali/relative; paragrafi strutturati |
| **B2** | congiuntivo (presente/passato/imperfetto), passivo, periodo ipotetico II, connettivi argomentativi | astratto + settoriale divulgativo; ≤ ~7% lessico non comune | argomentazione multi-paragrafo, incisi |
| **C1** | tutto il sistema verbale incl. passato remoto (narrativa), forme implicite (gerundio/participio), registro formale | ampio, idiomatico, tecnicismi e figure retoriche; fino a ~15% lessico non comune/colto | periodi complessi, subordinazione multipla, prosa saggistica/letteraria |

Reference: Linee guida CILS peg lexis to De Mauro's *Vocabolario di base* with a growing quota of "lessico comune" (≈5% B1, 7% B2, 15% C1) — see `factory/exams/cils/analysis/OVERVIEW.md`.

## 2. Anchor comparison

Compare the candidate against the transcribed example items/excerpts from the official dic-2024 papers in `factory/exams/cils/analysis/{A2,B1,B2,C1}.md` (§2 of each file) and, for A1, the genre descriptions in `analysis/A1.md`. Ask: *would this text sit naturally next to the anchor in the same fascicolo?* Consider topic register, sentence rhythm, and how much the reader must infer.

## 3. Quantitative sanity bands (guidance, not hard gates)

| Level | Avg words/sentence | "Hard-lexis" share (rough estimate of words outside everyday vocabulary) |
|---|---|---|
| A1 | ≤ 12 | ~0–2% |
| A2 | 10–15 | ~2–4% |
| B1 | 14–20 | ~4-6% |
| B2 | 18–25 | ~6–10% |
| C1 | 22–32 | ~10–18% |

Count on the cleaned text. A text may still pass outside a band if rubric + anchors agree (e.g. literary dialogue shortens sentences at C1) — say so explicitly in the verdict.

## 4. Decision procedure (write this into `sources.md` per candidate)

1. **Grade** the raw text with the rubric (cite 2–3 concrete features: e.g. «usa congiuntivo imperfetto "temesse", incisi lunghi → B2+»).
2. **Compare** to the level anchors (one sentence).
3. **Numbers:** words, avg sentence length, estimated hard-lexis share.
4. **Verdict:** `ACCEPT (target)`, `ACCEPT WITH ADAPTATION (from <level>, plan: <cuts/simplifications>)`, or `REJECT (<reason>)`.
   - Adaptation may bridge **at most one level** (e.g. B2 source trimmed to B1); never fake a level jump by rewriting every sentence — that destroys authenticity.
5. Texts that require outside/cultural knowledge to be understood → REJECT for objective-item slots.
