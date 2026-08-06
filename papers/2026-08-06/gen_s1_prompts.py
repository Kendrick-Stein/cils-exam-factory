#!/usr/bin/env python3
"""Generate S1 corpus-hunter dispatch prompts for one session (see factory/PIPELINE.md S1)."""
import pathlib

import yaml

SESSION = "2026-08-06"
CD = "/Users/kendrickstein/Code/CILS_Exam_AUTOGEN"
LEVELS = ["A1", "A2", "B1", "B2", "C1"]

SECTION_LABEL = {
    "lettura": "Comprensione della lettura",
    "strutture": "Analisi delle strutture di comunicazione",
}

# Orchestrator-owned pool reservation: no pool text may be claimed by two levels
# (cross-level reuse fails the quality audit). Ids are pool/<id>.md stems.
RESERVED = {
    "A1": ["666104fb9b77", "b7d2dc67ddc7"],
    "A2": ["2860d804492c", "cbc77544c0ed", "1f137c569ad9", "6dcce3592e26"],
    "B1": ["e26148efca5a", "479a5da5aa25", "7aa7c4fc9ad1"],
    "B2": ["6c788fbbdfe1", "3f9a5f277d3f", "2f49db8aa8b8"],
    "C1": ["748f28fe9dec", "92aa26100bbb", "79c9b123238e"],
}

HEAD = """You are the **corpus-hunter** for the CILS Exam Factory. First run `cd {cd}`. You have shell + network; you do NOT have WebFetch/WebSearch tools — fetch with `curl` and search with `curl` against a search engine or by going straight to the whitelisted sections in `factory/corpus/sources.yaml`.

## ROLE

You hunt **authentic Italian texts** for one exam level's text slots. You never invent text, never translate, never write from memory.

Read first: `factory/corpus/sources.yaml` (whitelist + rules), `factory/corpus/cefr-criteria.md` (grading), `factory/corpus/used-sources.txt` (the cross-date de-dup blacklist).

## Method, per slot
1. Pick sources from the whitelist matching the slot's genre (`levels:` section). Prefer texts published in the last 12 months for news/blog genres.
2. Fetch up to 2 candidates from different publishers. Paywall/cookie-wall stub → drop it. **Drop any candidate whose URL already appears in `factory/corpus/used-sources.txt`** (check with `grep -F "<url>" factory/corpus/used-sources.txt`). While fetching, **over-fetch**: grab 1–2 extra candidates from neighbouring levels/genres — you will grade and bank them even if this paper does not use them.
3. **Clean:** keep title + body prose; drop navigation, ads, captions, correlati, author bios, share buttons. Fix broken hyphenation. Keep paragraph breaks.
4. **Grade** per `cefr-criteria.md` §4: rubric evidence (2–3 concrete features), anchor comparison, numbers (words, avg sentence length, hard-lexis estimate), verdict `ACCEPT / ACCEPT WITH ADAPTATION (plan) / REJECT (reason)`. Adaptation bridges at most one CEFR level. Assign a primary CEFR plus `usable_levels` (primary ±1).
5. Record metadata: url, title, publisher, published date (if visible), accessed date (today).
6. **Bank every graded candidate** you fetched (used or not):
   `python3 scripts/pool_add.py --url <url> --title <t> --publisher <p> --published <YYYY-MM-DD> --fetched {session} --genre <genre> --cefr <primary> --usable-levels <L1,L2> --words <n> --fetch-intent {lv}/<slot> --text-file <cleaned.txt>`
   Write the cleaned text ALONE to the temp file — never your grading notes. Already-consumed/pooled URLs are skipped automatically.

## Fetch pitfalls (verified)
- Fetch with a browser User-Agent: `curl -sS -L -m 30 -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36' '<url>'`. On 403 / empty / JS-wall, retry the SAME url through `https://r.jina.ai/<url>`.
- Frequently bot-blocked (r.jina.ai usually works): focus.it, fanpage.it, today.it, gamberorosso.it, subito.it, focusjunior.it.
- Dead, do not try: `wired.it`, `italianofacile.news`.
- ANSA quirk: difficulty-highlight `<span>`s can split tokens (`teoria`→`te oria`); strip stray markup.
- Anonymize personal phone numbers/emails in realia — replace digits with `3XX XXXXXXX`.
- Off-whitelist sources are allowed with a one-line justification (e.g. a comune page for a local event) and must still be authentic and free to access.

## THIS TASK

- **LEVEL:** {lv}   **SESSION:** {session}   **today = {session}**
- **OUTPUT FILE (write it yourself):** `{cd}/papers/{session}/{lv}/sources.md`
- **Blacklist (hard):** `factory/corpus/used-sources.txt` — {nblack} URLs already consumed by earlier papers. Never accept a URL on that list.

### Slots for this level

| slot | genere | parole | feeds |
|---|---|---|---|
{slottable}

### Reserved pool texts — USE THESE, DO NOT FETCH FOR THEM

{reserved}

Read each reserved file (front-matter + body) and place it in whichever slot above its genre and length fit best; record in `sources.md` that it comes from the pool (`origin: pool/<id>.md`) with its recorded url/title/publisher/published/fetched metadata. If a reserved text is longer than its slot band, say so and give a trim plan (adaptation is allowed and logged); if it is much shorter than every remaining band, use it as ONE of the micro-testi in the abbinamento slot, or drop it and fetch live instead (say which). **Do not use any pool text that is not in the reserved list above — the other levels have reserved them and a duplicate would fail the cross-level gate.**

### Live fetches — every slot the reserved texts do not cover

Requirements: real, currently-published, free-to-access Italian web text; **verbatim Italian**, cleaned; land inside (or trimmable into) the slot's word band; different publishers across slots where possible.

### sources.md format (exactly this)

```markdown
# Sources — {lv} {session}

## Slot T1 — <genere>, target <min–max> parole, feeds <prova>
### Candidate 1 — ACCEPT
- url: <...>
- title: <...>
- publisher: <...>
- published: <YYYY-MM-DD or unknown>
- accessed: {session}
- origin: pool/<id>.md   (omit this line for live fetches)
- CEFR: <ACCEPT | ACCEPT WITH ADAPTATION> — <2–3 evidence bullets> — parole: <n>, frase media: <n>, lessico difficile: <n>%
- Adaptation plan: <cuts/simplifications, or "none">

<cleaned full text, verbatim Italian, paragraph breaks kept>
```

End the file with:

```
## Coverage
Slot T1: OK (candidate 1)
...
```

### Final reply to the orchestrator

Reply with ONLY:
1. the Coverage block,
2. one line per slot: `<slot> <words> <url>`,
3. a line `BANKED: <n> texts` listing the pool ids added.
Do not paste the texts into your reply.
"""


