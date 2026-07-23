# Design — Pre-harvested, graded corpus pool

**Date:** 2026-07-23
**Status:** approved (design), pending implementation plan
**Depends on:** `scripts/build_used_index.py` + `factory/corpus/used-sources.txt` (shipped 2026-07-23)

## Problem

S1 hunts texts **just-in-time, per level**. A text fetched during an A1 hunt that
turns out to be B2-appropriate is thrown away — the fetch is wasted. Every
`/genpapers` run re-searches from scratch even when a perfectly good, already-fetched
text exists. There is no standing inventory of usable, graded texts to draw from.

## Goal

Decouple **fetching** from **level assignment**. Build a standing pool of cleaned,
CEFR-graded texts that `/genpapers` selects from at build time. Fetches are never
wasted: everything fetched is graded and routed to the level(s) it fits, then banked.
Live search becomes the fallback, not the default.

## Decisions (locked with user, 2026-07-23)

1. **Pool-first + live fallback.** genpapers selects from the pool first; a slot the
   pool can't fill falls back to live `corpus-hunter`. A thin pool never blocks production.
2. **Folded into genpapers — no new command.** Harvesting is a byproduct of generation:
   over-fetch broadly, grade everything, use what's needed, bank the leftovers.
3. **Store full cleaned text + grade** in the pool. Next build needs zero re-fetching.
4. **Per-genre perishable/evergreen freshness**, filtered at selection time.
5. **Commit the pool to git** (consistent with today's tracked `sources.md`; keeps provenance).
6. **Storage = file-per-text + generated index** (approach A) — matches the repo's
   plaintext, git-diffable, one-artifact-per-file ethos and reuses the `build_used_index.py`
   pattern.

## Architecture — two composable layers

| Layer | Answers | Authority | Artifact |
|---|---|---|---|
| used-index (shipped) | what's been **consumed** | regenerated from every manifest | `factory/corpus/used-index.yaml`, `used-sources.txt` |
| **pool (new)** | what's **collected but unused** | grows on over-fetch, pruned on demand | `factory/corpus/pool/<id>.md`, `pool-index.yaml` |

**Selection = pool entries matching {level, genre, length, fresh} MINUS `used-sources.txt`.**
Consumption is *derived* from manifests, never stored twice, so the two layers cannot drift.
A pooled text that later gets used stays physically in `pool/` but is filtered out of
future selections (and can be pruned).

## Components

### 1. Pool store — `factory/corpus/pool/<id>.md`
- `id = sha1(normalize_url(url))[:12]` — stable, dedups naturally, matches the
  `normalize_url` used by `build_used_index.py` and `paper_quality_audit.py`.
- One markdown file per text: YAML front-matter + cleaned body prose.

```markdown
---
url: https://www.ansa.it/...
title: ...
publisher: ANSA (canale Scienza)
published: '2026-07-13'      # source publish date if visible, else null
fetched: '2026-07-23'        # when it entered the pool
genre: culture_science       # a sources.yaml category
cefr: B2                      # primary graded level
usable_levels: [B1, B2]      # primary +/- 1 per "adaptation bridges one level"
words: 244
perishable: false            # genre default, overridable at grading
perishable_until: null       # set to the event date for dated realia (else null)
fetch_intent: A2/L3          # which level+slot triggered the fetch (provenance)
---

<cleaned full text>
```

### 2. `scripts/build_pool_index.py`
- Scans `factory/corpus/pool/*.md`, emits `factory/corpus/pool-index.yaml`
  (catalog: id -> all front-matter fields, no body).
- Prints a **coverage report**: pool depth per `level x genre`, and how many entries
  are already consumed (in `used-sources.txt`) or stale-perishable.
- Mirrors `build_used_index.py` structure (argparse defaults, `load_yaml`, `normalize_url`).

### 3. `scripts/pool_select.py`
- `--level B1 --genre cronaca --words 300-450 [--fresh-only] [--json]`
- Reads `pool-index.yaml` + `used-sources.txt`; returns ranked **available** candidates:
  - level in `usable_levels`, genre match, word count in band,
  - NOT in `used-sources.txt`, NOT stale-perishable.
- Rank by: freshness (newer first for perishable), then closeness of `words` to band centre.
- Prints file paths + one-line metadata so S1 can grab the body directly.

### 4. corpus-hunter changes (`.claude/agents/corpus-hunter.md` + `.codex/agents/corpus-hunter.toml`)
- **Step 0 — consult the pool first:** run/query `pool_select` for the slot; if a fresh,
  unused, well-graded candidate exists, use it and skip fetching.
- **On live fetch — over-fetch + bank:** fetch a few extra candidates around neighboring
  levels/genres (not just the target slot). Grade **all** of them (primary CEFR +
  `usable_levels`). Write **every graded text** as a `pool/<id>.md` file, whether or not
  it's used in the current paper. This is where the "A1 hunt found a B2 text" rescue happens.
- Output to `sources.md` is unchanged for the slot actually used; the pool banking is
  additive.

### 5. Freshness — per-text perishability, genre default + grader override
`practical_realia` is mixed (a dated event programme is highly perishable; a museum
`orari`/service page is near-evergreen), so perishability is a **per-text stamp**, not a
pure genre lookup:
- A `freshness:` map in `factory/corpus/sources.yaml` gives the **genre default window**
  (months): `news_general`/`news_easy` = 12; `practical_realia` = 6; evergreen
  (`literature_public_domain`, `culture_science`, `opinion_essay`, `blogs_lifestyle`) = none.
- At grading, the hunter stamps `perishable` (bool) + `perishable_until` (date, optional):
  the genre default applies, but **override to perishable with the event date** when the
  text is tied to a dated happening (sagra, mostra, event programme), regardless of genre.
- `pool_select` marks an entry stale when `perishable` and the effective date
  (`perishable_until`, else the window applied to the newer of `published`/`fetched`) has passed.

### 6. Whitelist backfill — `factory/corpus/sources.yaml`
Add the recurring, safe off-whitelist domains observed in real runs (107 distinct today):
- **`comuni italiani`** — generalize the existing "altri comuni" note to `comune.<città>.it`
  (torino, modena, parma, genova, roma, firenze, venezia, como, ravenna…): avvisi/servizi/comunicati.
- **biblioteche** — bibliotecasalaborsa.it, biblioteche.comune.verona.it (realia A2/B1).
- **musei/cultura** — museiincomuneroma.it, cultura.gov.it, italia.it, visittrentino.info.
- **travel blogs** — turistipercaso.it, camminiditalia.org, bimbieviaggi.it, mountainblog.it (B1/B2).
- **divulgazione** — media.inaf.it, cnr.it (B2/C1).
- **food** — gamberorosso.it (B1/B2).

## Data flow (genpapers S1, per slot)

```
refresh used-index (blacklist) + pool-index (catalog)
for each text slot:
    pool_select(level, genre, length)
        hit  -> use pooled cleaned text (zero fetch)
        miss -> corpus-hunter live:
                    over-fetch neighbouring candidates
                    grade all -> write pool/<id>.md for each
                    use best-fit for this slot
after build -> regenerate used-index (session's picks now filter out of the pool)
```

## Integration & immutability
- Pool files are **mutable inventory**; published papers stay **immutable**. No conflict.
- Copyright posture unchanged: the pool stores cleaned, adapted-within-level source text —
  exactly what committed `sources.md` already holds — used only as manifest-attributed
  excerpts in the student paper. Nothing from `reference/` ever enters the pool.

## Pruning (optional, YAGNI-guarded)
- `scripts/build_pool_index.py --prune` deletes pool files that are consumed
  (in `used-sources.txt`) AND/OR stale-perishable. Manual, never automatic.

## Bootstrap (optional)
- A one-off `--from-sources-md` mode can seed the pool from historical
  `papers/*/*/sources.md` (which hold cleaned full text + CEFR verdicts), recovering the
  never-picked "candidate 2" texts. Most historical entries are already consumed and will
  filter out, so value is modest; do it only if the initial pool feels too thin.

## Testing
- `build_pool_index.py` / `pool_select.py` against a seeded fixture pool: assert filtering
  by level/genre/length, exclusion of consumed URLs, and stale-perishable exclusion.
- End-to-end smoke: bank a couple of texts via a simulated over-fetch, run `pool_select`,
  confirm the right candidate surfaces and a consumed one is hidden.
- Idempotency: `build_pool_index.py` twice → identical `pool-index.yaml` (as done for used-index).

## Out of scope
- No separate `/harvest` command (folded into genpapers).
- No automatic pruning or scheduled crawling.
- No publish-gate on cross-date reuse (kept as an S1-side preventive per 2026-07-23 directive).
- No re-fetch-at-build path (pool stores full text).
```
