#!/usr/bin/env python3
"""Generate S4 per-prova repair prompts from the blind-validation reports (PIPELINE.md S4).

Repair unit = one prova; executor = a FRESH item-writer that never saw the authoring
transcript. Usage: gen_s4_prompts.py [round-suffix]   e.g. `gen_s4_prompts.py -r2`.
"""
import collections
import json
import pathlib
import re
import sys

import yaml

SESSION = "2026-08-06"
CD = "/Users/kendrickstein/Code/CILS_Exam_AUTOGEN"
LEVELS = ["A1", "A2", "B1", "B2", "C1"]

RULES = {
    "cloze_verbi": "Cloze verbi: the printed text must force ONE tense/form per gap — hard past anchor up front («Domenica scorsa», «Nel 2019»); «ogni giorno / sempre / mentre + verbo» for imperfetto; «Adesso/Oggi» pivot for presente; «In questi anni / finora / fino a oggi» to force passato prossimo and block the remoto; passato remoto only with an unmistakable cue («Fu … che»). Auxiliary AND clitic go INSIDE the gap, and the printed sentence must make an obligatory clitic unmistakable (if the key is «mi permette», the surrounding text must rule out the clitic-less reading — otherwise re-cut the gap so the clitic is not optional). Never passato prossimo with essere when the subject's gender is unspecified.",
    "cloze_aperto": "Cloze aperto: no free-variant gaps — the article/preposition/pronoun must be grammatically OBLIGATORY (agreement forced by a visible antecedent). No bare-vs-articulated ambiguity, no «di cui»/«del quale» competition, no è/viene passive competition, no gap a content word could fill instead of a function word.",
    "cloze_aperto:connettivi": "Cloze connettivi: each gap takes exactly ONE connettivo that the logical relation makes obligatory; no interchangeable pairs («ma»/«però»), and the gap must not admit a verb or noun instead of a connective.",
    "cloze_mc_3": "Cloze a scelta multipla: exactly one option fits each gap; distractors wrong for a clear lexical/grammatical reason.",
    "cloze_mc_4": "Cloze a scelta multipla: exactly one option fits each gap; distractors wrong for a clear lexical/grammatical reason.",
    "scelta_multipla_3": "Scelta multipla: exactly one option defensible from the printed text alone; distractors plausible but text-refuted.",
    "scelta_multipla_4": "Scelta multipla: exactly one option defensible from the printed text alone; distractors plausible but text-refuted.",
    "vero_falso": "Vero/Falso: each statement unambiguously V or F from the text alone — no «non detto» traps.",
    "abbinamento": "Abbinamento: each micro-text matches exactly one option on a decisive printed detail; check every text against every option, including the unused ones.",
    "ricostruzione": "Ricostruzione: every non-anchor part must OPEN with a unique connettivo/anafora/time cue; verify each movable part fits in exactly one position and nowhere else; the key is the full sequence string.",
    "situazioni_mc_4": "Situazioni: each micro-messaggio has exactly ONE pragmatically correct function; distractors plausible but wrong.",
    "trasformazione_frasi": "Trasformazioni: the printed starter must FORCE the target structure and pin subject + pivot, leaving a completion of 8–20 words; the key must list every meaning-preserving rewrite (completion-only AND full-sentence forms) separated by `||`.",
}

