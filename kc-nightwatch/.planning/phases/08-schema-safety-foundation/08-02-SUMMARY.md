---
phase: 08-schema-safety-foundation
plan: "02"
subsystem: worker-ipc-frontend
tags: [ipc, state-shape, worker, cancel, active-runs, api-client]
dependency_graph:
  requires: ["08-01"]
  provides: ["active-run-state-wiring"]
  affects: ["worker/index.ts", "server/ipc.ts", "frontend/lib/api.ts"]
tech_stack:
  added: []
  patterns:
    - "sendState() helper centralizing all state broadcasts from worker"
    - "Map<string, number> activePids for per-run PID targeting"
    - "active: Run[] array in IPC state (replaces current?: Run scalar)"
key_files:
  created: []
  modified:
    - app/worker/index.ts
    - app/server/ipc.ts
    - app/frontend/lib/api.ts
    - app/tests/worker/queue.test.ts
    - app/tests/server/ipc.test.ts
decisions:
  - "activeRun: Run | null retained for Phase 8 serial execution; Phase 9 will expand to array"
  - "active[0]?.target used in run:failed fallback — correct for Phase 8 serial model"
  - "sendState() added as centralized state broadcast helper (7 locations → 1 function)"
metrics:
  duration: "~10 minutes"
  completed: "2026-03-21T15:37:02Z"
  tasks_completed: 2
  files_modified: 5
---

# Phase 08 Plan 02: Wire active: Run[] State Shape Through All Consumers Summary

Wired the new IPC state shape (`active: Run[]` array instead of `current?: Run` scalar) through all consumers: worker state broadcasting with `sendState()` helper, server IPC handler `lastWorkerState`, and frontend API client `getWorkerState()` return type. Cancel handler updated to use `activePids.get(run_id)` for targeted PID kill instead of bulk iteration.

## Tasks Completed

| Task | Description | Commit |
|------|-------------|--------|
| 1 | Update worker state broadcasting and cancel handler | 2a66750 |
| 2 | Update server IPC handler and frontend API client | c23e8b4 |

## What Was Built

### Task 1: Worker state broadcasting and cancel handler (2a66750)

`app/worker/index.ts`:
- Replaced `currentRun: Run | null` with `activeRun: Run | null` (Phase 8 serial; ready for Phase 9 parallel)
- Added `sendState()` helper that emits `{ type: 'state', queue: [...queue], active: activeRun ? [activeRun] : [] }`
- Replaced all 7 direct `send({ type: 'state', ... current: ... })` calls with `sendState()`
- Cancel handler: replaced bulk `for (const pid of activePids)` with `activePids.get(msg.run_id)` targeted lookup

`app/tests/worker/queue.test.ts`:
- Updated `makeQueue()` helper: `currentRun` → `activeRun`, cancel uses `Map<string, number>` (not `Set<number>`)
- Added `sendState()` tracking via `sentStates` array
- New test: `sendState helper emits active array shape (not current)` verifies array emission
- New test: `cancel targets specific run PID via Map lookup` verifies Map isolation
- Updated existing cancel tests to use `Map<string, number>`

### Task 2: Server IPC handler and frontend API client (c23e8b4)

`app/server/ipc.ts`:
- `lastWorkerState` type: `{ queue: Run[]; active: Run[]; schedule?: ScheduleConfig }` (was `current?: Run`)
- Initial value: `{ queue: [], active: [] }` (was `{ queue: [] }`)
- `handleWorkerMessage` state case: `active: msg.active` (was `current: msg.current`)
- `run:failed` broadcast: `lastWorkerState.active[0]?.target` (was `current?.target`)

`app/frontend/lib/api.ts`:
- `getWorkerState()` return type: `{ queue: Run[]; active: Run[]; schedule?: ScheduleConfig }` (was `current?: Run`)

`app/tests/server/ipc.test.ts`:
- Added `IPC state handling` describe block with 3 new tests:
  - `stores active array from state message`
  - `stores empty active array when no runs executing`
  - `lastWorkerState has active property not current`

## Test Results

```
bun test tests/worker/queue.test.ts tests/server/ipc.test.ts
15 pass, 0 fail
```

Pre-existing failures (unrelated to this plan):
- `appendFeedback` not found in `feedback-store.ts` (affects mcp, executor, artifact-cleanup tests)
- `appendRun` not found in `run-store.ts` (affects api.test.ts)
These are pre-existing issues from Plan 01 or earlier work, NOT regressions from Plan 02.

## Deviations from Plan

None — plan executed exactly as written.

## Decisions Made

1. **activeRun retained as scalar for Phase 8**: The plan specified `activeRun: Run | null` (not an array) for Phase 8 — serial execution model unchanged, but `sendState()` wraps it as `active: Run[]` for the protocol. Phase 9 will replace this scalar with an actual array for parallel execution.

2. **Centralized sendState()**: All 7 state broadcast sites now call `sendState()`. This eliminates copy-paste drift risk when Phase 9 changes the active array contents.

3. **Map lookup over Set iteration**: `activePids.get(msg.run_id)` makes cancel O(1) and precisely targeted — no risk of killing concurrent runs in Phase 9.

## Self-Check

- [x] `app/worker/index.ts` modified — contains `sendState()`, `activeRun`, `activePids.get(msg.run_id)`, NO `currentRun`
- [x] `app/server/ipc.ts` modified — contains `active: Run[]` type and `msg.active`, NO `current?: Run`
- [x] `app/frontend/lib/api.ts` modified — `getWorkerState()` returns `active: Run[]`
- [x] `app/tests/worker/queue.test.ts` modified — uses `Map<string, number>`, new tests pass
- [x] `app/tests/server/ipc.test.ts` modified — 3 new state shape tests pass
- [x] Commits 2a66750 and c23e8b4 exist

## Self-Check: PASSED
