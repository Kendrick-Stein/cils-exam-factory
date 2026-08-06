#!/usr/bin/env python3
"""Generate S2 per-prova dispatch prompts for one session (see factory/PIPELINE.md S2)."""
import pathlib
import sys

import yaml

SESSION = "2026-08-06"
PREV = ["2026-08-02", "2026-07-30"]
CD = "/Users/kendrickstein/Code/CILS_Exam_AUTOGEN"
LEVELS = ["A1", "A2", "B1", "B2", "C1"]

SECTION_NAME = {
    "lettura": "Test di comprensione della lettura",
    "strutture": "Test di analisi delle strutture di comunicazione",
    "scritta": "Test di produzione scritta",
    "orale": "Test di produzione orale",
}

# fragment -> slots, taken verbatim from the last passing session's fragments
SLOTS = {
    "A1": {
        "L1": "L1_ITEMS, T1_TEXT, T1_TITLE, ANS_L1_ROWS",
        "L2": "L2_ITEMS, T2_TEXT, T2_TITLE, ANS_L2_ROWS",
        "L3": "L3_ITEMS, L3_OPTIONS, ANS_L3_ROWS, ANS_L3_UNUSED",
        "S1": "S1_TEXT_WITH_GAPS, T4_TITLE, ANS_S1_NOTES, ANS_S1_ROWS",
        "S2": "S2_TEXT_WITH_GAPS, T5_TITLE, ANS_S2_NOTES, ANS_S2_ROWS",
        "S3": "S3_TEXT_WITH_GAPS, T6_TITLE, S3_OPT0_A, S3_OPT0_B, S3_OPT0_C, S3_OPTION_ROWS, ANS_S3_ROWS",
        "W": "W1_PROMPT, W2_PROMPT, MODEL_W1, MODEL_W1_PHRASES, MODEL_W2, MODEL_W2_PHRASES",
        "O": "O1_DOMANDE, O2_ARGOMENTI, MODEL_O1, MODEL_O1_PHRASES, MODEL_O2, MODEL_O2_PHRASES",
    },
    "B1": {
        "L1": "L1_ITEMS, T1_TEXT, T1_TITLE, ANS_L1_ROWS",
        "L2": "L2_ITEMS, T2_TEXT, T2_TITLE, ANS_L2_ROWS",
        "L3": ("T3_TITLE, T3_PART_A, T3_PART_B, T3_PART_C, T3_PART_D, T3_PART_E, T3_PART_F, "
               "T3_PART_G, T3_PART_H, T3_PART_I, T3_PART_J, T3_PART_K, ANS_L3_ROWS, ANS_L3_SEQUENCE"),
        "S1": "S1_TEXT_WITH_GAPS, T4_TITLE, ANS_S1_NOTES, ANS_S1_ROWS",
        "S2": "S2_TEXT_WITH_GAPS, T5_TITLE, ANS_S2_NOTES, ANS_S2_ROWS",
        "S3": ("S3_TEXT_WITH_GAPS, T6_TITLE, S3_OPT0_A, S3_OPT0_B, S3_OPT0_C, S3_OPT0_D, "
               "S3_OPTION_ROWS, ANS_S3_ROWS"),
        "S4": "S4_ITEMS, ANS_S4_ROWS",
        "W": ("W1_PROMPT, W2_PROMPT, W2_REQ_1, W2_REQ_2, W2_REQ_3, MODEL_W1, MODEL_W1_PHRASES, "
              "MODEL_W2, MODEL_W2_PHRASES"),
        "O": "O1_ARGOMENTI, O2_ARGOMENTI, MODEL_O1, MODEL_O1_PHRASES, MODEL_O2, MODEL_O2_PHRASES",
    },
    "C1": {
        "L1": "L1_ITEMS, T1_TEXT, T1_TITLE, ANS_L1_ROWS",
        "L2": "L2_ITEMS, T2_TEXT, T2_TITLE, ANS_L2_ROWS",
        "L3": ("T3_TITLE, T3_PART_A, T3_PART_B, T3_PART_C, T3_PART_D, T3_PART_E, T3_PART_F, "
               "T3_PART_G, T3_PART_H, T3_PART_I, T3_PART_J, T3_PART_K, T3_PART_L, T3_PART_M, "
               "T3_PART_N, T3_PART_O, T3_PART_P, ANS_L3_ROWS, ANS_L3_SEQUENCE"),
        "S1": "S1_TEXT_WITH_GAPS, T4_TITLE, ANS_S1_NOTES, ANS_S1_ROWS",
        "S2": "S2_TEXT_WITH_GAPS, T5_TITLE, ANS_S2_NOTES, ANS_S2_ROWS",
        "S3": ("S3_TEXT_WITH_GAPS, T6_TITLE, S3_OPT0_A, S3_OPT0_B, S3_OPT0_C, S3_OPT0_D, "
               "S3_OPTION_ROWS, ANS_S3_ROWS"),
        "S4": "T7_TITLE, T7_TEXT, S4_ITEMS, S4_SOURCE_0, S4_REWRITE_0, ANS_S4_ROWS, ANS_S4_NOTES",
        "W": ("W1A_PROMPT, W1B_PROMPT, W2A_PROMPT, W2B_PROMPT, MODEL_W1A, MODEL_W1A_PHRASES, "
              "MODEL_W1B, MODEL_W1B_PHRASES, MODEL_W2A, MODEL_W2A_PHRASES, MODEL_W2B, MODEL_W2B_PHRASES"),
        "O": "O1_ARGOMENTI, O2_ARGOMENTI, MODEL_O1, MODEL_O1_PHRASES, MODEL_O2, MODEL_O2_PHRASES",
    },
}
SLOTS["A2"] = SLOTS["A1"]
SLOTS["B2"] = SLOTS["B1"]

