# CILS Factory v2 Phase 1 Trust Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the hash-bound lifecycle, deterministic contract gate, clean deploy boundary, and canonical command/skill surface required before any new v2 paper can be authored.

**Architecture:** `scripts/paper_factory/` owns normalized data, hashes, ledger events, gate reports, lifecycle decisions, and site-closure validation. `scripts/paperctl.py` is the only lifecycle writer. Existing standalone scripts become compatibility adapters around this package while historical publications are admitted only through a fixed legacy registry.

**Tech Stack:** Python 3.11+, standard library, PyYAML, Markdown, unittest-style executable fixtures, GitHub Actions.

---

## File map

- Create `scripts/paper_factory/{__init__,errors,io,hashing,schemas,ledger,inventory,contract,lifecycle,legacy}.py`: focused trust-foundation modules.
- Create `scripts/paperctl.py`: seven-command CLI (`scaffold`, `snapshot`, `record-stage`, `audit`, `status`, `promote`, `build`).
- Create `factory/schemas/{manifest-v2,gate-report,artifact-inventory}.schema.json`: documented v2 contracts used by custom deterministic validators.
- Create `factory/legacy-registry.json`: immutable hashes for the three existing published sessions and their deployed files.
- Create `tests/`: discoverable unit/mutation/CLI fixtures; preserve existing `scripts/test_*.py` entrypoints.
- Modify `scripts/{blind_validation,format_audit,paper_quality_audit,paper_status,build_site}.py`: compatibility delegation and fail-fast behavior.
- Modify `.github/workflows/pages.yml`: test and clean-build the deploy artifact instead of uploading committed `docs/` blindly.
- Track `.agents/skills/genpapers/SKILL.md`; make `.codex`, `.claude` wrappers thin and valid.

### Task 1: Establish a discoverable test harness and package boundary

**Files:**
- Create: `scripts/paper_factory/__init__.py`
- Create: `scripts/paper_factory/errors.py`
- Create: `tests/__init__.py`
- Create: `tests/test_package_boundary.py`
- Create: `scripts/check_test_discovery.py`
- Modify: `scripts/README.md`

- [ ] **Step 1: Write a non-test-named discovery smoke script** at `scripts/check_test_discovery.py` that runs `python3 -m unittest discover -s tests -t . -p 'test_*.py'`, asserts at least one repo-local real test is executed, and imports `scripts.paper_factory`. Keeping the smoke script outside the `test_*.py` pattern prevents recursive self-discovery.
- [ ] **Step 2: Run it and verify RED** with `python3 scripts/check_test_discovery.py`; expected failure is the missing repo-local `tests/` package/test count, never recursive process creation.
- [ ] **Step 3: Add the minimal package, one real discoverable test, and documented canonical test command.** `tests/test_package_boundary.py` imports the package and asserts its public exception types; define `FactoryError`, `SchemaError`, `LifecycleError`, and `GateError` in `errors.py` only.
- [ ] **Step 4: Run GREEN** with `python3 -m unittest discover -s tests -v` and the six legacy executable tests.
- [ ] **Step 5: Commit** `test: establish discoverable factory test harness`.

### Task 2: Add canonical hashing, schema validation, and the explicit legacy registry

**Files:**
- Create: `scripts/paper_factory/io.py`
- Create: `scripts/paper_factory/hashing.py`
- Create: `scripts/paper_factory/schemas.py`
- Create: `scripts/paper_factory/legacy.py`
- Create: `factory/schemas/manifest-v2.schema.json`
- Create: `factory/schemas/gate-report.schema.json`
- Create: `factory/schemas/artifact-inventory.schema.json`
- Create: `factory/legacy-registry.json`
- Create: `tests/test_hashing_and_legacy.py`

- [ ] **Step 1: Write failing tests** for canonical JSON bytes, SHA-256 file hashing, safe relative paths, required v2 manifest fields, rejection of generic legacy fallback, registry missing/extra/hash drift, and registry entries for every currently published level/deployment set.
- [ ] **Step 2: Verify RED** with `python3 -m unittest tests.test_hashing_and_legacy -v`; expected failures are missing modules and registry.
- [ ] **Step 3: Implement minimal deterministic helpers.** Canonical JSON is UTF-8, sorted keys, compact separators, trailing newline; registry validation rejects paths outside the repo and any file not exactly listed.
- [ ] **Step 4: Generate the initial registry deterministically** from tracked historical sessions once, then commit the resulting fixed hashes; the runtime must validate, never auto-enroll legacy files.
- [ ] **Step 5: Run GREEN** plus a mutation that changes one byte in a copied legacy file and proves validation fails.
- [ ] **Step 6: Commit** `feat(factory): add schemas and fixed legacy registry`.

