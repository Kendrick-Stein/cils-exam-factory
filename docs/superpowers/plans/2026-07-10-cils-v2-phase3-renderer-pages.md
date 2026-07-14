# CILS Factory v2 Phase 3 Dual Renderer and Pages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce exam-realistic printable booklets/answer sheets/teacher guides and a modern accessible Pages site from the same Paper Model, with a deterministic G5 render gate.

**Architecture:** Stable per-level artifacts are rendered before promote and hashed as `level_release_digest`; lifecycle-dependent index/session pages are assembled only after promote and hashed in `site_closure_digest`. Print templates use official-inspired structure without CILS marks, barcodes or copied artwork.

**Tech Stack:** Python, Markdown, semantic HTML/CSS, one digest-pinned Linux OCI render image containing exact Playwright/Chromium, Axe, Poppler and font versions, executed identically from macOS development and GitHub Actions.

---

## File map

- Create `scripts/paper_factory/{print_renderer,answer_sheet,site_renderer,render_gate,pdf_tools}.py`.
- Create `infra/render/Dockerfile`, `factory/render/toolchain.lock.json`, and `scripts/render_in_container.py`. The lock records the base-image digest, built render-image digest, Playwright/Chromium/Axe/Poppler versions, font file hashes and renderer schema.
- Create `scripts/templates/{exam-booklet,answer-sheet,teacher-guide,level,sources,quality,session,index}.html`.
- Replace/extend `scripts/assets/{paper,site}.css`; add print-specific CSS tokens.
- Extend `tests/fixtures/render/`, `tests/test_print_renderer.py`, `tests/test_answer_sheet.py`, `tests/test_teacher_guide.py`, `tests/test_pages_renderer.py`, `tests/test_render_gate.py`.
- Modify `scripts/build_site.py`, `scripts/paperctl.py`, and Pages workflow.

### Task 1: Establish render golden fixtures and print tokens

- [ ] Write RED tests for A4 size, high-contrast print palette, embedded level/session footer, page-number placeholder, response-line geometry, explicit continuation pages, and no official marks/barcodes/privacy fields.
- [ ] Implement shared print tokens and HTML shell templates.
- [ ] Render representative A1, B1 and C1 fixture pages; inspect PNG output against Pavia-derived rubric without copying source visuals.
- [ ] Run GREEN and commit `feat(render): add official-inspired print foundations`.

### Task 2: Render `exam-booklet.pdf`

- [ ] Write failing tests for cover/section dividers, exact student projection equivalence, text/options/order, centralized scoring, A4/page count/footer/page numbering, no clipping/table breaks/unintended blank pages, and writing line capacity `ceil(max_words/7)`.
- [ ] Implement `print_renderer.py` and browser export inside the render container; container/image/browser/CSS/font/runtime versions enter `render_digest`.
- [ ] Build or pull the exact same digest-pinned Linux image locally and in CI; all pre-promote candidate and post-promote replay commands must go through `scripts/render_in_container.py`, never host Chrome. Add RED/GREEN tests where a changed image digest, Playwright/Axe/Poppler version, lock value or font byte invalidates `render_digest` before rendering.
- [ ] Add B1/B2 sequence and C1 transformation visual fixtures; require C1 response lines ≥3×90 mm.
- [ ] Run GREEN and commit `feat(render): build paginated exam booklets`.

### Task 3: Render `answer-sheet.pdf`

- [ ] Write failing tests that atomically map every scoring unit to OMR, V/F, matching/sequence boxes, fixed-capacity character cells, or open-response lines.
- [ ] Ensure character-cell capacity comes from profile data, never correct-answer length; sequence scoring uses links, not fragment count.
- [ ] Implement `answer_sheet.py`, candidate identity placeholders without personal data, and unbranded optical-style controls.
- [ ] Run GREEN and commit `feat(render): generate usable standalone answer sheets`.

### Task 4: Render `teacher-guide.pdf`

- [ ] Write failing tests for complete keys, evidence spans, distractor reasons, Chinese notes, accepted variants, sample word ranges, useful expressions, glossary and student/teacher separation.
- [ ] Implement teacher guide template and PDF export; keep solutions out of booklet and answer sheet.
- [ ] Run GREEN and commit `feat(render): generate evidence-rich teacher guides`.

### Task 5: Build the modern Pages information architecture

