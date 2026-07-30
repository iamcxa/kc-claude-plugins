# Bounded Trace Finalization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Preserve application flow verdicts while bounding trace finalization, rejecting invalid Playwright archives, and keeping cleanup and reporting reachable.

**Architecture:** Route the runner, verifier, and walkthrough through one executable finalizer that supervises the complete trace-stop process group, validates the resulting ZIP, performs bounded recovery after stop failure, and emits an atomic result contract. Consumers gate trace analysis on that contract and report trace infrastructure separately from the application verdict. Persistent Teams flows use a run-keyed lifecycle helper so every full flow or re-run starts and finalizes one fresh trace.

**Tech Stack:** Bash 3.2-compatible shell, Python 3 standard library (`zipfile`), Node.js built-in test runner, Markdown agent/skill protocols.

### Task 1: Prove the finalizer failure boundaries

**Files:**
- Test: `e2e-pipeline/compiler/test/trace-finalization.test.js`
- Create: `e2e-pipeline/scripts/finalize-trace.sh`
- Create: `e2e-pipeline/scripts/validate-trace-archive.py`

1. Add a stubbed `trace stop` that never exits and assert the finalizer returns within the watchdog budget.
2. Run the focused test and verify it fails without the finalizer.
3. Implement process-group supervision, bounded recovery, archive validation, quarantine, and an atomic result contract.
4. Run the focused test and verify the hang, truncated ZIP, unrelated ZIP, unsafe ZIP, and valid Playwright trace cases pass.

### Task 2: Give persistent runners one trace per flow run

**Files:**
- Test: `e2e-pipeline/compiler/test/trace-finalization.test.js`
- Create: `e2e-pipeline/scripts/team-trace-lifecycle.sh`
- Create: `e2e-pipeline/scripts/validate-trace-identifiers.sh`
- Modify: `e2e-pipeline/agents/e2e-test-runner.md`
- Modify: `e2e-pipeline/skills/e2e-test/SKILL.md`

1. Add failing tests for sequential run IDs, duplicate delivery, unsafe identifiers, and fresh traces on `EXECUTE_FLOW` and `RE-RUN`.
2. Implement run-keyed begin/finalize state with idempotent replay.
3. Update runner and orchestrator messages to carry the run identity and finalization result.
4. Accept the browser runtime path, browser run identity, and app as all-or-none argv fields; route
   start, stop, and recovery through the executable without accepting a shell command string.
5. Run the focused contract tests.

### Task 3: Apply shared semantics to verifier and walkthrough

**Files:**
- Test: `e2e-pipeline/compiler/test/trace-finalization.test.js`
- Modify: `e2e-pipeline/agents/e2e-flow-verifier.md`
- Modify: `e2e-pipeline/skills/e2e-flow/SKILL.md`
- Modify: `e2e-pipeline/skills/e2e-walkthrough/SKILL.md`
- Modify: `e2e-pipeline/skills/e2e-walkthrough/reference.md`
- Modify: shared references under `e2e-pipeline/references/`

1. Add failing contract tests that every producer invokes the finalizer, gates analysis, and starts a fresh trace for each persistent full-flow execution.
2. Replace raw trace-stop instructions with the shared result contract.
3. Keep `flow_verdict` independent from stop, validation, recovery, and artifact disposition.
4. Update shared report and command references.
5. Run the focused contract tests.

### Task 4: Verify the recovered branch

**Files:**
- All files listed above.

1. Run `bash -n`, `shellcheck`, and Python bytecode compilation for executable helpers.
2. Run `node --test compiler/test/trace-finalization.test.js`.
3. Run `npm run check` from `e2e-pipeline/`.
4. Run `git diff --check` and audit the exact unstaged file list.
5. Request code review and resolve only technically valid findings.
6. Leave all files unstaged and uncommitted until the user confirms the exact commit scope.
