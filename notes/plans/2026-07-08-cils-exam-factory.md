# CILS Exam Factory — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> **This session:** executed inline (superpowers:executing-plans) with targeted delegation — PDF-analysis subagents (already running), Codex for the site builder, and the generation pipeline's own agents for papers. Rationale: most tasks are context-heavy authoring; the pipeline itself is the subagent workflow the user asked for.

**Goal:** A repo where `/genpapers` produces validated, CILS-faithful practice papers (A1–C1, no listening) with answer keys, model essays and vocabulary packs, rendered to a GitHub Pages site with PDF downloads.

**Architecture:** Knowledge layer (`factory/` specs & templates, harness-agnostic) + orchestration layer (`.claude/skills/genpapers`, `.claude/agents/*`, `AGENTS.md` for Codex) + deterministic build layer (`scripts/build_site.py`, headless-Chrome PDFs, `docs/` Pages root). Spec: `notes/specs/2026-07-08-cils-exam-factory-design.md`.

**Tech Stack:** Claude Code skills/subagents, Codex CLI, Python 3.12 (`markdown`, `pyyaml`), headless Google Chrome for PDF, GitHub Pages (main:/docs), git + gh CLI.

---

## Interfaces locked by this plan

### `papers/` data model (produced by pipeline, consumed by build)

```
papers/<YYYY-MM-DD>/<LEVEL>/
├── paper.md        # student copy, Italian only
├── answers.md      # key + explanations (中文 notes) + 范文 + Glossario
├── sources.md      # S1 output: candidate texts + metadata (working file)
└── manifest.yaml   # provenance + validation log
```

`paper.md` / `answers.md` front-matter (YAML, first block in file):

```yaml
---
exam: CILS
level: B1                    # A1|A2|B1|B2|C1
level_name: "CILS UNO — B1"  # official name from exam.yaml
session: "2026-07-08"
kind: paper                  # paper | answers
---
```

`manifest.yaml` schema:

```yaml
exam: cils
level: B1
session: "2026-07-08"
title: "CILS UNO — B1 · Esercitazione"
status: published            # draft | published  (build only publishes 'published')
sources:
  - id: T1
    url: "https://..."
    title: "..."
    publisher: "ANSA"
    accessed: "2026-07-08"
    used_in: "Comprensione della lettura, Prova n. 1"
    adapted: true
    words_used: 420
pipeline:
  generator: claude-fable-5
  template: factory/exams/cils/templates/B1.md
  stages:                    # append-only log
    - {stage: corpus, at: "2026-07-08T15:10+08:00"}
    - {stage: authoring, at: "..."}
    - {stage: blind_validation, at: "...", agreement: "38/40", flags: 2}
    - {stage: reconcile, at: "...", round: 1, fixed_items: ["A.3", "B.12"]}
    - {stage: blind_validation, at: "...", agreement: "40/40", flags: 0}
    - {stage: format_audit, at: "...", result: pass}
validation:
  objective_items: 40
  final_agreement: 40
  rounds: 1
  result: pass               # pass | fail
```

### `docs/` output model (produced by build, served by Pages)

```
docs/
├── index.html                          # sessions × levels grid, newest first
├── assets/{site.css, paper.css}
└── papers/<date>/<LEVEL>/{paper.html, answers.html, paper.pdf, answers.pdf, paper.md, answers.md}
```

### Build CLI

```
python3 scripts/build_site.py            # rebuild all published papers + index
python3 scripts/build_site.py --no-pdf   # skip PDF regeneration (fast preview)
```

PDF via: `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf=<out> <file-url>`

---

### Task 1: Repo scaffold — CLAUDE.md, AGENTS.md, README

**Files:** Create `CLAUDE.md`, `AGENTS.md`, `README.md`

- [ ] Write `CLAUDE.md`: project purpose, map of `factory/`, how `/genpapers` works, quality gates, "never republish `reference/`", commit conventions.
- [ ] Write `AGENTS.md` (Codex adapter): "to generate papers, follow `factory/PIPELINE.md`; run blind validation via fresh `codex exec` subprocess; then `python3 scripts/build_site.py` and commit."
- [ ] Write `README.md`: what this repo is, site URL, disclaimer (not affiliated with Università per Stranieri di Siena), how papers are made (pipeline diagram), local usage.
- [ ] Commit: `chore: scaffold repo docs`

### Task 2: Consolidate official-paper analysis → `exam.yaml` + `style-guide.md`

**Blocked by:** the five analysis agents writing `factory/exams/cils/analysis/{A1,A2,B1,B2,C1,OVERVIEW}.md`.

**Files:** Create `factory/exams/cils/exam.yaml`, `factory/exams/cils/style-guide.md`