REMINDER = {
    "scelta_multipla_3": "Each stem tests comprehension derivable from THIS text alone; exactly one correct option; distractors plausible but text-refuted.",
    "scelta_multipla_4": "Each stem tests comprehension derivable from THIS text alone; exactly one correct option; distractors plausible but text-refuted.",
    "vero_falso": "Vero/Falso: each statement is unambiguously V or F from the text alone — no 'non detto' traps; balance V and F.",
    "abbinamento": "Abbinamento: each micro-text matches exactly one option; there are MORE options than items (the extras stay unused — list them in ANS_L3_UNUSED). Each match uniquely derivable.",
    "cloze_aperto": "Cloze aperto: NO free-variant gaps. Make each article/preposition OBLIGATORY; avoid è/viene passive competition, di cui/del quale competition, bare-vs-articulated ambiguity, open quantifiers. One and only one correct token per gap.",
    "cloze_aperto:connettivi": "Cloze CONNETTIVI: each gap takes exactly one connettivo/segnale discorsivo that the logical relation makes obligatory; no interchangeable connective pairs (e.g. avoid gaps where 'ma' and 'però' both fit).",
    "cloze_verbi": "Cloze VERBI — force ONE form per gap with explicit printed time markers: hard past anchor up front («Domenica scorsa», «Nel 2019»); «ogni giorno / sempre / mentre + verbo» for imperfetto; explicit «Adesso/Oggi» for present; «In questi anni / finora / fino a oggi» to force passato prossimo (blocks passato remoto); passato remoto only with an unmistakable cue («Fu … che»). Auxiliary AND clitic go INSIDE the gap. No essere-aux passato prossimo with an unspecified-gender subject.",
    "cloze_mc_3": "Cloze a scelta multipla (3 opzioni): exactly one option fits each gap; example gap 0 is pre-filled (S3_OPT0_*). Distractors wrong for a clear lexical/grammatical reason.",
    "cloze_mc_4": "Cloze a scelta multipla (4 opzioni): exactly one option fits each gap; example gap 0 pre-filled (S3_OPT0_*). Distractors wrong for a clear reason.",
    "situazioni_mc_4": "Situazioni (10 micro-messaggi realistici, 4 opzioni): each item has exactly ONE pragmatically correct communicative function; distractors plausible but wrong. Compose the micro-messaggi on the model of authentic realia (no source text).",
    "trasformazione_frasi": "Trasformazioni (6): derive each from the T7 source. The printed STARTER must FORCE the target structure (e.g. «QUALORA» → congiuntivo; nominalisation; discorso indiretto) and pin subject + pivot, leaving a completion of 8–20 words. key lists ALL correct rewrites with `||` (both completion-only and full-sentence forms) — meaning-preserving lexical variants are CORRECT answers, not defects. S4_SOURCE_0/S4_REWRITE_0 are the worked example (item 0).",
}
REMINDER_W = {
    "A1": "Two prompts (tema + testo funzionale). Provide one 范文 per task INSIDE the printed word range + 3-5 espressioni utili each. No key entries.",
    "B1": "Two prompts: W1 tema; W2 testo funzionale with 3 explicit content requests (W2_REQ_1..3). One 范文 per task INSIDE the printed word range + 3-5 espressioni utili each. No key entries.",
    "C1": "Saggio breve (scelta fra 2: W1A/W1B) + lettera/e-mail formale (scelta fra 2: W2A/W2B). Provide a 范文 for EACH of the four tracce INSIDE the printed word range + 3-5 espressioni utili each. No key entries.",
}
REMINDER_W["A2"] = REMINDER_W["A1"]
REMINDER_W["B2"] = REMINDER_W["B1"]
REMINDER_O = "Produzione orale: compose text-only argomenti/domande (NEVER image tracce). Provide a COMPLETE memorizable model for EVERY argomento/domanda (dialoghi as Esaminatore:/Candidato: turns; monologhi within the spoken-length range in the template comment) + 3-5 espressioni utili per prova. key stays EMPTY."

