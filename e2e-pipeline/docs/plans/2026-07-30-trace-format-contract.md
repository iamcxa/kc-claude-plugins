# Trace Format Contract Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make `agent-browser` trace producer capability explicit before capture, validate the
actual artifact format after bounded finalization, and analyze Chrome Trace Event JSON without
passing it to the Playwright ZIP validator.

**Architecture:** A Node CLI performs pre-capture feature detection and returns one strict trace
contract. The shared finalizer records the declared and detected formats, selects a format-specific
validator, and preserves the application verdict on any mismatch. A dependency-free streaming
Python validator/summarizer handles Chrome trace JSON while the existing hardened ZIP path remains
unchanged for runtimes that can actually produce Playwright archives.

**Tech Stack:** Node.js built-ins, Bash 3.2, Python 3 standard library, `node:test`, Markdown agent
contracts.

### Task 1: Pre-capture Capability Contract

**Files:**
- Create: `bin/e2e-trace-contract.js`
- Create: `compiler/test/trace-contract.test.js`
- Modify: `package.json`
- Modify: `package-lock.json`

1. Write failing tests with fake `agent-browser` executables for Chrome DevTools JSON,
   Playwright ZIP, and unknown trace help.
2. Run `node --test compiler/test/trace-contract.test.js` and verify RED because the CLI is
   missing.
3. Implement strict version/help probing. Emit `producer`, `producer_version`,
   `declared_format`, `extension`, `validator`, and `analyzer` as JSON.
4. Fail closed for unrecognized capability before any `trace start`.
5. Add the executable to package and lockfile bin maps.
6. Run the focused test and verify GREEN.

### Task 2: Bounded Chrome Trace Validation and Summary

**Files:**
- Create: `scripts/validate-chrome-trace.py`
- Create: `compiler/test/fixtures/chrome-trace-event.json`
- Create: `compiler/test/chrome-trace-validator.test.js`

1. Add a small fixture derived from a real `agent-browser 0.32.0` owned Chrome for Testing
   capture.
2. Write failing tests for valid Chrome JSON, malformed JSON, a Playwright ZIP mismatch, event
   limits, and bounded summary output.
3. Run `node --test compiler/test/chrome-trace-validator.test.js` and verify RED because the
   validator is missing.
4. Implement a streaming top-level `traceEvents` parser with file, event-count, event-size, and
   elapsed-time limits.
5. Implement `validate`, `detect`, and `summarize` commands without third-party dependencies.
6. Run the focused test and verify GREEN.

### Task 3: Format-aware Shared Finalization

**Files:**
- Modify: `scripts/finalize-trace.sh`
- Modify: `compiler/test/trace-finalization.test.js`

1. Extend the finalizer test helper with explicit producer, version, and declared format.
2. Write failing integration tests proving:
   - a real Chrome JSON fixture is accepted by the Chrome validator;
   - a real Playwright ZIP fixture remains accepted by the ZIP validator;
   - JSON declared as ZIP is detected as a mismatch and never reaches the ZIP validator;
   - mismatched extensions fail before `trace stop`;
   - the result records producer, declared format, detected format, validator, and eligibility.
3. Run the focused finalization tests and verify RED.
4. Add `--trace-producer`, `--trace-producer-version`, and `--trace-format`.
5. Reject extension mismatches before stop with bounded close recovery.
6. Detect the produced artifact after stop, quarantine mismatches, and select only the matching
   validator.
7. Preserve existing timeout, recovery, quarantine, atomic result, and application-verdict
   semantics.
8. Run the focused finalization tests and verify GREEN.

### Task 4: Persistent Teams Runtime Integration

**Files:**
- Modify: `scripts/team-trace-lifecycle.sh`
- Modify: `compiler/test/trace-finalization.test.js`

1. Write failing tests proving capability detection precedes `trace start`, Chrome capability uses
   `trace.json`, and the declared contract survives begin/finalize replay.
2. Run the focused lifecycle tests and verify RED.
3. Invoke `e2e-trace-contract` before capture, persist its fields in lifecycle state, derive the
   artifact extension, and pass the exact contract to the finalizer.
4. Run the focused lifecycle tests and verify GREEN.

### Task 5: Runner, Verifier, Walkthrough, and Analyzer Contracts

**Files:**
- Modify: `agents/e2e-test-runner.md`
- Modify: `agents/e2e-flow-verifier.md`
- Modify: `agents/e2e-trace-analyzer.md`
- Modify: `skills/e2e-test/SKILL.md`
- Modify: `skills/e2e-flow/SKILL.md`
- Modify: `skills/e2e-flow/reference.md`
- Modify: `skills/e2e-walkthrough/reference.md`
- Modify: `references/commands.md`
- Modify: `references/common-patterns.md`
- Modify: `compiler/test/trace-finalization.test.js`

1. Add failing structural tests requiring every active producer to detect capability before
   `trace start`, use the contract-derived extension, and pass the declared format to finalization.
2. Add failing analyzer contract tests for separate Playwright and Chrome branches.
3. Run the structural tests and verify RED.
4. Update each active producer contract to use the shared detector and propagate producer,
   version, format, artifact path, validator, and analysis scope.
5. Extend the analyzer instructions so Playwright retains API/console analysis while Chrome uses
   bounded performance summary output and never claims API/console cleanliness.
6. Update report fields and artifact ignore guidance for both `.zip` and `.json`.
7. Run the structural tests and verify GREEN.

### Task 6: Verification and Handoff

1. Run focused trace contract, validator, and finalization tests.
2. Run `npm test`.
3. Run changed-file Biome lint and the full lint command.
4. Run `git diff --check`.
5. Run `npm pack --dry-run --json` and confirm both executables and validators are packaged.
6. Inspect the exact diff against `origin/main` and perform a fix-first review.
7. Present the exact touched-file list and proposed
   `fix(e2e-pipeline): align trace producer and artifact formats` commit for user confirmation
   before staging.
