# CILS Factory v2 Phase 2 Source and Paper Model Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make source records and a structured Paper Model the only authoring inputs, then derive student, teacher, key, and gate artifacts without drift.

**Architecture:** Private raw snapshots live under ignored `work/source-cache/`; committed source records retain identity, hashes, limited evidence, rights and adaptation metadata. `paper-model.json` models texts, objective items, evidence, cognition, writing tasks, answers and glossary; deterministic renderers create compatibility Markdown and the blind student projection.

**Tech Stack:** Python 3.11+, JSON/YAML, standard library, PyYAML, existing CILS config/templates.

---

## File map

- Create `scripts/paper_factory/{source_records,paper_model,content_renderer,source_gate,item_quality}.py`.
- Create `factory/schemas/{source-record,paper-model,judgment-report}.schema.json`.
- Modify `factory/exams/cils/exam.yaml` to declare cognition quotas and response capacities for each standard profile/level.
- Modify `factory/validation/checklist.md` and `factory/PIPELINE.md` to define G1–G4 artifacts.
- Add discoverable fixtures/tests under `tests/`.

### Task 1: Source record schema and private-cache boundary

- [ ] Write failing fixtures for a valid record and failures for snippet-only content, missing publisher/URL/accessed/rights, insufficient body, missing digest, path escape, raw text committed outside ignored cache, and unjustified cross-level reuse.
- [ ] Verify RED with `python3 -m unittest tests.test_source_records -v`.
- [ ] Implement `source_records.py` and `source-record.schema.json`; expose intake validation through `paperctl audit --gate g1a`. Add an append-only `source_attempt` event/schema for every acquisition attempt with slot, attempt number, candidate identity, accepted boolean, and stable rejection reason (`snippet_only`, `paywall_stub`, `insufficient_body`, `duplicate_url`, `rights`, `genre`, `cefr`, or `fetch_error`).
- [ ] Add tests proving accepted and rejected candidates are both persisted as events while only accepted records enter `source_intake_digest`; these events are the later metrics source for acceptance/rejection rates and attempt counts.
- [ ] Add `.gitignore` entries for `work/source-cache/` and tests proving source records can reference but never publish raw snapshots.
- [ ] Run GREEN and commit `feat(sources): add provenance and private-cache contracts`.

### Task 2: Structured Paper Model schema and validator

- [ ] Write failing A1–C1 model fixtures covering MC, V/F, matching, sequence links, open cloze, verb cloze, pragmatic MC, transformations, and writing choices.
- [ ] Test IDs, option counts, accepted variants, evidence spans, distractor reasons, cognition tags, scoring units, writing ranges/space, answer notes, samples, expressions, and glossary.
- [ ] Verify RED with `python3 -m unittest tests.test_paper_model -v`.
- [ ] Implement focused model parsing/validation without embedding generated Markdown as the source of truth.
- [ ] Run GREEN and commit `feat(model): define the CILS paper model contract`.

### Task 3: Deterministic content renderer and drift detection

- [ ] Write failing tests that render `paper.md`, `answers.md`, `key.json`, `student-projection.md`, and `pages-data.json` from one model.
- [ ] Assert stable bytes across two renders, exact key coverage, no teacher/source leakage in projection, and `generated_from` digest binding.
- [ ] Add a mutation test that hand-edits each derived file and makes `paperctl audit` fail.
- [ ] Implement `content_renderer.py` for every modeled item type and writing/answer section.
- [ ] Run GREEN and commit `feat(model): render all content artifacts from one model`.

### Task 4: Implement G1a/G1b source gates

- [ ] Write failing source fixtures for paywall/search-result stubs, insufficient text, fact drift, voice/genre drift, rewrite beyond policy, CEFR mismatch, and duplicate sources.
- [ ] Implement deterministic G1a checks and the schema/binding for independently supplied G1b judgment reports.
- [ ] Require G1b to bind `source_intake_digest + content_digest + policy_digest` and include fact/voice/CEFR verdicts per adapted text.
- [ ] Run tests and commit `feat(gates): bind source intake and fidelity evidence`.

### Task 5: Implement complete G2 over the model and generated projections

- [ ] Extend contract mutations to operate on the model: section/prova order, durations, points, scoring units, exact consegne, item/options counts, answer coverage, sample word counts, glossary and response capacity.
- [ ] Verify mutations fail before implementation.
- [ ] Make `paperctl audit --gate g2` validate the model first, regenerate to a temporary directory, compare committed derivatives byte-for-byte, then bind its report to content/policy digests.
- [ ] Run GREEN and commit `feat(gates): validate model contracts and generated derivatives`.

### Task 6: Add G3 blind/adversarial and G4 difficulty/item-quality contracts

- [ ] Add failures for blind mismatch/flag/extra/missing answer, second defensible option, external-knowledge dependence, unsupported cognition tag, duplicate/imbalanced options, answer-position collapse, missing evidence and weak distractors.
- [ ] Add cognition quotas and response capacities to the standard profile for A1–C1; encode them as auditable data, not keywords.
- [ ] Implement deterministic G4a and schema/binding validation for independent adversarial/G4b reports; CI reruns G4a only.
- [ ] Make the legacy `scripts/paper_quality_audit.py` CLI read the same model/G4a implementation and submit any lifecycle event through `paperctl record-stage`; add a regression proving it cannot retain the former keyword-depth heuristic or direct manifest writes.
- [ ] Update blind preparation to copy only `student-projection.md` bytes and never reveal repo paths, sources or keys.
- [ ] Run GREEN and commit `feat(gates): add independent ambiguity and difficulty controls`.

### Task 7: Integrate Phase 2 into `paperctl` and the generation pipeline

- [ ] Add integration tests for `paperctl scaffold --adapter paper-model-v2`, `snapshot`, ordered G1a→G1b→G2→G3→G4 events, stale-report invalidation, two-round repair budget, and draft reasons.
- [ ] Update canonical skill, role prompts, pipeline and checklist to write model/source/judgment reports through `paperctl record-stage`.
- [ ] Explicitly reject `legacy-markdown-v2` for any new session.
- [ ] Extend the PR validation workflow to recompute G0/G2/G4a, recompute source/content/policy/student digests, and validate the schema/executor/report digest/bindings of committed G1a/G1b/G3/G4b reports without network or model calls.
- [ ] Run the entire Phase 1+2 test matrix and commit `feat(factory): make paper-model-v2 mandatory for new sessions`.

### Task 8: Phase 2 integration verification

- [ ] Render all A1–C1 golden fixtures twice and compare bytes.
- [ ] Run all source/model/gate mutation tests and legacy regressions.
- [ ] Confirm private snapshots and Pavia source PDFs are ignored and absent from `git diff`.
- [ ] Run `git diff --check`; commit verification notes only if they add durable evidence.
- [ ] Complete a dedicated Phase 2 review and stacked PR from `codex/factory-v2-phase2` onto the reviewed Phase 1 branch; do not mix Phase 3 renderer work into this PR.

Exact commands for Tasks 1–8 use `python3 -m unittest tests.test_source_records tests.test_paper_model tests.test_content_renderer tests.test_source_gates tests.test_model_contract tests.test_item_quality tests.test_paperctl_model_flow -v`; each task first runs its named module expecting the stated missing behavior, then reruns it expecting `OK`, followed by `python3 -m unittest discover -s tests -t . -v` for regressions.