EFFORT = {
    ("B2", "L3"): "high", ("B2", "S2"): "high",
    ("C1", "L1"): "high", ("C1", "L3"): "high", ("C1", "S1"): "high",
    ("C1", "S2"): "high", ("C1", "S4"): "high",
}

HEAD = """You are an item-writer for the CILS Exam Factory (work in the current repo checkout at {cd}).

Read first, in this order:
1. .claude/agents/item-writer.md — your full role; every rule is binding.
2. factory/exams/cils/style-guide.md and factory/validation/checklist.md §A.
3. factory/exams/cils/templates/{lv}.md — find your {{{{SLOT}}}} placeholders and follow the HTML comments next to them EXACTLY (item counts, formats, examples (0), length guidance).

Assignment: level {lv}, session {session}, fragment ID {fid} ({secname}).

Prova spec from exam.yaml:
{spec}
"""

TAIL = """
Item-writer reminder for this prova: {reminder}
{variety}
Output: write EXACTLY ONE file, papers/{session}/{lv}/fragments/{fid}.json — a JSON object
{{"prova": "{fid}", "slots": {{...}}, "answer_slots": {{...}}, "key": {{...}}, "glossario_candidates": [...]}}.
- Fill EXACTLY these slots (paper + answers): {slots}
- Slot values are the exact markdown the template expects at that position. 100% Italian in paper-facing slots; spiegazioni/notes may carry short 中文 glosses; never add point statements, source attributions or extra headings inside slot content.
- key uses qualified IDs ({fid}.<n>) and session conventions: "V || Vero" style alternatives with ||; ricostruzione/abbinamento keys per the template comments; list every genuinely correct variant with ||.
- Up to 5 glossario_candidates drawn VERBATIM from your text (parola, categoria, zh, en, esempio){glossnote}.
- Do NOT touch manifest.yaml or any other file.

Reply (short, no fragment content): item count, final text word count, words_used from your source, anything adapted heavily.
"""

VARIETY = """
Variety requirement (this session must not clone the previous one): before composing,
read the same fragment from the two most recent sessions —
`papers/{p0}/{lv}/fragments/{fid}.json` and `papers/{p1}/{lv}/fragments/{fid}.json`
(use whichever exist) — and deliberately choose DIFFERENT temi/argomenti/situazioni from
those. Same format and difficulty, new content.
"""

SOURCE_BLOCK = """
Your ONE source text: the '## Slot {slot}' section of papers/{session}/{lv}/sources.md — read ONLY that section (do not use other slots' texts). Follow its adaptation plan; adapt INTO the band; cut whole sentences first; never invent facts.

The reading text body you deliver in the *_TEXT / *_WITH_GAPS slot (title and items excluded) is word-counted by the quality audit against the band in the spec — land inside it, aim mid-band.
"""

NO_SOURCE_BLOCK = """
This fragment has NO source text — compose its content per the template HTML comments and the spec below.
"""

