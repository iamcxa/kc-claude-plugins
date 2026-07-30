# E2E Browser Runtime Isolation

## Design

`e2e-pipeline` browser runners must not call the global `agent-browser` daemon
directly. The shared `bin/e2e-browser-runtime.js` command owns browser startup and
forwards each operation with:

- a daemon namespace derived from a per-invocation `browser_run_id`;
- an app session derived from the mapping's `app`;
- an explicit Chrome for Testing executable;
- a controlled agent-browser config with inherited auto-connect, CDP, and remote
  provider settings removed.

The `/e2e-test` orchestrator generates one run ID before dispatch. All teammates
and subagents in that invocation receive the same runtime path and run ID. A
same-invocation team re-run keeps the ID and browser. A fresh invocation generates
a new ID, shuts down and deletes any prior `e2e-test` team, then creates new
members with the complete invocation state. A runner rejects a different run ID
instead of partially switching browser ownership.

The runtime rejects unsafe identities, unavailable or non-Chrome-for-Testing
executables, and protected attachment flags. It also uses a top-level command
allowlist derived from the e2e-test runner and canonical command reference, so
nested command interpreters such as `batch` (including argv and stdin programs),
`chat`, `mcp`, and `plugin` are rejected before `agent-browser` is launched.

This slice integrates the primary `/e2e-test` and `e2e-test-runner` path. Compiler,
mapper, flow verifier, walkthrough, debug observer, and UI verification remain
follow-up consumers because their lifecycle and packaging contracts differ.

## Implementation Plan

1. Add focused Node tests for namespace, executable, environment, cleanup, and
   run-ID behavior.
2. Implement the runtime command with fail-closed validation.
3. Add contract tests for orchestrator-to-runner propagation.
4. Route the e2e-test runner instructions and canonical command reference through
   the runtime.
5. Run focused tests, a real isolated browser probe, and the full npm check.
