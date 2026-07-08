# CILS Exam Factory — Design Spec

- **Date:** 2026-07-08
- **Status:** approved-by-default (user provided full requirements and switched to execution mode; deviations from this spec require a note here)
- **Spec location note:** superpowers default is `docs/superpowers/specs/`, but `docs/` is reserved as the GitHub Pages web root in this repo, so specs live in `notes/specs/`.

## 1. Goal

One command — `/genpapers` in Claude Code (or the equivalent request in Codex CLI) — produces a **dated batch of CILS-style practice papers** for levels **A1, A2, B1, B2, C1** (default: all five), each consisting of:

1. **Student paper** (`paper.md`) — Italian only, structure/wording as close as possible to the official dic-2024 CILS papers: reading comprehension, structures of communication (grammar/vocab), and written production. **No listening, no oral.**
2. **Answer key & study pack** (`answers.md`) — correct answers, per-item explanations (concise, with 中文 notes for Chinese-speaking learners), a **model essay (范文)** per writing task, and a **"Glossario da ricordare"**: 15–25 words/phrases worth memorizing, IT → 中文/EN with an example from the texts.
3. **Manifest** (`manifest.yaml`) — sources (URL, publisher, access date), pipeline stages, validation log → reproducibility.

Then the build layer renders HTML + PDF, regenerates the static site in `docs/`, and publishes via git push to **GitHub Pages**, where anyone can download fresh papers.

## 2. Non-goals

- Ascolto (listening) and produzione orale are excluded by design (one-line note in papers for transparency).
- No affiliation with Università per Stranieri di Siena; the site carries a clear disclaimer. Official PDFs stay local (`reference/`, gitignored) and are never republished.
- No CI/CD in v1 — build and publish run locally as pipeline steps (GitHub Actions can be added later without redesign).

## 3. Requirements traceability

| # | Requirement (user) | Design answer |
|---|---|---|
| R1 | `/genpapers` in this repo generates papers at multiple levels | Skill orchestrates per-level pipeline; `--levels`, `--date`, `--no-publish` options |
| R2 | Questions + correct answers | `paper.md` + `answers.md`, independent blind-solve validation |
| R3 | Extra learning content (words/phrases) after answers | Glossario da ricordare section, spec'd in templates |
| R4 | No listening; writing gets a model essay | Sections excluded; 范文 required per writing task |
| R5 | GitHub Pages site with click-to-download | `docs/` static site, PDF/HTML/MD per paper, index by date × level |
| R6 | As close as possible to real exam templates | Templates derived from official dic-2024 papers (verbatim consegne, same counts/points/durations); format-audit gate |
| R7 | Minimal human intervention, reproducible | Single command through publish; manifests; quality gates auto-retry |
| R8 | Extensible to CELI/PLIDA/TELC/DELF/JLPT/HSK | Config-driven: `factory/exams/<exam>/`; agents and scripts are exam-agnostic |
| R9 | ~5 papers per run, daily to weekly cadence | Batch = one dated session dir; on-demand invocation (cron optional later) |

## 4. Architecture — three layers

### 4.1 Knowledge layer — `factory/` (harness-agnostic "brain")

```
factory/
├── PIPELINE.md                  # master workflow: stages, gates, failure handling
├── exams/cils/
│   ├── exam.yaml                # levels → sections → prove → item counts/points/timing
│   ├── analysis/{A1,A2,B1,B2,C1,OVERVIEW}.md   # extracted from official papers (agents)
│   ├── templates/{A1,A2,B1,B2,C1}.md           # fill-in skeletons w/ verbatim consegne
│   └── style-guide.md           # layout & wording conventions from real papers
├── corpus/
│   ├── sources.yaml             # whitelisted authentic sources per level/genre
│   └── cefr-criteria.md         # CEFR grading rubric + anchor excerpts + heuristics
└── validation/checklist.md      # item & format quality gates
```

Both Claude Code and Codex execute *from these files*; nothing pipeline-critical lives only in a skill.

### 4.2 Orchestration layer — thin adapters

- `.claude/skills/genpapers/SKILL.md` — Claude Code entry; fans out **per-level subagents** (parallel) and runs gates.
- `.claude/agents/` — role definitions: `corpus-hunter` (search/fetch/clean/CEFR-grade), `item-writer` (fill template, key, explanations, 范文, glossario), `blind-solver` (solves student copy only), `format-auditor` (checklist vs template).
- `AGENTS.md` — Codex adapter: same pipeline run sequentially; blind-solve independence via a fresh `codex exec` subprocess.

### 4.3 Build/publish layer — `scripts/` (deterministic)

- `build_site.py` — scans `papers/**/manifest.yaml` → renders paper/answers HTML (print CSS), makes PDFs via **headless Chrome** (present on this machine; zero extra installs), regenerates `docs/index.html`.
- Publishing = `git add/commit/push`; Pages serves `main:/docs`.