### Task 3: Implement ledger, artifact inventories, and lifecycle CLI basics

**Files:**
- Create: `scripts/paper_factory/ledger.py`
- Create: `scripts/paper_factory/inventory.py`
- Create: `scripts/paper_factory/lifecycle.py`
- Create: `scripts/paperctl.py`
- Create: `tests/test_paperctl_lifecycle.py`

- [ ] **Step 1: Write failing CLI tests** for `scaffold`, `snapshot`, `record-stage`, and `status`: safe session/level names, schema v2 draft manifest, frozen `policy_digest`, monotonic append-only JSONL, normalized `legacy-markdown-v2` inventory, and computed—not stored—`publishable`.
- [ ] **Step 2: Verify RED** by invoking each command through `subprocess.run`; expect missing CLI/subcommands.
- [ ] **Step 3: Implement the minimal CLI and modules.** `scaffold` refuses any existing published tree; `snapshot` inventories the exact adapter file set; `record-stage` verifies prior event hash and monotonic stage/repair rules; `status` is read-only JSON plus concise text.
- [ ] **Step 4: Add tamper tests** proving a one-byte change to `paper.md`, `answers.md`, `key.json`, or `sources.md` changes `content_digest` and invalidates reports bound to the old digest.
- [ ] **Step 5: Run GREEN** with `python3 -m unittest tests.test_paperctl_lifecycle -v`.
- [ ] **Step 6: Commit** `feat(factory): add paperctl lifecycle and hash inventories`.

### Task 4: Replace the hollow format check with a normalized G2 contract gate

**Files:**
- Create: `scripts/paper_factory/contract.py`
- Create: `tests/fixtures/contracts/` passing A1–C1 fixtures
- Create: `tests/test_contract_mutations.py`
- Modify: `scripts/format_audit.py`
- Modify: `scripts/blind_validation.py`
- Modify: `scripts/paper_quality_audit.py`

- [ ] **Step 1: Write one failing mutation per checklist rule:** front matter, order, duration, points/scaling, item/options count, exact normalized consegna, source leakage, language/placeholders, atomic IDs/key coverage, answers explanations, writing samples/word counts/useful expressions, glossary shape, source fields, and status/stage consistency.
- [ ] **Step 2: Verify RED** and record that the old passing fixture is insufficient.
- [ ] **Step 3: Implement a shared normalized parser** that derives the expected contract from `exam.yaml` plus the level template and compares the actual Markdown/key/manifest package. Do not accept a report based only on file presence or heading counts.
- [ ] **Step 4: Make `format_audit.py` delegate to the contract gate** while retaining its CLI. Gate reports include `report_id`, `content_digest`, `policy_digest`, issues, and report digest.
- [ ] **Step 5: Change reconcile failure to non-zero** and add tests for mismatch, ambiguity flag, extra/missing answer, and atomic sequence scoring.
- [ ] **Step 6: Close every legacy write path.** Add subprocess tests proving `blind_validation.py --write-manifest`, `format_audit.py --write-manifest`, and `paper_quality_audit.py --write-manifest` cannot edit lifecycle state directly: each must delegate a validated event to `paperctl record-stage` or reject the option. In Phase 1, `paper_quality_audit.py` is a fail-fast/report-binding compatibility adapter for legacy quality evidence; the model-based G4a implementation is intentionally deferred to Phase 2 Task 6.
- [ ] **Step 7: Run GREEN** for new tests and `scripts/test_{format_audit,blind_validation,paper_quality_audit}.py`.
- [ ] **Step 8: Commit** `feat(factory): enforce complete hash-bound contract gate`.

### Task 5: Add promote/seal and published-tree write protection

**Files:**
- Modify: `scripts/paper_factory/lifecycle.py`
- Modify: `scripts/paperctl.py`
- Modify: `scripts/paper_status.py`
- Create: `tests/test_promote_and_write_guard.py`

- [ ] **Step 1: Write failing tests** for common digest binding across G1b/G2/G3/G4/G5, missing/stale report rejection, repair budget, publishable computation, `promote` draft-only behavior, seal digest creation, and every lifecycle write refusing a published tree.
- [ ] **Step 2: Verify RED** against current CLI.
- [ ] **Step 3: Implement minimal promote and guards.** The seal fixes inventory/report digests; status reads it; no command may reopen or mutate published content.
- [ ] **Step 4: Keep `paper_status.py` as a read-only compatibility wrapper** around the same predicate so old and new entrypoints cannot disagree.
- [ ] **Step 5: Run GREEN** and a post-audit tamper scenario that must block both status and promote.
- [ ] **Step 6: Commit** `feat(factory): seal publishable papers and guard published trees`.