HEAD = """You are an item-writer for the CILS Exam Factory (repo at {cd}) running a **stage S4 repair**. You are a FRESH agent: you did not write this prova.

Read first:
1. `.claude/agents/item-writer.md` — your full role, especially "Stage S4 — repair" and the hard rules.
2. `factory/exams/cils/templates/{lv}.md` — the HTML comments next to your {{{{SLOT}}}} placeholders (formats, counts, examples).
3. Your current fragment: `papers/{session}/{lv}/fragments/{fid}.json`.

{source}
Assignment: level {lv}, session {session}, fragment ID **{fid}**.

Prova spec from exam.yaml:
{spec}

## Blind-validation defects to fix

An independent solver received ONLY the printed student paper (no key, no source, no web) and reported these problems:

{defects}

## What to do

- For EACH defect decide whether the KEY is wrong or the ITEM is ambiguous. Ambiguity is the usual cause: fix the item so that exactly ONE answer is defensible from the printed text alone — re-cut the gap, add the printed time marker / disambiguating cue the rule requires, change what the item tests, or replace the item outright. A flagged item fails the gate even when the solver's answer matched your key, so a flag must be designed away, not argued away.
- Then **rescan every other item in this prova for the same defect class** and fix those too, even if the solver did not catch them. A second failure on this prova would drop the level to `draft`.
- Keep item COUNT, point values, consegna and slot names identical. Do not renumber.
- {rule}
- Keep the text inside its exam.yaml word band (measured on the *_TEXT / *_WITH_GAPS body, title and items excluded).

## Output

Rewrite EXACTLY ONE file, `papers/{session}/{lv}/fragments/{fid}.json`, same JSON shape (`prova`, `slots`, `answer_slots`, `key`, `glossario_candidates`), with all the slot keys it already has. Update the chiavi rows and spiegazioni to match your fixes. Do NOT touch manifest.yaml, paper.md, answers.md or any other file.

Reply (short, no fragment content): one line per defect saying what you changed, plus any other items you preemptively fixed.
"""

SOURCE = ("Your ONE source text: the '## Slot {slot}' section of papers/{session}/{lv}/sources.md "
          "— read ONLY that section.\n")


def main():
    suffix = sys.argv[1] if len(sys.argv) > 1 else ""
    exam = yaml.safe_load(open(f"{CD}/factory/exams/cils/exam.yaml"))
    outdir = pathlib.Path(f"{CD}/papers/{SESSION}/s4-prompts")
    outdir.mkdir(parents=True, exist_ok=True)
    index = []

    for lv in LEVELS:
        report = pathlib.Path(f"{CD}/papers/{SESSION}/{lv}/blind-validation.json")
        if not report.exists():
            continue
        rep = json.loads(report.read_text())
        defects = collections.defaultdict(list)
        for m in rep.get("mismatches", []):
            prova = m["item_id"].split(".")[0]
            key = m["expected"] if len(m["expected"]) < 120 else m["expected"][:117] + "…"
            defects[prova].append(
                f"- **{m['item_id']}** — la tua chiave: `{key}` | risposta del solutore cieco: "
                f"`{m['actual']}` → leggendo SOLO il testo stampato il solutore ha scelto "
                f"un'altra risposta difendibile.")
        for f in rep.get("flags", []):
            prova = f["item_id"].split(".")[0]
            defects[prova].append(
                f"- **{f['item_id']}** — AMBIGUITY FLAG dal solutore: «{f['reason']}» → "
                f"l'item va reso univoco (un flag fa fallire il gate anche se la risposta coincide).")

        specs = {}
        for sec in exam["levels"][lv]["sections"]:
            pre = {"lettura": "L", "strutture": "S"}.get(sec["id"])
            if not pre:
                continue
            for p in sec.get("prove", []):
                specs[f"{pre}{p['n']}"] = p

        for fid, items in sorted(defects.items()):
            p = specs.get(fid)
            if p is None:
                print(f"!! {lv} {fid}: no spec (defect outside a lettura/strutture prova)")
                continue
            tipo = p["tipo"]
            if tipo == "cloze_aperto" and "connettiv" in str(p.get("focus", "")).lower():
                tipo = "cloze_aperto:connettivi"
            slot = (p.get("testo") or {}).get("slot")
            src = SOURCE.format(slot=slot, session=SESSION, lv=lv) if slot else \
                "This prova has NO source text — its content is composed.\n"
            body = HEAD.format(
                cd=CD, lv=lv, session=SESSION, fid=fid, source=src,
                spec=yaml.safe_dump(p, allow_unicode=True, sort_keys=False).rstrip(),
                defects="\n".join(items), rule=RULES.get(tipo, ""))
            (outdir / f"{lv}-{fid}{suffix}.txt").write_text(body)
            effort = "high" if (lv in ("B2", "C1") or suffix) else "medium"
            index.append(f"{lv} {fid}{suffix} {effort}")
            print(f"{lv} {fid}: {len(items)} defect(s) -> {effort}")

    (outdir / "_index.txt").write_text("\n".join(index) + "\n")
    print(f"\n{len(index)} repair prompts")


if __name__ == "__main__":
    main()
