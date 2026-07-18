---
name: genpapers
description: Generate a dated batch of CILS-style practice papers (A1–C1, no listening) from authentic web texts, validate them with blind solving, quality audit and format audit, build the static site and publish to GitHub Pages. Use when the user asks to generate exam papers / practice tests ("genpapers", "生成试卷", "make paper", "出题").
---

# /genpapers — orchestrate one session of the paper factory

You are the **orchestrator**. The workflow authority is `factory/PIPELINE.md` — read it first, follow S0–S7. This file only adds Claude-Code-specific mechanics.

## Arguments

`/genpapers [levels] [date] [--no-publish] [--exam cils]`

- `levels`: comma list, default `A1,A2,B1,B2,C1`
- `date`: session date `YYYY-MM-DD`, default today (local time); use `YYYY-MM-DD-rN` for a same-day revision session
- `--no-publish`: stop after S6 (build), skip git commit/push
- `--exam`: default `cils` → all specs read from `factory/exams/<exam>/`

If the session dir for a level already exists **and was published**, refuse to overwrite (immutability) — offer a new date or a same-day revision session such as `YYYY-MM-DD-r2` instead.

## Role dispatch — unit of work: **one prova**; executor picked per tier

User directives: (2026-07-08) Claude orchestrates, heavy execution is dispatched out to save Claude tokens; (2026-07-13) the dispatch unit is a single prova, repairs touch only that prova, and **not everything goes to the strongest executor** — match the tier to the work.

### Executor tiering (cost control)

| Work | Executor | Why |
|---|---|---|
| Assembly, audits, reconcile/merge, build, git | local Python / shell | zero tokens |
| S3 blind solving (full paper or `--prova` extract) | `codex exec --sandbox read-only` (low effort) or Claude subagent with `model: sonnet` | cheap **and** model-diverse from the writer |
| S1 corpus | Codex task (needs network) or Sonnet subagent | fetch-heavy, not reasoning-heavy |
| S2 fragments: all A1–B1 prove, all W/O/GLOSSARIO fragments | Codex (medium effort) or Sonnet subagent | sufficient quality |
| S2 fragments: B2/C1 ricostruzione, C1 trasformazioni & literary adaptation; any prova failing its 2nd repair round | Codex (high effort) or Opus subagent | genuinely hard |
| Orchestration, gates, manifests | main context | by design |

Codex dispatch: `node "$(ls -d ~/.claude/plugins/cache/openai-codex/codex/*/scripts/codex-companion.mjs | tail -1)" task --background --write "<role body + prova inputs + output path>"` → `status`/`result <job-id>`.

### Mechanics