### Task 6: Make site builds clean, atomic, and closure-checked

**Files:**
- Modify: `scripts/build_site.py`
- Modify: `.github/workflows/pages.yml`
- Modify: `scripts/assets/site.css`
- Create: `tests/test_clean_build_closure.py`
- Modify: `scripts/test_build_site.py`

- [ ] **Step 1: Write failing tests** for published-to-draft removal, deleted manifest removal, polluted output removal, PDF failure non-zero, cache invalidation by CSS/renderer/browser version, and exact closure (`sealed v2 + registry legacy + generated assets/index`).
- [ ] **Step 2: Verify RED** against the current incremental builder.
- [ ] **Step 3: Build into a sibling temporary directory**, validate every required artifact, then atomically replace the requested output. Never copy arbitrary prior output.
- [ ] **Step 4: Add `paperctl build` delegation** and closure report/digest. `--no-pdf` is preview-only and cannot satisfy release G5.
- [ ] **Step 5: Split Pages workflow at Phase 1.** Trigger on both `pull_request` and `main`; create a PR/main `validate` job that installs dependencies, runs tests/audits, clean-builds into `_site`, validates closure, and uploads a non-deploy build artifact. Create a separate `deploy` job guarded by `github.event_name == 'push' && github.ref == 'refs/heads/main'`, depending on `validate`, and upload/deploy only that validated `_site`. A PR must never receive Pages write/id-token permissions or call `deploy-pages`.
- [ ] **Step 6: Add workflow-structure tests** that fail if pull requests have no validation path, if deploy lacks the main-only guard, or if committed `docs/` is uploaded directly.
- [ ] **Step 7: Run GREEN** and two consecutive clean builds to verify deterministic HTML/MD/CSS.
- [ ] **Step 8: Commit** `feat(site): deploy only clean closure-checked builds`.

### Task 7: Consolidate the canonical skill and compatibility wrappers

**Files:**
- Track/Modify: `.agents/skills/genpapers/SKILL.md`
- Modify: `.codex/skills/make-paper/SKILL.md`
- Modify: `.claude/skills/genpapers/SKILL.md`
- Modify: `.claude/commands/genpapers.md`
- Modify: `AGENTS.md`
- Modify: `CLAUDE.md`
- Modify: `factory/PIPELINE.md`
- Modify: `scripts/test_agent_entrypoints.py`

- [ ] **Step 1: Capture three RED skill-pressure baselines** using the old skill in isolated fixture repos: (a) a blind output mismatch must stop at draft without exposing key/source files, (b) a stale digest after audit must block promote, and (c) a published same-day session must select `-rN` and prepare separate Release/Improvement scopes. Save prompts and machine-checkable outcomes under `tests/fixtures/skill-scenarios/`.
- [ ] **Step 2: Add RED entrypoint tests** for all wrappers on a case-sensitive copied tree; assert no nonexistent companion/cache path, no `.Codex` case drift, canonical CLI discoverability, blind isolation wording, and promote/build gates. Run `python3 scripts/test_agent_entrypoints.py`; expected failure names the broken `.agents` companion/canonical references.
- [ ] **Step 3: Rewrite one canonical skill** to contain orchestration judgment and `paperctl` commands only; reduce other surfaces to thin pointers that name the canonical tracked path and pipeline.
- [ ] **Step 4: Update repo instructions** so S0–S7 lifecycle writes go through `paperctl` and new sessions cannot use legacy fallback.
- [ ] **Step 5: Forward-run the exact same three scenarios** and assert blind isolation, draft stop, digest rejection, immutable revision naming, and PR-scope separation now pass; static text assertions alone are insufficient.
- [ ] **Step 6: Run GREEN** for entrypoint tests, scenario runner, and `python3 scripts/paperctl.py --help`.
- [ ] **Step 7: Commit** `feat(skills): make genpapers the canonical paper factory entrypoint`.

### Task 8: Phase 1 integration verification

- [ ] Run `python3 -m unittest discover -s tests -v` and all `scripts/test_*.py` entrypoints.
- [ ] Run `python3 scripts/paperctl.py status` against synthetic v2 fixtures and validate historical sessions through `factory/legacy-registry.json` without modifying them.
- [ ] Run mutation matrix for content, report, lifecycle, output, and legacy tampering.
- [ ] Run `git diff --check` and review only intended tracked files; preserve `.superpowers/` and unrelated local settings.
- [ ] Commit plan checkbox updates as `docs: record CILS v2 phase 1 verification`.
- [ ] Complete a dedicated Phase 1 code review and PR from `codex/cils-factory-v2`; require the new `validate` job, while confirming no Pages deployment is attempted from the PR.
