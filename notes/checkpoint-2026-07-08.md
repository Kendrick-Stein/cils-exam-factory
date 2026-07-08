# Session checkpoint — 2026-07-08 (spend-limit interruption)

**What happened:** at ~16:40 the Claude monthly spend limit was hit; all running subagents were cut off ("You've hit your monthly spend limit"). Salvage assessment below. **New execution mode (user directive): Claude orchestrates, Codex executes all heavy stages** — see CLAUDE.md "Execution mode".

## State of session 2026-07-08

| Level | S1 corpus | S2 paper | S3–S4 validation | S5 audit | Notes |
|---|---|---|---|---|---|
| A1 | ✅ `sources.md` 6/6 + manifest | ❌ (agent died) | — | — | ready to author |
| A2 | ✅ `sources.md` 6/6 | ❌ | — | — | manifest sources[] still to fill from sources.md |
| B1 | ✅ `sources.md` 6/6 + manifest | ❌ (agent died) | — | — | pilot level, author first |
| B2 | ❌ no sources.md | ❌ | — | — | corpus agent died before writing; re-run S1 |
| C1 | ✅ `sources.md` 6/6 | ❌ | — | — | manifest sources[] to fill |

Everything else (factory specs, 5 templates, skill+agents, site builder, tests) is **complete and committed**.

## Resume instructions (any future session)

1. If Claude subagents are available again: run `/genpapers A1,A2,B2,C1 2026-07-08` logic but SKIP S1 for levels with a complete `sources.md` (A1/A2/C1) — go straight to S2. B2 needs S1 first. B1: check `papers/2026-07-08/B1/` — if `paper.md` exists and manifest shows validation passed, don't regenerate.
2. If not: author inline from each level's `sources.md` following `factory/PIPELINE.md`, blind-validate with:
   `codex exec --sandbox read-only "Solve the exam paper at /tmp/cils-blind-<date>-<L>/paper.md …"` (see AGENTS.md §2).
3. After any level passes S5: set manifest `status: published`, run `python3 scripts/build_site.py`, commit `papers/ docs/`, push.
4. Publishing target: public repo `cils-exam-factory` (owner Kendrick-Stein), Pages from `main:/docs`. If the repo doesn't exist yet: `gh repo create cils-exam-factory --public --source . --push` then enable Pages via `gh api`.

## User-facing note

The user must raise the limit at claude.ai/settings/usage (or wait for the monthly reset) for subagent-parallel generation. Single-session inline generation still works but is slower and consumes the main context.
