# Flow-Managed Authentication Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:test-driven-development to implement this plan task-by-task.

**Goal:** Add a declarative `auth_mode: flow-managed` contract that gives every `/e2e-test` replay a newly absent Chrome for Testing profile, skips runner pre-auth only for that mode, verifies profile binding, preserves the canonical profile, and records cleanup.

**Architecture:** Extend the owned `e2e-browser-runtime.js` seam because it already controls the daemon namespace, session, Chrome executable, and profile launch option. The runtime will reserve an ephemeral profile under its managed home, bind it to one run/app/replay, verify Chrome materialized that exact path, compare a canonical-profile digest before cleanup, and remove only marker-owned profiles. Orchestrator and runner instructions will carry `auth_mode`, canonical/ephemeral paths, and lifecycle results; default flows continue using the canonical persistent profile.

**Tech Stack:** Node.js CommonJS, `node:test`, Markdown skill/agent contracts, YAML fixtures.

## Design decision

Three approaches were considered:

1. Infer login intent from flow steps. Rejected because it is ambiguous and the issue requires a declarative, mechanically testable mode.
2. Let the runner create arbitrary temporary directories. Rejected because the runner cannot prove daemon/profile binding and arbitrary cleanup creates a destructive-path risk.
3. Add `auth_mode: flow-managed` and enforce lifecycle in the owned browser runtime. Selected because the runtime is the single launch-ownership boundary and can fail closed before flow steps.

`auth_mode` accepts only `persistent` (default when omitted) or `flow-managed`. Flow-managed profiles live under `~/.agent-browser/flow-managed/<app>/`, include an ownership record outside the profile directory, and are unique per replay even when a Teams teammate and `browser_run_id` are reused.

### Task 1: Capture the current broken contract

**Files:**
- Create: `compiler/test/fixtures/flow-managed-auth.yaml`
- Create: `compiler/test/flow-managed-auth-contract.test.js`

1. Add a fixture whose first step opens `/auth/login`.
2. Assert the orchestrator recognizes `auth_mode: flow-managed`, generates a replay-specific ephemeral profile, and passes both profile paths to the runner.
3. Assert the runner skips Phase 1d only in flow-managed mode, verifies logged-out state before step 1, and preserves default persistent auth.
4. Assert Teams `RE-RUN` requires a different ephemeral profile.
5. Run `node --test compiler/test/flow-managed-auth-contract.test.js` and capture the expected RED failures.

### Task 2: Implement fail-closed profile lifecycle primitives

**Files:**
- Modify: `bin/e2e-browser-runtime.js`
- Modify: `compiler/test/browser-runtime.test.js`
- Create: `compiler/test/flow-managed-auth-runtime.test.js`

1. Test profile reservation under the managed root, collision rejection, app/run binding, and rejection of arbitrary paths.
2. Test first open requires a previously absent path and post-open Chrome artifacts.
3. Test a simulated daemon that does not materialize the requested profile fails.
4. Test canonical-profile digest comparison and marker-owned cleanup.
5. Implement minimal runtime commands and option parsing to satisfy each test.

### Task 3: Wire the orchestrator and runner contracts

**Files:**
- Modify: `skills/e2e-test/SKILL.md`
- Modify: `agents/e2e-test-runner.md`
- Modify: `references/agent-teams.md`
- Modify: `references/commands.md`

1. Validate `auth_mode` and derive default `persistent`.
2. Prepare one fresh profile per logical run/replay, including same-invocation Teams `RE-RUN`.
3. In flow-managed mode, close the owned session before launch, verify runtime binding before steps, skip pre-auth/auto-login, verify the login route/controls from step 1, and clean up after evidence capture.
4. Record freshness, binding, canonical digest, cleanup status, and profile path in reports and structured summaries.
5. Skip auto-compiled replay for flow-managed auth until the standalone compiler owns an equivalent lifecycle boundary.

### Task 4: Cross-skill impact and documentation

**Files:**
- Modify: `agents/e2e-flow-verifier.md`
- Modify: `skills/e2e-flow/SKILL.md`
- Modify: `skills/e2e-walkthrough/SKILL.md`
- Modify: `skills/e2e-walkthrough/reference.md`
- Modify: `references/common-patterns.md`

1. Make `/e2e-flow` verification honor the declared mode rather than pre-warming a persistent authenticated browser.
2. Make `/e2e-walkthrough` preserve persistent auth by default and document how a generated flow can opt into replay-isolated auth.
3. Document the shared lifecycle, failure modes, and cleanup safety boundary.

### Task 5: Verification

1. Run focused runtime and contract tests.
2. Run `npm run check` from `e2e-pipeline/`.
3. Run `git diff --check`.
4. Inspect status and report all touched files without staging or committing.