- [ ] Read all six analysis files; spot-check 2–3 claims against the PDFs (Read tool, specific pages) where numbers look suspicious (e.g. items ≠ points × weight).
- [ ] Write `exam.yaml`: per level → `level_name`, `sections[]` (id, nome, durata_min, punti_max, prove[]: numero, titolo, tipo, items, punti_per_item, punti, testo {genere, parole_min, parole_max, fonte_tipo}), `soglia` (pass threshold), plus `excluded_sections: [ascolto, orale]` with official names/durations for transparency.
- [ ] Write `style-guide.md`: verbatim consegna phrasebook per prova type; numbering conventions; cover/section header wording; answer-marking conventions; text-attribution format; typical distractor style; what the chiavi section looks like.
- [ ] Commit: `feat(cils): exam.yaml + style guide from official dic-2024 papers`

### Task 3: Level templates (A1, A2, B1, B2, C1)

**Files:** Create `factory/exams/cils/templates/{A1,A2,B1,B2,C1}.md`

- [ ] Each template = complete fill-in skeleton for `paper.md` AND `answers.md` (two parts in one file, split by `<!-- ANSWERS -->`): front-matter, cover block, per-section headers with durations/points, per-prova verbatim consegne with `{{...}}` slots for texts/items, item-count comments (`<!-- exactly 7 items -->`), writing tasks with word ranges, then answers part: chiavi table, per-item explanation slots, 范文 slot per writing task, Glossario table (15–25 rows, columns: Parola/Espressione | Cat. | 中文 | EN | Esempio dal testo).
- [ ] A1 template header carries: `<!-- A1: struttura da Linee guida CILS (nessun campione dic-2024); confidence: media -->`.
- [ ] Cross-check every template against `exam.yaml` counts (item numbers, points sums).
- [ ] Commit: `feat(cils): level templates A1–C1`

### Task 4: Corpus registry, CEFR criteria, validation checklist

**Files:** Create `factory/corpus/sources.yaml`, `factory/corpus/cefr-criteria.md`, `factory/validation/checklist.md`

- [ ] `sources.yaml`: per level → genres needed (mapped to template slots) → whitelisted sources with concrete URLs (ANSA, RaiNews, Il Post, Focus, Today.it, GialloZafferano, siti istituzionali, Liberliber, Wikisource IT, ecc.), paywall notes, fallbacks; global rules (no paywalled full texts, attribution format, length bands per level).
- [ ] `cefr-criteria.md`: rubric per level (grammar inventory, lexical range, sentence complexity); anchor excerpts (≤50 words) taken from the official-paper analyses; quantitative sanity bands (avg sentence length, estimated rare-word share); decision procedure (grade → compare to anchors → accept/adapt/reject).
- [ ] `validation/checklist.md`: objective-item gates (single defensible answer, distractors plausible-but-wrong, no trivia-from-outside-text, no overlapping options), paper-level gates (counts/points/sums/word-ranges/section order/attribution lines present), audit output format (PASS/FAIL per line + fix list).
- [ ] Commit: `feat: corpus registry, CEFR criteria, validation checklist`

### Task 5: `factory/PIPELINE.md` (runtime workflow, harness-agnostic)

**Files:** Create `factory/PIPELINE.md`

- [ ] Stages S0–S7 exactly as in the design spec §5 (scaffold → corpus → authoring → blind validation → reconcile ≤2 rounds → format audit → build → publish), with: per-stage inputs/outputs/actor, gate criteria, manifest entries to append, failure behavior (`status: draft`, excluded from publish), and per-harness execution notes (Claude Code: dispatch `.claude/agents/*` roles via Agent tool, levels in parallel; Codex: sequential + fresh `codex exec` for blind solve).
- [ ] Commit: `feat: pipeline spec`

### Task 6: `/genpapers` skill + agent role definitions

**Files:** Create `.claude/skills/genpapers/SKILL.md`, `.claude/agents/{corpus-hunter,item-writer,blind-solver,format-auditor}.md`

- [ ] `SKILL.md`: name/description front-matter; args (`levels` default `A1,A2,B1,B2,C1`; `date` default today; `--no-publish`; `--exam cils`); orchestration algorithm referencing `factory/PIPELINE.md` (never duplicating specs); explicit rule: blind-solver must receive ONLY `paper.md`; publish step = `build_site.py` + git commit/push; final report table.
- [ ] Agent files: front-matter (`name`, `description`, `tools`) + role instructions that point at the factory files they must read; `corpus-hunter` gets WebSearch/WebFetch/Read/Write; `blind-solver` gets Read/Write only (no web — prevents "answer by searching the source article").
- [ ] Commit: `feat: /genpapers skill + pipeline agent roles`

### Task 7: Site builder + PDF pipeline (delegated to Codex)

**Files:** Create `scripts/build_site.py`, `scripts/assets/site.css`, `scripts/assets/paper.css`, `scripts/README.md`; Test: `scripts/test_build_site.py` + fixture `papers/_fixture/FX/`

Spec handed to Codex (acceptance = test passes; I review the diff):