**Alternatives considered:** (a) one mega-agent per paper — rejected: validation loses independence, no source QC before heavy authoring, user explicitly asked for modular components; (b) classical-NLP CEFR classifier + LaTeX pipeline — rejected for v1: heavy dependencies for marginal gain; rubric+anchor LLM grading with quantitative sanity checks is adequate, and HTML/print-CSS gives one rendering path for both site and PDF (pandoc/typst not installed; xelatex exists but LaTeX authoring by agents is fragile).

## 5. Generation pipeline (per level, per session)

| Stage | Actor | Output | Gate |
|---|---|---|---|
| S0 scaffold | script/orchestrator | `papers/DATE/LEVEL/` | — |
| S1 corpus | corpus-hunter agent | `sources.md` (2–5 cleaned candidate texts + metadata + CEFR grade) | orchestrator QC: genre coverage, lengths, level match |
| S2 authoring | item-writer agent | draft `paper.md` + `answers.md` | template counts/points respected |
| S3 blind validation | blind-solver agent (fresh context, student copy ONLY) | `blind-answers` + ambiguity flags | — |
| S4 reconcile | orchestrator (+item-writer patches) | fixed items; re-blind-check affected prove | 100% agreement on objective items, no ambiguity flags; ≤2 rounds else paper → `draft`, excluded from publish |
| S5 format audit | format-auditor agent | audit report; fixes applied | checklist fully green |
| S6 build | `build_site.py` | HTML/PDF/site | files exist, non-empty |
| S7 publish | git | pushed `docs/` + `papers/` | skipped with `--no-publish` or if any level still `draft` and `--strict` |

Every stage appends to `manifest.yaml` (timestamps, agents, rounds, diffs) → **reproducibility**.

## 6. Corpus & authenticity policy

- **Only authentic web sources**, whitelisted per level in `sources.yaml`: A1/A2 — annunci, orari, menù, cartelli, e-mail semplici, brevi notizie locali; B1 — cronaca, blog, guide pratiche, interviste semplici; B2 — approfondimenti, divulgazione scientifica, recensioni; C1 — editoriali, saggistica, **testi letterari** (Liberliber/Wikisource, public domain).
- Prefer non-paywalled: ANSA, RaiNews, Il Post (free), Focus, Today.it, siti istituzionali (comuni, musei, Trenitalia), GialloZafferano, Subito.it (realia), Liberliber/Wikisource.
- Texts are **abridged/adapted with credit** — `«Testo adattato da: <testata>, <URL>, consultato il <data>»` — exactly the practice of real CILS papers ("adattato da..."). Excerpt length stays within level norms (~100–650 words). Originals never stored in the repo; manifest keeps the pointer.
- **CEFR grading:** rubric in `cefr-criteria.md` + comparison against anchor excerpts from the official papers + quantitative sanity signals (sentence length, rare-lexis density). Texts failing the target grade are discarded at S1.

## 7. Fidelity to real exams

- Per-level structure (prove, item counts, punti, durations, consegna wording) comes from the **dic-2024 official papers** the user provided, extracted into `analysis/*.md` by dedicated agents; consegne are reused **verbatim** (formulaic instructions), source texts are always fresh.
- **A1 exception:** no 2024 sample available → structure from official *Linee guida CILS* + A2 conventions; marked lower-confidence in the template header.
- `format-auditor` checks every generated paper against the template + `validation/checklist.md` (counts, point sums, word ranges, section order, headers).

## 8. Publishing

- Public repo **`cils-exam-factory`** (owner Kendrick-Stein), Pages from `main:/docs`.
- `docs/index.html`: sessions × levels grid, per paper: **[PDF] [HTML] [MD]** for both paper and answers; disclaimer + methodology page.
- Papers are immutable once published; corrections create a new dated session.

## 9. Extensibility

Adding CELI/PLIDA/TELC/DELF/JLPT/HSK = create `factory/exams/<exam>/{exam.yaml,templates/,analysis/,style-guide.md}` (+ corpus sources for that language). Agents, pipeline, validation, build scripts are exam- and language-agnostic (UTF-8 throughout; scoring/timing all read from `exam.yaml`).

## 10. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Paywalls / fetch failures | whitelist with fallbacks; S1 QC gate before authoring |
| Scanned-PDF misreads in analysis | cross-check vs linee guida OVERVIEW; orchestrator spot-checks |
| Wrong answer keys (LLM error) | independent blind solve in fresh context; regenerate on disagreement; ≤2 rounds then draft |
| Ambiguous items | ambiguity flags = failures even when answers agree |
| Chrome PDF quirks | simple print CSS; MD/HTML always downloadable as fallback |
| Copyright | adaptation + attribution; official PDFs gitignored; excerpts within level norms |

## 11. Session success criteria

1. `/genpapers` skill + agents + factory specs committed and usable next session.
2. Today's batch (2026-07-08, A1–C1) generated **through the real pipeline** (agents + gates), validated, built.
3. Site live on GitHub Pages with working PDF downloads.
4. Manifests complete; no official material republished.