GLOSSARIO_PROMPT = """You are an item-writer for the CILS Exam Factory (repo at {cd}).

Read first:
1. .claude/agents/item-writer.md — your role (GLOSSARIO section).
2. factory/exams/cils/templates/{lv}.md — find {{{{GLOSSARIO_ROWS}}}} and the header just above it. The table columns are: | Parola/Espressione | Categoria | 中文 | EN | Esempio dal testo |. Your GLOSSARIO_ROWS value is ONLY the data rows (one per line, `| ... | ... | ... | ... | ... |`), no header, no separator line.
3. factory/exams/cils/style-guide.md.

Assignment: level {lv}, session {session}, fragment ID GLOSSARIO.

Read the `glossario_candidates` arrays from EVERY other fragment JSON in papers/{session}/{lv}/fragments/ (all files except GLOSSARIO.json). Pool them, then SELECT 15–25 of the most useful, level-appropriate, DISTINCT entries (dedupe near-duplicates; spread across the different source texts; prefer content words/expressions a learner at this level should acquire). Keep each entry's parola/categoria/中文/EN/esempio verbatim from the candidate (esempio = the short citation from its text).

Output: write EXACTLY ONE file, papers/{session}/{lv}/fragments/GLOSSARIO.json:
{{"prova": "GLOSSARIO", "slots": {{"GLOSSARIO_ROWS": "| parola | categoria | 中文 | EN | esempio |\\n| ... |"}}, "answer_slots": {{}}, "key": {{}}, "glossario_candidates": []}}

Reply (short): number of rows selected.
"""


def main():
    exam = yaml.safe_load(open(f"{CD}/factory/exams/cils/exam.yaml"))
    outdir = pathlib.Path(f"{CD}/papers/{SESSION}/s2-prompts")
    outdir.mkdir(parents=True, exist_ok=True)
    index = []

    for lv in LEVELS:
        cfg = exam["levels"][lv]
        for sec in cfg["sections"]:
            for p in sec.get("prove", []):
                if sec["id"] == "lettura":
                    fid = f"L{p['n']}"
                elif sec["id"] == "strutture":
                    fid = f"S{p['n']}"
                else:
                    continue
                slot = (p.get("testo") or {}).get("slot")
                key = p["tipo"]
                if key == "cloze_aperto" and "connettiv" in str(p.get("focus", "")).lower():
                    key = "cloze_aperto:connettivi"
                reminder = REMINDER.get(key, "")
                if p["tipo"] == "ricostruzione":
                    reminder = (f"Ricostruzione ({p['parti']} parti, {p['ancore']} ancora/e fissa/e): "
                                "every non-anchor part must OPEN with a unique connettivo/anafora/time cue so "
                                "EXACTLY ONE order is coherent. Verify each movable part cannot sit anywhere "
                                "else. Key = the full sequence string.")
                body = HEAD.format(cd=CD, lv=lv, session=SESSION, fid=fid,
                                   secname=SECTION_NAME[sec["id"]],
                                   spec=yaml.safe_dump(p, allow_unicode=True, sort_keys=False).rstrip())
                if slot:
                    body += SOURCE_BLOCK.format(slot=slot, session=SESSION, lv=lv)
                    variety = ""
                else:
                    body += NO_SOURCE_BLOCK
                    variety = VARIETY.format(p0=PREV[0], p1=PREV[1], lv=lv, fid=fid)
                body += TAIL.format(reminder=reminder, variety=variety, session=SESSION, lv=lv,
                                    fid=fid, slots=SLOTS[lv][fid], glossnote="")
                (outdir / f"{lv}-{fid}.txt").write_text(body)
                index.append(f"{lv} {fid} {EFFORT.get((lv, fid), 'medium')}")

        for fid, secid in (("W", "scritta"), ("O", "orale")):
            sec = next(s for s in cfg["sections"] if s["id"] == secid)
            reminder = REMINDER_W[lv] if fid == "W" else REMINDER_O
            body = HEAD.format(cd=CD, lv=lv, session=SESSION, fid=fid,
                               secname=SECTION_NAME[secid],
                               spec=yaml.safe_dump(sec, allow_unicode=True, sort_keys=False).rstrip())
            body += NO_SOURCE_BLOCK
            body += TAIL.format(reminder=reminder,
                                variety=VARIETY.format(p0=PREV[0], p1=PREV[1], lv=lv, fid=fid),
                                session=SESSION, lv=lv, fid=fid, slots=SLOTS[lv][fid],
                                glossnote=" — omit for W/O (no source)")
            (outdir / f"{lv}-{fid}.txt").write_text(body)
            index.append(f"{lv} {fid} medium")

        (outdir / f"{lv}-GLOSSARIO.txt").write_text(
            GLOSSARIO_PROMPT.format(cd=CD, lv=lv, session=SESSION))

    index += [f"{lv} GLOSSARIO low" for lv in LEVELS]
    (outdir / "_index.txt").write_text("\n".join(index) + "\n")
    print(f"wrote {len(index)} prompts to {outdir}")


if __name__ == "__main__":
    sys.exit(main())