- [ ] `build_site.py` (stdlib + `markdown` + `yaml`; if imports missing: `python3 -m pip install --user markdown pyyaml`):
  - scan `papers/*/*/manifest.yaml` (skip dirs starting with `_`), include only `status: published`;
  - md→HTML: strip front-matter, render with `markdown` extensions `['tables','attr_list','md_in_html']`, wrap in shell template (lang=it, links `../../assets/paper.css`, header with level badge + session + site name, footer with disclaimer + attribution note);
  - PDF: headless Chrome command above unless `--no-pdf`; skip regen when source md older than existing pdf (mtime);
  - copy raw `paper.md`/`answers.md` into `docs/papers/...`;
  - regenerate `docs/index.html`: hero, per-session cards grouped by date desc, per level row → links PDF/HTML/MD for paper & answers, level badges colored per CEFR, methodology + disclaimer footer, no JS required;
  - idempotent; exit non-zero on malformed manifest; UTF-8 everywhere.
- [ ] `paper.css`: A4 `@page` margins 2cm, exam-like typography (serif body, clear prova headers, item spacing, no page-break inside items — `break-inside: avoid`), header/footer suppressed (Chrome flag), answer boxes/lines rendered from markdown conventions (e.g. `___` runs, tables).
- [ ] `site.css`: clean card grid, CEFR badge palette, responsive, no framework.
- [ ] `test_build_site.py`: builds fixture (tiny fake paper) with `--no-pdf` → asserts docs files exist & index links them; with PDF (only if Chrome present) → asserts pdf >10KB.
- [ ] Run test: `python3 scripts/test_build_site.py` → PASS; delete/keep fixture under `papers/_fixture` (skipped by scanner but used by test via override arg).
- [ ] Review Codex diff, fix, commit: `feat: static site + PDF builder`

### Task 8: Pilot — generate B1 paper end-to-end through the real pipeline

- [ ] S0: `papers/2026-07-08/B1/` scaffold + manifest stub.
- [ ] S1: dispatch corpus-hunter (role file content inline in prompt — new agent files aren't registered until next session): needs per `exam.yaml` B1 text slots; output `sources.md`; orchestrator QC.
- [ ] S2: dispatch item-writer with template + sources.md → `paper.md` + `answers.md` (complete, counts exact).
- [ ] S3: dispatch blind-solver with ONLY `paper.md` → answers + flags.
- [ ] S4: diff vs key; patch flagged/mismatched items via item-writer; re-blind-check affected prova (fresh agent). Gate: 100% agreement, 0 flags, ≤2 rounds.
- [ ] S5: dispatch format-auditor vs template + checklist → apply fixes → PASS.
- [ ] S6: `python3 scripts/build_site.py` → check `docs/papers/2026-07-08/B1/*` incl. PDFs open correctly (spot-read PDF).
- [ ] Update manifest at every stage. Commit: `feat(papers): 2026-07-08 B1 pilot`

### Task 9: Batch — A1, A2, B2, C1 in parallel

- [ ] Dispatch 4 paper-generation flows (S1→S2 per level) as parallel background agents; then S3–S5 per level as pilot; fix rounds as needed.
- [ ] Build site; verify each level's PDFs; commit: `feat(papers): 2026-07-08 full batch A1–C1`

### Task 10: Publish — GitHub repo + Pages

- [ ] `gh repo create cils-exam-factory --public --source . --push` (default branch main).
- [ ] Enable Pages: `gh api -X POST repos/Kendrick-Stein/cils-exam-factory/pages -f 'source[branch]=main' -f 'source[path]=/docs'` (fallback: PUT if exists).
- [ ] Poll `gh api repos/.../pages` until `status: built`; `curl -I` the site URL and one PDF URL → 200.
- [ ] Add site URL to README + CLAUDE.md; commit+push: `docs: link live site`

### Task 11: Final verification & handoff

- [ ] superpowers:verification-before-completion — walk every user acceptance criterion (R1–R9 in spec §3) with evidence (file paths, URLs, HTTP checks).
- [ ] Confirm `reference/` is untracked (`git status --ignored | grep reference`).
- [ ] Save memories: project (goals, sample-data paths, repo/site URLs, cadence), user (Chinese-speaking Italian learner; wants 中文 glosses), feedback (template fidelity is the acceptance bar).
- [ ] Final report to user: what was built, URLs, how to run `/genpapers` next time, known limitations (A1 lower-confidence template, C2 not yet analyzed).

## Self-review

- Spec coverage: R1→T6, R2→T3/T8, R3→T3 (Glossario), R4→T3 (范文 slots; excluded sections in exam.yaml), R5→T7/T10, R6→T2/T3/T5 gates, R7→T5 (manifest) /T6, R8→config-driven layout (T2–T5 under `factory/exams/cils/`), R9→skill args (T6). ✓
- No placeholders: content requirements are spelled out per file; scripts have acceptance tests; verbatim-consegna sourcing defined (analysis files). ✓
- Type consistency: manifest/front-matter/docs-tree schemas defined once above and referenced by T3/T6/T7/T8. ✓
