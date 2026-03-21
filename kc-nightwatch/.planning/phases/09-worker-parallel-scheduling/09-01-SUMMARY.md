---
phase: 09-worker-parallel-scheduling
plan: "01"
subsystem: worker
tags: [bun, ipc, concurrency, queue, map, worker]

# Dependency graph
requires:
  - phase: 08-schema-safety-foundation
    provides: flat active: Run[] IPC shape, activeRun→activeRuns groundwork
provides:
  - Per-target queue isolation using Map<string, Run[]> (targetQueues) and Map<string, Run> (activeRuns)
  - processTarget(targetName) — independent per-target drain loop
  - __all__ expansion routing into per-target concurrent sub-runs
  - Queue depth 1 enforcement with trigger-aware rejection (manual=reject, interval=skip)
  - Cancel that searches all target queues
affects: [10-auto-action, scheduler-per-target]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Per-target Map isolation: Map<targetName, Run[]> + Map<targetName, Run> for concurrent execution"
    - "processTarget idempotency guard: has(targetName) → return early"
    - "Recursive enqueue for __all__ expansion: each sub-run routes through per-target logic"
    - "Trigger-aware queue overflow: interval=silent skip, manual=reject with run:failed IPC"

key-files:
  created: []
  modified:
    - app/worker/index.ts
    - app/tests/worker/queue.test.ts

key-decisions:
  - "Queue depth 1 per target (D-04): max 1 active + 1 queued per target — prevents pile-up without blocking other targets"
  - "Manual trigger rejected with run:failed IPC (D-05): client gets visible feedback when target queue is full"
  - "Interval trigger silently skipped (D-06): scheduler pile-up prevention — no error noise for expected scheduling behavior"
  - "__all__ expands at enqueue time via recursive per-target routing (D-01/D-02): concurrent sub-runs, total time = max not sum"
  - "No IPC shape changes needed (D-07): sendState() collecting from activeRuns.values() already satisfies flat active: Run[] contract"

patterns-established:
  - "Per-target Map isolation: independent queues and active slots per target prevent cross-target blocking"
  - "processTarget idempotency: called freely without double-processing risk — has() guard returns immediately if already running"

requirements-completed: [PARA-01]

# Metrics
duration: 15min
completed: 2026-03-22
---

# Phase 9 Plan 01: Worker Per-Target Queue Isolation Summary

**Serial single-run-at-a-time queue replaced with Map-based per-target isolation — different targets now execute concurrently, same-target runs queue with depth 1, __all__ expands to N parallel sub-runs**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-03-22T00:00:00Z
- **Completed:** 2026-03-22T00:15:00Z
- **Tasks:** 1
- **Files modified:** 2

## Accomplishments

- Replaced `queue: Run[]` + `activeRun: Run | null` with `targetQueues: Map<string, Run[]>` + `activeRuns: Map<string, Run>` — pure per-target isolation
- `processTarget(targetName)` replaces `processNextRun()` — each target has an independent drain loop that fires concurrently across targets
- `sendState()` now collects from `Array.from(activeRuns.values())` and `Array.from(targetQueues.values()).flat()` — satisfies the Phase 8 flat IPC shape with no schema changes
- `__all__` target expansion moved from `processNextRun` into `enqueue()` — sub-runs route through per-target logic and start concurrently instead of serially
- Queue depth 1 enforcement: third enqueue for same target rejects with `run:failed` IPC (manual) or silently skips (interval)
- Cancel handler searches all `targetQueues` entries instead of a single flat queue
- 18 tests covering PARA-01 isolation, EXEC-09 drain, EXEC-08 cancel — all passing

## Task Commits

1. **Task 1: Per-target queue isolation implementation** - `7bdb779` (feat)

## Files Created/Modified

- `app/worker/index.ts` - Replaced serial queue model with per-target Map isolation; new processTarget(); updated enqueue(), sendState(), cancel handler; top-level randomUUID import
- `app/tests/worker/queue.test.ts` - Rewrote makeQueue() helper for per-target model; added PARA-01 describe block with 9 tests; updated EXEC-09/EXEC-08 to per-target semantics

## Decisions Made

- Queue depth 1 per target chosen (not 0 or unbounded): 1 queued slot lets a second trigger "reserve" the target without risk of unbounded queue growth
- Manual trigger gets `run:failed` IPC rejection so the dashboard can show clear user feedback; interval trigger gets silent skip since scheduler pile-up is expected/silent
- `__all__` expansion moved to `enqueue()` (not `processTarget`) so recursive routing works correctly without a placeholder active run

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. TypeScript had pre-existing frontend type errors (missing DOM lib, htm/preact modules) — these are out of scope and pre-existing.

## Next Phase Readiness

- Per-target queue isolation is complete and tested — Phase 9 Plan 02 (per-target scheduler) can now build on top of this model
- `enqueue()` is the single entry point for all triggers — per-target scheduler will call the same `enqueue()` function
- `processTarget()` idempotency guard means the scheduler can safely call `enqueue()` concurrently without double-processing

---
*Phase: 09-worker-parallel-scheduling*
*Completed: 2026-03-22*
