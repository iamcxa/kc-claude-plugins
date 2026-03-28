---
phase: 19-signal-priority-wire-fix
plan: 01
subsystem: api
tags: [hono, signal-priority, frontend, bun, preact]

# Dependency graph
requires:
  - phase: 17-signal-priority-display
    provides: signal-priority service (computePriorities), routes/signal-priority.ts, frontend ActionCard with priorityScore prop
  - phase: 15-data-layer-foundations
    provides: Phase 15 /api/signals/priority route (signalsRoutes) and SignalPriorityItem type — kept unchanged
provides:
  - GET /api/signals/priority/run?run_id=<id> route — distinct from Phase 15 aggregate endpoint
  - signalPriorityRoutes imported and registered in server/index.ts
  - api.getSignalPriority(runId) calling /api/signals/priority/run with run-scoped scoring
  - priorityMap keyed by signal_id enabling ActionCard score badge display and descending sort
  - SIG-01 v4.0 requirement satisfied (all 7/7 v4.0 requirements complete)
affects: [verification, future-phases-using-signal-priority]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Route isolation: per-run scoring at /api/signals/priority/run; aggregate by indicator at /api/signals/priority"
    - "Inline type at API boundary: getSignalPriority returns inline object shape instead of importing server-side type"

key-files:
  created: []
  modified:
    - app/server/routes/signal-priority.ts
    - app/server/index.ts
    - app/frontend/lib/api.ts
    - app/frontend/pages/runs.ts
    - app/shared/types.ts
    - app/tests/server/signal-priority.test.ts
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Route path changed from /api/signals/priority to /api/signals/priority/run to avoid shadowing Phase 15 signalsRoutes"
  - "Inline type shape used in api.ts for SignalPriorityEntry (no cross-boundary server type import)"
  - "Duplicate SignalPriorityEntry removed from shared/types.ts — authoritative definition in services/signal-priority.ts"

patterns-established:
  - "worktree executor drift fix: three-point check (route path, registration, API client key) when resuming disconnected Phase work"

requirements-completed: [SIG-01]

# Metrics
duration: 3min
completed: 2026-03-27
---

# Phase 19 Plan 01: Signal Priority Wire Fix Summary

**End-to-end signal priority data flow restored: /api/signals/priority/run route registered, API client updated with runId param, priorityMap keyed by signal_id — ActionCards now display score badges and sort descending in run detail**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-27T13:37:01Z
- **Completed:** 2026-03-27T13:40:00Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments

- Fixed route path collision: changed `/api/signals/priority` to `/api/signals/priority/run` so Phase 15 signalsRoutes no longer shadows Phase 17 signalPriorityRoutes
- Registered `signalPriorityRoutes` in server/index.ts (was missing — the root cause of the 404 disconnect)
- Updated `getSignalPriority()` to accept `runId` param and call the new run-scoped endpoint
- Fixed frontend `priorityMap` to key by `signal_id` (was `indicator`) in both useEffect hooks, sort, and prop pass-through
- Removed duplicate `SignalPriorityEntry` from shared/types.ts (worktree executor artifact)
- All 14 signal-priority route tests updated to new path and pass; full suite 450 tests, 0 fail
- SIG-01 marked complete — all 7/7 v4.0 requirements satisfied

## Task Commits

1. **Task 1: Wire signal priority route + API client + update tests** - `05fec6a` (fix)
2. **Task 2: Wire frontend mapping + sort + update SIG-01 requirement** - `070421b` (fix)

**Plan metadata:** `4e498e9` (docs: complete plan)

## Files Created/Modified

- `app/server/routes/signal-priority.ts` - Route path changed from /api/signals/priority to /api/signals/priority/run
- `app/server/index.ts` - Added import and registration of signalPriorityRoutes
- `app/frontend/lib/api.ts` - getSignalPriority(runId) with new path; removed SignalPriorityItem import
- `app/frontend/pages/runs.ts` - priorityMap keyed by signal_id in both useEffects + sort + prop
- `app/shared/types.ts` - Removed duplicate SignalPriorityEntry interface
- `app/tests/server/signal-priority.test.ts` - All route test paths updated to /api/signals/priority/run
- `.planning/REQUIREMENTS.md` - SIG-01 marked [x] complete; formula text corrected; Unsatisfied: 0

## Decisions Made

- Route path uses `/run` suffix to maintain backward compat with Phase 15's `/api/signals/priority` aggregate endpoint — no migration needed for existing callers
- Used inline type in api.ts `getSignalPriority` return type to avoid importing server-side types into frontend module

## Deviations from Plan

None — plan executed exactly as written. All 5 sub-actions in Task 1 and all 4+1 sub-actions in Task 2 matched their specifications.

## Issues Encountered

None. The three wiring breaks (route path, registration, key name) were exactly as diagnosed in the plan. No unexpected behavior encountered.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- v4.0 milestone requirements complete: all 7/7 satisfied (VIZ-01, VIZ-02, VIZ-03, SIG-01, SIG-02, SIG-03, FORGE-01)
- ActionCards in run detail will display priority score badges and sort by score descending once the server is running with the new code
- No blockers for future work

## Self-Check: PASSED

- All 7 modified files found on disk
- Commits 05fec6a and 070421b verified in git log
- 450 tests pass, 0 fail
- SIG-01 marked complete in REQUIREMENTS.md
- SUMMARY.md created at .planning/phases/19-signal-priority-wire-fix/19-01-SUMMARY.md

---
*Phase: 19-signal-priority-wire-fix*
*Completed: 2026-03-27*
