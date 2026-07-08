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

## Role dispatch — default executor: Codex (Claude orchestrates only)

User directive (2026-07-08): to save Claude tokens, stages run on Codex; Claude Code builds the dispatch prompts (from the role files in `.claude/agents/` + the level inputs), enforces gates, owns manifests, builds, publishes.

- S1/S2/S4/S5: `node "$(ls -d ~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs | tail -1)" task --background --write "<role body + level inputs + output paths>"` → `status`/`result <job-id>`. Levels can run as parallel background tasks.
- S3: run `python3 scripts/blind_validation.py prepare --paper-dir papers/<date>/<LEVEL>` to create `/tmp/cils-blind-<session>-<level>/paper.md`, then run fresh `codex exec --sandbox read-only` on that isolated file (fresh session ⇒ independent context).
- S2 must also emit `papers/<date>/<LEVEL>/key.json` (`{"L1.1": "B", …, "L3": "A-D-…"}`), so S4 reconcile is `python3 scripts/blind_validation.py reconcile --paper-dir papers/<date>/<LEVEL> --blind-output <file> --report papers/<date>/<LEVEL>/blind-validation.json --write-manifest`; only failing items go back to an LLM.
- Corpus tasks on Codex must quote fetch evidence (curl output snippets + URLs); spot-verify 1–2 sources with WebFetch. If Codex has no network, fall back to running S1 in the main context with WebSearch/WebFetch.

Alternative (only when the user explicitly allows Claude subagents):

| Stage | subagent_type | run_in_background |
|---|---|---|
| S1 corpus | `corpus-hunter` | yes — dispatch all levels in parallel |
| S2 authoring | `item-writer` | yes — parallel per level once its S1 gate passed |
| S3 blind validation | `blind-solver` | per level after S2 |
| S4 repairs | `item-writer` (fresh) | as needed, ≤2 rounds |
| S5 format audit | `format-auditor` | per level |

- If a named agent type is not registered (first session after install), fall back to `subagent_type: general-purpose` and paste the role file's body into the prompt.
- Every dispatch prompt must state: level, session date, absolute file paths the role needs, and the exact output path.
- **Blind-solver isolation (hard rule):** copy `paper.md` alone to an isolated dir outside the repo (`/tmp/cils-blind-<session>-<level>/paper.md`) and give the solver ONLY that absolute path ("read exactly this one file, nothing else, no web"). Never mention `answers.md`, `sources.md`, source URLs or the repo path in that prompt. (Pasting the full paper text into the prompt is an equally valid alternative.)
- After each stage, append the manifest entries specified in `factory/PIPELINE.md` yourself (orchestrator owns `manifest.yaml`).

## Gates you enforce personally

1. **S1 QC:** every text slot has an accepted candidate (genre, CEFR verdict, length band). Reject skimpy metadata.
2. **S2 mechanical check:** count items per prova against `factory/exams/<exam>/exam.yaml`; verify point statements, attribution lines, no `{{slots}}` left.
3. **S4 reconcile:** use `scripts/blind_validation.py reconcile` to diff key vs blind answers; any mismatch or flag → repair → fresh blind-check of affected prove; 100%/0-flags within 2 rounds or the level stays `draft`.
4. **S5:** apply auditor fixes, re-audit once if needed; only then set `status: published`.

## Build & publish

```bash
python3 scripts/build_site.py          # S6 — verify exit 0 and per-level outputs
git add papers/<date>/<published-levels> docs
git commit -m "feat(papers): <date> <levels>"   # S7 (skip with --no-publish; draft levels excluded)
git push
```

## Final report to the user (always)

Markdown table: level | status (published/draft+reason) | objective items | blind agreement | repair rounds | link paths under `docs/papers/<date>/<level>/`. Then the live site URL (see README) and any drafts to regenerate.
