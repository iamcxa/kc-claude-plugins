---
title: Provide a portable local-service supervisor
status: backlog
source: GitHub issue #94 — captain fast-track for blocked CarLove E2E
started:
completed:
verdict:
worktree:
issue: 94
pr:
ledger_pr:
pr_artifact_v1:
ledger_artifact_v1:
mod-block:
design:
lane: e2e-pipeline/runtime-hardening
id: s473jqtygr02ytntjexbr17z
---

## Problem

Workers can invent a foreground local-service supervisor using Bash-only `wait -n` while running under macOS zsh. The supervisor fails before browser launch and consumes a valid E2E attempt even though application behavior was never exercised.

## Proposed approach

Provide one executable local-service supervisor with an explicit supported shell/runtime contract, preflight capability checks, owned process/listener evidence, persistent state, and scoped cleanup. Route all service-owning E2E consumers to it instead of prompt-authored shell loops.

## Design determination

`required` — service lifecycle, ownership, and attempt-budget boundaries are executable runtime behavior.

## Acceptance criteria

**AC-1 — Unsupported supervision fails before services or browser attempts start.**
Verified by: a RED/GREEN test with an unsupported shell/capability fixture. Falsified by: starting a child before preflight completes.

**AC-2 — Started services carry durable ownership evidence.**
Verified by: tests for launcher PID, listener ownership, state persistence, and readiness. Falsified by: accepting a live port owned by another process.

**AC-3 — Cleanup stops only owned services and preserves the result receipt.**
Verified by: tests with owned and foreign processes. Falsified by: killing a foreign PID/listener.

**AC-4 — E2E consumers use the shared helper rather than writing `wait -n` supervisors.**
Verified by: cross-consumer contract tests. Falsified by: adding prompt guidance that recreates an ad-hoc foreground supervisor.

## Test plan

Reproduce the zsh `wait -n` failure, add focused RED supervisor tests, verify GREEN on macOS-compatible primitives, then run the full `e2e-pipeline` check.

## Measurement

No dispatch yet.

## Doc diff

Replace ad-hoc local-service supervision guidance with the executable helper contract.

## Out of scope

Browser namespace ownership, application-specific startup commands, and service implementation changes.
