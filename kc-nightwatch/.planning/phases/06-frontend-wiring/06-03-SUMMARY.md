---
phase: 06-frontend-wiring
plan: "03"
subsystem: ui
tags: [preact, polling, sse, use-poll, refresh-trigger, queue-time]

requires:
  - phase: 06-frontend-wiring
    plan: "01"
    provides: "usePoll hook with refreshTrigger signal for interval + SSE-driven immediate re-fetch"

provides:
  - "runs.ts: 5s auto-refresh polling via usePoll, stops when all runs reach terminal state"
  - "runs.ts: SSE-driven immediate re-fetch via refreshTrigger (watched internally by usePoll)"
  - "runs.ts: run list shows 'Queued Xm ago' for queued runs, started_at for others"
  - "runs.ts: run detail header shows both queued_at and started_at timestamps"
  - "runs.ts: detail view refreshes alongside list during active polling"

affects: []

tech-stack:
  added: []
  patterns:
    - "useCallback for stable fetchFn identity — passed to usePoll without triggering usePoll re-setup"
    - "hasActiveRuns state gates polling — usePoll receives shouldPoll=false when all runs are terminal"
    - "Detail refresh via runs dependency — useEffect([runs]) re-fetches selected run only when polling is active"

key-files:
  created: []
  modified:
    - app/frontend/pages/runs.ts

key-decisions:
  - "useCallback wraps loadRuns to maintain stable identity — avoids spurious usePoll invocations"
  - "Detail refresh effect guards on hasActiveRuns — no unnecessary API calls when all runs are terminal"
  - "Queue time display: 'Queued Xm ago' for queued status, timeAgo(started_at) for all other statuses"

patterns-established:
  - "Polling page pattern: loadRuns via useCallback + hasActiveRuns state + usePoll(loadRuns, 5_000, hasActiveRuns)"
  - "Detail-follows-list pattern: useEffect([runs]) re-fetches detail when list updates during active polling"

requirements-completed: [QUEUE-02, POLL-01]

duration: 5min
completed: 2026-03-20
---

# Phase 06 Plan 03: Runs Page Polling and Queue Time Display Summary

**Runs page live-updates every 5s via usePoll with SSE-driven immediate re-fetch, showing "Queued Xm ago" in the list and both queued_at/started_at in run detail**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-20T09:40:00Z
- **Completed:** 2026-03-20T09:45:00Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Added `usePoll(loadRuns, 5_000, hasActiveRuns)` — Runs page now auto-refreshes every 5s when any run is active or queued
- Polling stops automatically when all runs reach terminal state (completed/failed/timeout/cancelled)
- SSE events from app.ts (Plan 02) increment refreshTrigger, which usePoll watches internally — triggers immediate re-fetch without waiting for 5s interval
- Run list shows "Queued Xm ago" for queued runs (using queued_at) and existing started_at display for all other statuses
- Run detail header now shows both "Queued Xm ago" and "Started Xm ago" spans with ISO timestamp tooltips
- Detail view re-fetches selected run on each list refresh during active polling (useEffect on `runs` dependency)

## Task Commits

Each task was committed atomically:

1. **Task 1: Add auto-refresh polling and queue time display to Runs page** - `5ced23a` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified
- `app/frontend/pages/runs.ts` — useCallback import, usePoll import, hasActiveRuns state, loadRuns() function, usePoll call, detail refresh effect, queue time display in list, queued_at + started_at spans in detail header

## Decisions Made
- `useCallback` wraps `loadRuns` to give it a stable identity — necessary so passing it to `usePoll` doesn't cause usePoll to re-setup on every render
- Detail refresh effect guards on `hasActiveRuns` — avoids unnecessary `api.getRun()` calls when there are no active runs and polling is stopped
- Queue time conditional: `run.status === 'queued'` shows `Queued ${timeAgo(run.queued_at)}` since started_at is undefined for queued runs; all other statuses fall through to `timeAgo(run.started_at)`

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 06 is now complete — all 3 plans executed
- Runs page polling mirrors Dashboard behavior, both driven by the same usePoll + refreshTrigger infrastructure from Plan 01
- SSE events from Plan 02 (app.ts) automatically trigger re-fetch on both Dashboard and Runs page via shared refreshTrigger signal

---
*Phase: 06-frontend-wiring*
*Completed: 2026-03-20*