- **S2 (per prova):** one background task per fragment — prompt = item-writer role body + the prova's `exam.yaml` spec + its ONE source-text section from `sources.md` + the `{{SLOT}}` names to fill + output path `papers/<date>/<LEVEL>/fragments/<ID>.json`. All fragments of a level run in parallel. Then `python3 scripts/assemble_paper.py --paper-dir papers/<date>/<LEVEL>` (local, no LLM) produces `paper.md`/`answers.md`/`key.json` and fails listing unfilled slots. LLMs never emit template skeleton text (covers, consegne, answer sheets).
- **S3:** `python3 scripts/blind_validation.py prepare --paper-dir papers/<date>/<LEVEL>` (whole paper) or `--prova L3,S2` (extract only those blocks) → fresh solver on the isolated file. Capture the solver's ANSWERS/FLAGS to a file (`codex exec … > blind-output.txt`, or ask the subagent to reply with the two JSON blocks only) instead of hand-transcribing JSON through the main conversation.
- **S4 (per prova):** reconcile with `python3 scripts/blind_validation.py reconcile --paper-dir papers/<date>/<LEVEL> --blind-output <file> --report papers/<date>/<LEVEL>/blind-validation.json --write-manifest`. Each failing prova → **fresh** item-writer task (that fragment + its source text + defect list; it may fix stems/keys or change the prova's testing approach). Re-assemble, then re-validate only the affected prove: `prepare --prova …` → solver → `python3 scripts/blind_validation.py merge-output --base <prev full blind-output> --patch <partial> --out <merged>` → full reconcile on the merged file. **Never resume a previous authoring agent** — transcript replay costs more than the repair itself.
- Corpus tasks on Codex must quote fetch evidence (curl output snippets + URLs); spot-verify 1–2 sources with WebFetch. If Codex has no network, fall back to Sonnet subagents with WebSearch/WebFetch.

Alternative (only when the user explicitly allows Claude subagents):

| Stage | subagent_type | model | run_in_background |
|---|---|---|---|
| S1 corpus | `corpus-hunter` | sonnet | yes — all levels in parallel |
| S2 fragments | `item-writer` | sonnet (A1–B1, W, O, glossario) / opus (hard B2–C1 prove) | yes — parallel per prova once S1 gate passed |
| S3 blind validation | `blind-solver` | sonnet | per level (or per prova) after assembly |
| S4 repairs | `item-writer` (**fresh**, per prova) | as S2; opus after a 2nd failure | as needed, ≤2 rounds |
| S5 format audit | deterministic script | — | — |

- If a named agent type is not registered (first session after install), fall back to `subagent_type: general-purpose` and paste the role file's body into the prompt.
- Every dispatch prompt must state: level, session date, absolute file paths the role needs, and the exact output path.
- **Blind-solver isolation (hard rule):** copy `paper.md` alone to an isolated dir outside the repo (`/tmp/cils-blind-<session>-<level>/paper.md`) and give the solver ONLY that absolute path ("read exactly this one file, nothing else, no web"). Never mention `answers.md`, `sources.md`, source URLs or the repo path in that prompt. (Pasting the full paper text into the prompt is an equally valid alternative.)
- After each stage, append the manifest entries specified in `factory/PIPELINE.md` yourself (orchestrator owns `manifest.yaml`).

## Gates you enforce personally

1. **S1 QC:** every text slot has an accepted candidate (genre, CEFR verdict, length band). Reject skimpy metadata.
2. **S2 mechanical check:** count items per prova against `factory/exams/<exam>/exam.yaml`; verify point statements, no visible source attribution lines in `paper.md`, complete manifest source metadata, and no `{{slots}}` left.
3. **S4 reconcile:** use `scripts/blind_validation.py reconcile` to diff key vs blind answers; any mismatch or flag → fresh per-prova repair → partial re-blind (`prepare --prova`) merged via `merge-output` → full reconcile; 100%/0-flags within 2 rounds or the level stays `draft`.
4. **S5:** apply auditor fixes, re-audit once if needed.
5. **S5/S5b:** run `python3 scripts/format_audit.py --session <date> --levels <published-candidates> --report papers/<date>/format-audit.json --write-manifest`, then `python3 scripts/paper_quality_audit.py --session <date> --levels <published-candidates> --report papers/<date>/quality-audit.json --write-manifest`; repair any failures (section order/counts, source/study-aid leakage, student-copy leakage, length/depth problems, missing quality metadata, cross-level reuse, variant mismatch) and rerun until pass. Only then set `status: published`.

## Build & publish

Publish is automatic once all gates pass (user directive 2026-07-18) — do not ask for confirmation; only `--no-publish` stops S7.

```bash
python3 scripts/build_site.py          # S6 — verify exit 0 and per-level outputs
git add papers/<date>/<published-levels> docs
git commit -m "feat(papers): <date> <levels>"   # S7 (skip with --no-publish; draft levels excluded)
git push
# Deploy: Pages serves docs/ from main. If on a working branch, also merge into main and push it.
# If local main is checked out in another worktree: git -C <worktree> merge <branch> && git -C <worktree> push origin main
```

## Final report to the user (always)

Markdown table: level | status (published/draft+reason) | objective items | blind agreement | repair rounds | link paths under `docs/papers/<date>/<level>/`. Then the live site URL (see README) and any drafts to regenerate.
