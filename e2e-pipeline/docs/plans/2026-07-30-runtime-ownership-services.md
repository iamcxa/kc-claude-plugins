# Runtime Ownership and Local Services Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Close issues #90 and #94 by making browser-daemon ownership and local-service supervision executable, auditable, and shared across every E2E consumer.

**Architecture:** Extend `e2e-browser-runtime.js` so the first open verifies `agent-browser session info --json`, socket-safe namespace binding, Chrome for Testing process arguments, profile ownership, and `reused=false`, then persists a receipt used by later same-run commands. Add a separate Node-based local-service supervisor driven by a strict JSON manifest; it preflights without starting children, owns process groups, proves listener ownership, persists receipts, and performs scoped cleanup without shell `wait -n`.

**Tech Stack:** Node.js CommonJS, `node:test`, Bash code generation, `agent-browser` 0.32 session diagnostics, `ps`/`lsof` capability probes on macOS/Linux.

### Task 1: Browser ownership RED tests

**Files:**
- Create: `compiler/test/browser-runtime-ownership.test.js`
- Modify: `compiler/test/browser-runtime-contract.test.js`

1. Add a stub `agent-browser` that distinguishes browser commands from `session info --json`.
2. Add a stub process-table command with an exact Chrome for Testing executable/profile row.
3. Assert first open writes a complete ownership receipt and rejects `reused=true`.
4. Assert a later same-run open accepts reuse only when the persisted receipt matches.
5. Assert namespace, session, executable, profile, socket directory, PID, and process-argument mismatches fail closed.
6. Assert long run IDs normalize to distinct socket-safe namespaces.
7. Run the focused tests and confirm RED because receipt/session/process validation is absent.

### Task 2: Browser ownership GREEN implementation

**Files:**
- Modify: `bin/e2e-browser-runtime.js`
- Modify: `references/agent-browser-runtime.json`
- Modify: `compiler/test/browser-runtime.test.js`

1. Add socket-safe namespace derivation and final socket-path validation.
2. Add `--receipt` parsing and a default run/app receipt path.
3. On `open`, read and strictly validate `session info --json`.
4. Read the process table and require one Chrome root process with the requested executable and profile.
5. Require `reused=false` when no receipt exists; validate same-run reuse against the existing receipt.
6. Persist/refresh the receipt atomically and mark it closed after scoped cleanup.
7. Remove inherited socket-directory/browser-binding environment overrides.
8. Run focused browser runtime tests until GREEN.

### Task 3: Route every browser consumer through the runtime

**Files:**
- Modify: `skills/e2e-test/SKILL.md`
- Modify: `skills/e2e-map/SKILL.md`
- Modify: `skills/e2e-walkthrough/SKILL.md`
- Modify: `skills/e2e-walkthrough/reference.md`
- Modify: `skills/e2e-flow/SKILL.md`
- Modify: `agents/e2e-test-runner.md`
- Modify: `agents/e2e-mapper.md`
- Modify: `agents/e2e-flow-verifier.md`
- Modify: `references/commands.md`
- Modify: `references/agent-teams.md`
- Modify: `compiler/compiler.js`
- Modify: `compiler/codegen.js`
- Modify: compiler tests that assert generated browser command text

1. Extend the structural contract test to cover mapper, verifier, walkthrough, flow, and generated scripts.
2. Confirm RED on raw browser lifecycle calls.
3. Add runtime path/run ID/receipt fields to each consumer handoff.
4. Replace raw commands with a declared runtime command prefix.
5. Generate a Bash `agent-browser()` compatibility function that routes existing generated commands through the runtime, maps named sessions to mapping apps, and writes receipts under the result directory.
6. Require compiled callers to provide `E2E_BROWSER_RUNTIME`; generate a fresh run ID when none is supplied.
7. Run consumer/codegen tests until GREEN.

### Task 4: Local-service supervisor RED tests

**Files:**
- Create: `compiler/test/local-service-runtime.test.js`
- Create: `compiler/test/fixtures/local-service-fixture.js`

1. Reproduce zsh `wait -n` failure as a control assertion on macOS.
2. Define a v1 manifest with `command` as argv, absolute `cwd`, host, port, and readiness timeout.
3. Assert preflight rejects shell strings, unsupported platforms/tools, duplicate names/ports, relative paths, and invalid timeouts before starting children.
4. Start a real Node TCP fixture and assert the receipt records supervisor, launcher, process-group, and listener ownership.
5. Start a foreign listener and assert adoption is rejected.
6. Assert status detects drift and stop terminates only owned processes while preserving a final receipt.
7. Run the focused test and confirm RED because the helper does not exist.

### Task 5: Local-service supervisor GREEN implementation

**Files:**
- Create: `bin/e2e-local-service-runtime.js`
- Modify: `package.json`

1. Implement `new-run-id`, `preflight`, `start`, `status`, `stop`, and private `supervise`.
2. Use `spawn` with argv and `shell:false`; never emit or evaluate shell source.
3. Feature-test process groups, `ps`, and `lsof` before starting services.
4. Run one detached supervisor that owns child process groups and writes atomic state.
5. Poll readiness and prove each listener PID belongs to its declared service group.
6. Handle TERM/INT/child exit with bounded scoped cleanup and final receipt updates.
7. Run focused tests until GREEN.

### Task 6: Integrate optional service ownership across consumers

**Files:**
- Modify: the skills, agents, references, compiler, and structural tests listed in Task 3
- Modify: `references/common-patterns.md`

1. Detect an explicit service manifest or `.claude/e2e/services.json`.
2. Preflight/start services before generating or consuming a browser attempt.
3. Pass the service runtime/run ID/state directory through orchestrator handoffs.
4. Stop services only from the owning orchestrator after browser/trace cleanup.
5. Add optional `E2E_SERVICE_MANIFEST`, `E2E_SERVICE_RUNTIME`, and `E2E_SERVICE_STATE_DIR` support to compiled scripts.
6. Assert every consumer references the shared helper and contains no `wait -n` supervisor guidance.
7. Run focused contract/codegen tests until GREEN.

### Task 7: Documentation, findings, and full verification

**Files:**
- Modify: `references/learned-patterns.md`
- Create or update: `.claude/e2e/reports/skill-quality-findings.md` (project-local)
- Modify: relevant docs only if behavior is not already fully described by the consumer/reference edits

1. Record the assumption/reality gaps for daemon receipt schema and macOS shell portability.
2. Record the D1 patterns: session isolation is not daemon ownership; service supervision must be executable and shell-free.
3. Run `npm run lint`.
4. Run focused runtime/contract/codegen tests.
5. Run `npm test` and confirm all tests pass.
6. Run one real isolated Chrome for Testing receipt probe.
7. Run one real local-service start/status/stop probe.
8. Verify git diff is limited to `e2e-pipeline/**`.

### Task 8: Review, PR, and release inclusion

1. Run exact-head code review and resolve all Critical/Important findings.
2. Ask the user to confirm the touched files and commit scope.
3. Stage only explicit `e2e-pipeline/**` paths.
4. Commit using `fix(e2e-pipeline): harden runtime ownership and local services`.
5. Push and open a Draft PR closing #90 and #94.
6. After CI passes, mark Ready and squash-merge.
7. Confirm release-please updates the next `e2e-pipeline` release with the merged fix.
8. Merge the release only when the separate `kc-pr-flow` owner has cleared the shared release gate, then sync local Claude/Codex installs and smoke-check both runtime helpers.

Implementation note: `references/agent-browser-runtime.json` required no
content change. The executable runtime supplies and verifies the namespace,
socket root, engine, executable, profile, and receipt bindings explicitly.
