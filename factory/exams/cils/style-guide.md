# CILS style guide — wording & layout conventions for generated papers

Distilled from the dic-2024 official papers (`analysis/*.md`). Templates already embed most of this; this file is the reference for item-writers, auditors and future template authors.

## 1. Naming & headers

- Level names: "CILS A1", "CILS A2", "CILS UNO — B1", "CILS DUE — B2", "CILS TRE — C1".
- Section = **test**: "Test di comprensione della lettura", "Test di analisi delle strutture di comunicazione", "Test di produzione scritta", "Test di produzione orale". Section header line carries: "Tempo a disposizione: **NN minuti**" + "Numero delle prove **N**" + total points (orale has no tempo a disposizione: durations are per prova, printed in the consegna).
- Prova running head: `<Sezione> — Prova n. N` (e.g. "Comprensione della lettura — Prova n. 2").
- Cover block: "Certificazione di Italiano come Lingua Straniera" / "Quaderno di esame" / "Livello: X" / month-year. Our papers add "Prova di esercitazione" + the non-affiliation notice.

## 2. Consegne (immutable formulas)

Always bold-italic in the real papers; in markdown they live in blockquotes. Canonical formulas:

- Reading a text: «Leggi il testo.» / plural «Leggi i testi.»
- MC comprehension: «Completa le seguenti frasi. Scegli una delle quattro proposte di completamento che ti diamo per ogni frase. DEVI SCRIVERE LE RISPOSTE NEL "FOGLIO DELLE RISPOSTE".» (3-option variant: «…una delle tre proposte…»)
- Individuazione (V/F): «Leggi le seguenti informazioni. Indica se le informazioni sono vere o false. DEVI SCRIVERE LE RISPOSTE NEL "FOGLIO DELLE RISPOSTE".»
- Ricostruzione: «Leggi il testo. Il testo è diviso in N parti. Le parti non sono in ordine. Ricostruisci il testo. Scrivi il numero d'ordine accanto a ciascuna parte. DEVI SCRIVERE…»
- Abbinamento: «Leggi i testi. Scegli tra i testi da A a H i sei che completano i testi da 1 a 6. DEVI SCRIVERE…» (adapt letter range/counts to the prova)
- Cloze articoli/preposizioni: «Completa il testo con gli articoli e le preposizioni semplici e articolate: utilizza le preposizioni fra parentesi. DEVI SCRIVERE…» (A1 variant: «Completa il testo con gli articoli determinativi.»)
- Cloze verbi: «Completa il testo con le forme dei verbi che sono tra parentesi. DEVI SCRIVERE…»
- Cloze lessicale MC: «Completa il testo. Scegli una delle proposte di completamento. DEVI SCRIVERE…»
- Situazioni comunicative: «Scegli per ogni espressione una delle quattro situazioni di comunicazione. DEVI SCRIVERE…»
- Writing word count: «Devi scrivere da X a Y parole.» — always its own line.
- Oral durations (from the official quaderni): «Durata della conversazione: 2-3 minuti circa.» / «Durata dell'esposizione: 1 minuto e mezzo circa.» — italic, own line after the consegna. Argomenti in bold numbered list, one per line; C1 role-play situations are short bold-numbered paragraphs.
- Points statement: when present in official materials, keep it on criteria/scoring pages, not inside B2/C1 prova bodies. The official 2024 B2/C1 quaderni do not print per-prova scoring lines in the student item pages.

## 3. Items & examples

- Item numbering restarts at 1 within each prova; the worked example is item/gap **(0)** and appears wherever the real paper has one: all cloze prove, MC-cloze (options row 0 with the key struck through), A2-style word banks (bank letter struck through).
- MC options: `A) … B) … C) … D)` each ending with a period; stems bold; distractors text-anchored.
- V/F items: statement + `Vero ○ Falso ○`.
- Cloze gaps: `__(n)__`; helper word in italics immediately before the gap: `*(di)* __(n)__`, `*(raccontare)* __(n)__`. Worked example shows the answer inside: `__al (0)__`.
- Ricostruzione: parts lettered A, B, C…; part A pre-numbered 1 (C1: two anchors, A=1 and one more given); parts begin with connectives/anaphora that make the order unique.
- Micro-message prove (B1/B2 strutture n.4): stimulus in bold, 25–50 words, realistic register (segreteria telefonica, SMS, avviso, e-mail); options all start with «È …».

## 4. Texts

- Boxed in the original, centred ALL-CAPS title. In markdown: `### TITLE` above the text.
- Interviews: interviewer questions bold, answers plain.
- **Source attribution:** student `paper.md` must not print source attribution lines. The dic-2024 papers do not show `Testo adattato da` in the quaderno; this factory keeps source credit and adaptation metadata in `manifest.yaml` and audit files instead.
- Text-selection rules (linee guida § 1.4.3.2): no culture-bound trivia required for comprehension; no religious/moral/political content; lexis within level (De Mauro VdB + level's lessico comune quota); anything outside must be inferable from context.

## 5. Answer sheet & writing space (our practical adaptations)

- Real exams use optical sheets + barcoded writing sheets. Practice papers include an **"ESEMPIO DI FOGLIO DELLE RISPOSTE"** near the cover; any simplified answer grid is a practice artifact, not a source of solutions.
- Real B1+ papers put writing prompts on separate sheets; when the generator prints them in-paper for practice, it must still keep keys, criteria, model answers and study aids in `answers.md`.
- STAMPATELLO note is kept for open-cloze grids (authentic flavour, useful habit).

## 6. Answers file (`answers.md`)

- Chiavi as tables with qualified IDs (`L1.1`, `S2.7`, `W1`); spiegazioni quote the decisive words of the text; add a one-line 中文 note where the trap is subtle.
- Writing: print the official criteri (from `exam.yaml`), then one 范文 per task **inside the word range**, then 3–5 «Espressioni utili» with 中文 glosses.
- Oral («Produzione orale — criteri e testi modello»): print the criteri, then a complete memorizable model for **every** argomento/domanda — dialogues as `Esaminatore:`/`Candidato:` (C1: `Interlocutore:`) turns, monologues within the spoken-length range noted in the template comment — plus 3–5 «Espressioni utili» per prova. The student paper prints only argomenti/domande and durations; all models stay in `answers.md`.
- Close with **Glossario da ricordare**: 15–25 entries from the paper's own texts (Parola/Espressione | Categoria | 中文 | EN | Esempio dal testo).

## 7. Language policy

`paper.md` is 100% Italian (as the real exam). `answers.md` is Italian with targeted 中文 notes/glosses (study aid). English only in the EN column of the glossary.
