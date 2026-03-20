---
phase: 05-schema-server-infrastructure
plan: "01"
subsystem: server-ipc-api
tags: [queue-awareness, sse, ipc, api, typescript]
dependency_graph:
  requires: []
  provides: [queued_at-timestamp, worker-state-endpoint, run-failed-sse]
  affects: [phase-06-frontend-wiring]
tech_stack:
  added: []
  patterns: [lastWorkerState-snapshot, broadcastGlobal-run-failed, GET-worker-state-polling]
key_files:
  created: []
  modified:
    - app/shared/types.ts
    - app/server/ipc.ts
    - app/server/routes/api.ts
    - app/worker/scheduler.ts
    - app/worker/index.ts
decisions:
  - "queued_at field is optional (queued_at?: string) for backward compatibility with existing runs in nightwatch-runs.yaml"
  - "run:failed target lookup uses lastWorkerState.current?.target — the failing run IS the current run at failure time; fallback to 'unknown'"
  - "GET /api/worker/state placed before GET /api/runs/:id param route to respect Hono route ordering"
metrics:
  duration: "~10 minutes"
  completed_date: "2026-03-20"
  tasks_completed: 2
  files_modified: 5
---

# Phase 5 Plan 1: Schema and Server Infrastructure Summary

Queue awareness server-side foundation: queued_at timestamp on all 4 enqueue paths, GET /api/worker/state endpoint, and run:failed global SSE broadcast.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Add queued_at to Run type and all 4 enqueue paths | 504da36 | shared/types.ts, server/routes/api.ts, worker/scheduler.ts, worker/index.ts |
| 2 | Add worker state endpoint and run:failed SSE broadcast | 256904f | server/ipc.ts, server/routes/api.ts |

## What Was Built

### Task 1: queued_at timestamp on all enqueue paths

Added `queued_at?: string` to the `Run` interface in `app/shared/types.ts`. The field is optional for backward compatibility with existing YAML-stored runs.

Set `queued_at: new Date().toISOString()` at all 4 enqueue sites:
1. `POST /api/runs` — manual trigger
2. `POST /api/webhook` — webhook trigger
3. `app/worker/scheduler.ts` — interval trigger (scheduler-initiated runs)
4. `app/worker/index.ts` — `__all__` expansion sub-runs

### Task 2: Worker state endpoint and run:failed SSE broadcast

In `app/server/ipc.ts`:
- Added `let lastWorkerState` module variable, initialized to `{ queue: [] }`
- Exported `getLastWorkerState()` function
- Updated `case 'state'` handler to store `{ queue, current, schedule }` snapshot on every IPC state message
- Updated `case 'run:failed'` handler to call `broadcastGlobal('run:failed', { run_id, target, error })` — target resolved from `lastWorkerState.current?.target ?? 'unknown'`

In `app/server/routes/api.ts`:
- Added `getLastWorkerState` to import from `../ipc.ts`
- Added `GET /api/worker/state` route (placed before param routes per Hono ordering rules), returns `getLastWorkerState()` as JSON

## Verification Results

All 3 plan success criteria verified:

1. **queued_at on all 4 paths**: 4 matches found in api.ts (2), scheduler.ts (1), index.ts (1)
2. **GET /api/worker/state**: Route definition confirmed at api.ts:45
3. **run:failed SSE broadcast**: `broadcastGlobal('run:failed',` confirmed at ipc.ts:99

TypeScript: No errors in any of the 5 modified files. Pre-existing frontend type errors (htm/preact DOM types) are unrelated and out of scope.

Tests: 173 pass / 6 fail / 4 errors — same failure count as baseline (pre-existing `appendFeedback` export issue in feedback-store tests, not related to this plan's changes).

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED

Files exist:
- app/shared/types.ts: FOUND
- app/server/ipc.ts: FOUND
- app/server/routes/api.ts: FOUND
- app/worker/scheduler.ts: FOUND
- app/worker/index.ts: FOUND

Commits exist:
- 504da36: FOUND (feat(05-01): add queued_at timestamp to Run type and all 4 enqueue paths)
- 256904f: FOUND (feat(05-01): add worker state endpoint and run:failed SSE broadcast)
