---
description: Generate CILS practice papers through the repo paper factory.
argument-hint: "[levels] [date] [--no-publish] [--exam cils]"
---

# /genpapers

Thin slash-command entrypoint for the paper factory.

Delegate the full workflow to `.claude/skills/genpapers/SKILL.md`. Before doing any stage work, read `factory/PIPELINE.md` and follow S0 through S7 for the requested levels.

Defaults:
- exam: `cils`
- levels: `A1,A2,B1,B2,C1`
- session date: today, unless a `YYYY-MM-DD` date is provided; use `YYYY-MM-DD-rN` for a same-day revision session that must not overwrite a published session

Supported option:
- `--no-publish`: run through build validation and skip S7 commit/push.

Hard reminders:
- S3 blind validation must be independent.
- The blind solver may receive only `paper.md`, never `answers.md`, `sources.md`, manifests, source URLs, repo context, or web access.
- Published papers are immutable; do not overwrite a published session.
