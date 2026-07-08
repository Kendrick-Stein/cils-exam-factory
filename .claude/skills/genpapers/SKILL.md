---
name: genpapers
description: Generate a dated batch of CILS-style practice papers (A1–C1, no listening) from authentic web texts, validate them with blind solving and format audit, build the static site and publish to GitHub Pages. Use when the user asks to generate exam papers / practice tests ("genpapers", "生成试卷", "make paper", "出题").
---

# /genpapers — orchestrate one session of the paper factory

You are the **orchestrator**. The workflow authority is `factory/PIPELINE.md` — read it first, follow S0–S7. This file only adds Claude-Code-specific mechanics.

## Arguments

`/genpapers [levels] [date] [--no-publish] [--exam cils]`

- `levels`: comma list, default `A1,A2,B1,B2,C1`
- `date`: session date `YYYY-MM-DD`, default today (local time)
- `--no-publish`: stop after S6 (build), skip git commit/push
- `--exam`: default `cils` → all specs read from `factory/exams/<exam>/`

If the session dir for a level already exists **and was published**, refuse to overwrite (immutability) — offer a new date instead.

## Role dispatch (Agent tool)

| Stage | subagent_type | run_in_background |
|---|---|---|
| S1 corpus | `corpus-hunter` | yes — dispatch all levels in parallel |
| S2 authoring | `item-writer` | yes — parallel per level once its S1 gate passed |
| S3 blind validation | `blind-solver` | per level after S2 |
| S4 repairs | `item-writer` (fresh) | as needed, ≤2 rounds |
| S5 format audit | `format-auditor` | per level |

- If a named agent type is not registered (first session after install), fall back to `subagent_type: general-purpose` and paste the role file's body into the prompt.
- Every dispatch prompt must state: level, session date, absolute file paths the role needs, and the exact output path.
- **Blind-solver isolation (hard rule):** paste the full text of `paper.md` INTO the prompt; instruct it to use no files and no web. Never mention `answers.md`, `sources.md` or source URLs in that prompt.
- After each stage, append the manifest entries specified in `factory/PIPELINE.md` yourself (orchestrator owns `manifest.yaml`).

## Gates you enforce personally

1. **S1 QC:** every text slot has an accepted candidate (genre, CEFR verdict, length band). Reject skimpy metadata.
2. **S2 mechanical check:** count items per prova against `factory/exams/<exam>/exam.yaml`; verify point statements, attribution lines, no `{{slots}}` left.
3. **S4 reconcile:** diff key vs blind answers; any mismatch or flag → repair → fresh blind-check of affected prove; 100%/0-flags within 2 rounds or the level stays `draft`.
4. **S5:** apply auditor fixes, re-audit once if needed; only then set `status: published`.

## Build & publish

```bash
python3 scripts/build_site.py          # S6 — verify exit 0 and per-level outputs
git add papers docs
git commit -m "feat(papers): <date> <levels>"   # S7 (skip with --no-publish)
git push
```

## Final report to the user (always)

Markdown table: level | status (published/draft+reason) | objective items | blind agreement | repair rounds | link paths under `docs/papers/<date>/<level>/`. Then the live site URL (see README) and any drafts to regenerate.