def main():
    exam = yaml.safe_load(open(f"{CD}/factory/exams/cils/exam.yaml"))
    pool = {s["source_file"].split("/")[-1][:-3]: s
            for s in yaml.safe_load(open(f"{CD}/factory/corpus/pool-index.yaml"))["sources"]}
    nblack = len([l for l in open(f"{CD}/factory/corpus/used-sources.txt") if l.strip()
                  and not l.startswith("#")])
    outdir = pathlib.Path(f"{CD}/papers/{SESSION}/s1-prompts")
    outdir.mkdir(parents=True, exist_ok=True)

    seen = set()
    for lv in LEVELS:
        rows = []
        for sec in exam["levels"][lv]["sections"]:
            label = SECTION_LABEL.get(sec["id"])
            if not label:
                continue
            for p in sec.get("prove", []):
                t = p.get("testo") or {}
                if not t.get("slot"):
                    continue
                lo, hi = t["parole"]
                rows.append(f"| {t['slot']} | {t['genere']} | {lo}–{hi} | {label}, "
                            f"Prova n. {p['n']} ({p['tipo']}, {p['items']} item) |")

        res = []
        for pid in RESERVED[lv]:
            assert pid not in seen, f"pool text {pid} reserved twice"
            seen.add(pid)
            s = pool[pid]
            res.append(f"- `factory/corpus/pool/{pid}.md` — CEFR {s['cefr']} "
                       f"(usable {','.join(s['usable_levels'])}), {s['words']} parole, "
                       f"genere `{s['genre']}` — \"{s['title']}\"")

        body = HEAD.format(cd=CD, lv=lv, session=SESSION, nblack=nblack,
                           slottable="\n".join(rows), reserved="\n".join(res))
        (outdir / f"{lv}.txt").write_text(body)
        print(f"{lv}: {len(rows)} slots, {len(res)} reserved pool texts, "
              f"{len(rows) - len(res)} live fetches")

    (outdir / "_index.txt").write_text("\n".join(f"{lv} medium" for lv in LEVELS) + "\n")


if __name__ == "__main__":
    main()
