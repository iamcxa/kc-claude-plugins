---
title: Isolate agent-browser daemon ownership per run
status: backlog
source: GitHub issue #90 — captain fast-track for blocked CarLove E2E
started:
completed:
verdict:
worktree:
issue: 90
pr:
ledger_pr:
pr_artifact_v1:
ledger_artifact_v1:
mod-block:
design:
lane: e2e-pipeline/runtime-hardening
id: rsqcmc9yvrhsf6w9cgrzbnzm
---

## Problem

The pipeline can isolate a browser context while still attaching its first command to another run's `agent-browser` daemon. The browser runtime merged through #96 covers `e2e-test`, trace, and managed-auth paths, but issue #90 remains open until mapper, verifier, walkthrough, and compiler-generated scripts share the same mechanically verified ownership contract.

## Proposed approach

Audit the current `e2e-browser-runtime.js` contract against every consumer, then close only the remaining gaps. Keep namespace, Chrome for Testing executable, profile, session, non-reuse receipt, and cleanup ownership in one executable helper.

## Design determination

`required` — cross-consumer daemon ownership and fail-closed startup are shared runtime behavior.

## Acceptance criteria

**AC-1 — Parallel runs cannot share daemon/session/profile state.**
Verified by: a contract test that launches two fake runtime namespaces and rejects cross-run adoption. Falsified by: removing namespace from any browser command.

**AC-2 — All browser-owning consumers route through one executable helper.**
Verified by: structural contract tests over mapper, runner, verifier, walkthrough, and generated-script surfaces. Falsified by: adding a direct unowned browser lifecycle command.

**AC-3 — Ownership receipts are complete and cleanup is scoped.**
Verified by: runtime tests for namespace, executable, profile, session, `reused=false`, and run-scoped close behavior. Falsified by: accepting an incomplete or mismatched receipt.

## Test plan

Add focused RED contract/runtime tests, run the affected test files, then run the full `e2e-pipeline` check.

## Measurement

No dispatch yet.

## Doc diff

Update consumer instructions only where the executable contract changes their invocation.

## Out of scope

Trace finalization, selector grammar, and application-specific flows.
