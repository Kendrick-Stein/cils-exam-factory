# CILS Factory v2 Phase 4 First Full Session Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate, independently validate, seal, clean-build, and prepare publication of the complete 2026-07-10 CILS standard-practice A1–C1 batch.

**Architecture:** Each level has an independent S0–S6 artifact set and repair budget; shared policies are frozen once. Phase 1–3 are separate stacked factory PRs; the paper-release branch is cut from the reviewed Phase 3 head. A retrospective may create a later `codex/factory-improvements-<resolved_session>` PR only when measured failures justify it.

**Tech Stack:** Canonical genpapers skill, `paperctl`, source web access, independent Codex blind solvers/reviewers, headless Chrome/Poppler, git/gh.

---

## Fixed run profile

- Requested session: `2026-07-10`. Before creating any branch or artifact, resolve exactly one `resolved_session`: use `2026-07-10` unless sealed, otherwise the lowest unused immutable `2026-07-10-rN`. Persist it in run metadata and use it everywhere.
- Levels: `A1,A2,B1,B2,C1`.
- Variant: `cils-2024-standard`; sections: reading, structures, writing; no listening/oral.
- Source acquisition: authentic first-party or reputable Italian publishers, unique across levels, complete enough for the target adaptation, with private snapshot hashes and public metadata.
- Success: all five levels pass G0–G5 on the same digests; fewer than five is a diagnostic checkpoint, not completion.

### Task 1: Freeze the release base and scaffold all five levels

- [ ] Verify the Phase 3 factory branch—including the already implemented/tested `paperctl learn`—has green tests/review and fix its commit SHA.
- [ ] Resolve and persist `resolved_session`, then create `codex/papers-<resolved_session>` and its worktree from that exact SHA. Use the same value for paper paths, reports, metrics, PR titles and any optional improvement branch; do not include factory modifications in the release diff relative to its base.
- [ ] Run `paperctl scaffold` for A1–C1, freeze one `policy_digest`, and validate draft ledgers/manifests.
- [ ] Run status and confirm no published tree is being overwritten.

### Task 2: S1 source intake and G1a

- [ ] Perform the web-access prerequisite check and show the automation-risk notice before network access.
- [ ] Acquire sources by independent level/slot groups; every candidate attempt—accepted or rejected—must append the Phase 2 `source_attempt` event with candidate identity and stable reason, while accepted records also include URL, title, publisher, author/date when available, accessed date, body evidence, snapshot digest, rights note, CEFR evidence, genre and adaptation plan.
- [ ] Reject snippets, aggregation without underlying text, paywall stubs and cross-level URL reuse; record each rejection and stop after two attempts per missing slot.
- [ ] Write source records/private snapshots, run `paperctl audit --gate g1a`, and record one hash-bound event per level.

### Task 3: S2 author the Paper Models and derive all content artifacts

- [ ] Author A1–C1 models independently from accepted records and frozen templates/config.
- [ ] Preserve exact counts, scoring units, durations and consegne; include evidence spans, distractor reasons, cognition tags, accepted variants, writing tasks, samples, useful expressions and glossary.
- [ ] Run the deterministic renderer; never hand-edit `paper.md`, `answers.md`, `key.json`, projection or Pages data.
- [ ] Run G1b source-fidelity review and G2 contract audit for each level; route any failures within the shared two-round budget.
- [ ] If fidelity repair replaces a source, count it in the same two-round budget, recompute `source_intake_digest`, rerun G1a, then rerun G1b→G5. If only adaptation changes, start at G1b; if only item/model content changes, start at G1b/G2 as required by the digest dependency graph.

### Task 4: S3/S4 independent blind and adversarial validation

- [ ] For each level run `blind_validation.py prepare` so only isolated student-projection bytes exist in `/tmp`; invoke a fresh read-only solver with no repo/web access.
- [ ] Reconcile mechanically; any mismatch or flag is a failure and the command must exit non-zero.
- [ ] Run an independent adversarial reviewer without the key and an independent G4b item-quality reviewer; run deterministic G4a.
- [ ] Repair only the failing source/adaptation/item/model evidence, regenerate the full artifact set, and rerun from G1a when source identity/snapshot changed, otherwise from G1b/G2 as the dependency graph requires. Stop after two total content repair rounds across all failure categories.

### Task 5: S5/S6 dual rendering and G5

- [ ] Render `exam-booklet`, `answer-sheet`, `teacher-guide`, accessible paper/answers, source and quality pages for each level.
- [ ] Run projection equivalence, PDF geometry/capacity/page-number tests, visual PNG inspection, accessibility/responsive/link tests and level-release digest checks.
- [ ] Fix only session-local content/layout hints inside the model; shared renderer defects go to the factory branch and force a new revision session.
- [ ] Record G5 reports on the same render/release digests.

### Task 6: S7 status, promote, and clean release build

- [ ] Run `paperctl status` and require 5/5 publishable with G0–G5 bindings.
- [ ] Promote/seal each level; verify any subsequent session-tree write is rejected.
- [ ] Clean-build into an empty `_site`, compare stable level digests, include only fixed legacy files, assemble index/session pages, and validate site closure.
- [ ] Copy a local preview to `docs/` only as a convenience; `_site`/CI remains publishing authority.

### Task 7: Independent final review and core release PRs

- [ ] Run full unit/fixture/mutation/skill test suite, five-level status table, clean rebuild, link check, PDF inspection and `git diff --check`.
- [ ] Run the already-reviewed `paperctl learn --session <resolved_session> --out reports/<resolved_session>` from the frozen factory base; verify its schema covers all §13 metrics and that it writes outside the sealed session tree.
- [ ] Obtain final spec-compliance and code-quality reviews for factory code and a separate content/quality review for the five-paper release.
- [ ] Commit only sealed paper/report files on the release branch; push factory and stacked release branches.
- [ ] Open/verify the three stacked Phase 1–3 factory PRs and a separate Paper Release PR from `codex/papers-<resolved_session>`; retarget the release PR after the factory stack merges. Do not open or report an Improvement PR yet, and do not auto-merge any PR.

### Task 8: Conditionally execute a retrospective Factory Improvement PR

- [ ] If `metrics.json` contains no justified proposal, record `improvement_pr: none` in the retrospective and skip every remaining step in this task.
- [ ] Otherwise create a fresh `codex/factory-improvements-<resolved_session>` worktree from the reviewed Phase 3 factory head, never from or inside the paper-release worktree. Until the factory stack merges, set the Improvement PR base to `codex/factory-v2-phase3`; after merge it may be rebased/retargeted to `main`.
- [ ] For each selected proposal, first write a failing automated test that reproduces its cited failure ID and run it to verify the expected RED; proposal metadata alone is not sufficient.
- [ ] Implement the minimal factory/skill/config/renderer correction, run the targeted test GREEN, then run all unit, mutation, golden, visual, skill-entrypoint and clean-build regressions applicable to the changed subsystem.
- [ ] Verify the diff contains no files under `papers/<resolved_session>/`, no sealed artifact/report edits, and no Paper Release commits; obtain spec-compliance and code-quality approval.
- [ ] Commit, push and open the Improvement PR with failure IDs, RED/GREEN evidence and test results. Do not merge automatically and do not use the change to re-sign the current session.

### Task 9: Final publication handoff report

- [ ] Report level status, objective items, blind agreement, repair rounds, local artifact links, the Phase 1–3 factory PR links, Paper Release PR link, optional Improvement PR link or explicit `none`, and the exact merge/deployment condition for GitHub Pages.