- [ ] Write failing semantic/accessibility tests for index, session, level, paper, answers, sources and quality pages; answer reveal must require an explicit action.
- [ ] Implement 44×44 px controls, AA colors, visible focus, correct page `lang`, responsive layouts at 375/768/1280 px, no horizontal overflow, meta description/canonical/Open Graph and print/download links.
- [ ] Keep per-level pages lifecycle-stable and show only G0–G4 report IDs/digests; assemble published/G5 status in post-promote index/session pages.
- [ ] Add source summaries without raw text and confidence labels for A1/A2 standard evidence.
- [ ] Run GREEN and commit `feat(site): redesign Pages for practice and provenance`.

### Task 6: Implement deterministic G5 and release closure

- [ ] Write RED tests for missing/undersized PDFs, non-A4 pages, missing page numbers/footer, clipping/overflow, insufficient response capacity, broken links, accessibility failures, projection divergence and output tampering.
- [ ] Implement the **pre-promote candidate path first**: `paperctl build --candidate --session ... --level ...` invokes the locked Linux render container, renders stable per-level outputs outside the session tree while status remains draft, computes `render_digest`/`level_release_digest`, runs deterministic G5, and records the hash-bound report through `paperctl record-stage`. This is the G5 evidence required before `promote` and breaks the lifecycle cycle.
- [ ] Implement `render_gate.py`; hash stable per-level files as `level_release_digest`, normalize PDF metadata or use pixel hashes, and keep session/index outside that digest.
- [ ] Implement the distinct **post-promote replay path** in the identical image digest: clean-build from an empty directory, compare stable per-level digest or normalized PDF pixel hashes to the pre-promote candidate, assemble legacy/index/assets, and calculate exact `site_closure_digest`.
- [ ] Extend CI with a PR-safe validation/build job that installs the lock, runs unit/fixture/mutation/skill tests, validates G1/G3/G4b bindings, recomputes G0/G2/G4a/G5 and model outputs, and clean-builds `_site`; keep deploy as a separate main-only job consuming that validated artifact.
- [ ] Run two clean builds and tamper tests; commit `feat(gates): seal rendered levels and site closure`.

### Task 7: Implement retrospective metrics and `paperctl learn` before the release fork

- [ ] Write RED schema/golden tests for every §13 metric: source attempts/acceptance/rejection reasons, freshness/genre/CEFR/rewrite per slot, initial/final blind agreement, flags, repair rounds, cognition and answer-position distributions, failure IDs, render/a11y results, publishable/draft reasons, and zero-or-more evidence-linked improvement proposals.
- [ ] Implement `paperctl learn --session <resolved_session> --out reports/<resolved_session>` as a read-only aggregator over ledgers/gate/render reports. It writes `metrics.json` plus `retrospective.md` outside the sealed session tree and never edits current artifacts, policy, skill or lifecycle state.
- [ ] Add a golden with no justified improvement and assert it emits an empty proposal list; add another with a repeated failure ID and assert a minimal tested proposal is emitted.
- [ ] Run `python3 -m unittest tests.test_learning_metrics -v` RED then GREEN, followed by the complete suite; commit `feat(factory): add evidence-bound retrospective metrics` before fixing the Phase 3 release-base SHA.

### Task 8: Phase 3 visual and regression verification

- [ ] Use the PDF inspection workflow to render representative booklet, answer sheet and teacher guide pages to PNG and inspect original resolution.
- [ ] Run all Phase 1–3 tests plus legacy site compatibility.
- [ ] Run local site in the in-app browser; verify navigation, answer reveal, responsive viewports, download links and source/quality pages.
- [ ] Record any content-driven layout repair as model hints, never ad-hoc post-render edits.
- [ ] Run `git diff --check` and commit final Phase 3 fixes with their RED regressions.
- [ ] Complete a dedicated Phase 3 review and stacked PR from `codex/factory-v2-phase3` onto the reviewed Phase 2 branch. Freeze its reviewed head as the only base for the paper-release branch.

Exact commands: each task first runs its named module (`tests.test_print_renderer`, `tests.test_answer_sheet`, `tests.test_teacher_guide`, `tests.test_pages_renderer`, `tests.test_render_gate`) and expects a missing-rule failure; after implementation it must report `OK`, then `python3 -m unittest discover -s tests -t . -v` must remain green. Numeric assertions include usable writing width ≥150 mm, baseline spacing ≥8 mm, C1 transform lines ≥90 mm, every font embedded, every page A4, and every interactive target ≥44×44 px.
