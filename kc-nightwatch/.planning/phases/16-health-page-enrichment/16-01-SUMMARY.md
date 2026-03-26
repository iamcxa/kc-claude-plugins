---
phase: 16-health-page-enrichment
plan: 01
subsystem: api
tags: [hono, bun, typescript, health-api, types]

# Dependency graph
requires:
  - phase: 15-calibration-api
    provides: HealthIndicatorData type and health-api.ts indicator loop structure
provides:
  - HealthIndicatorData.run_ids parallel array in types.ts and health-api.ts
  - api.getForgeResults() client method in api.ts
  - Two new test cases verifying run_ids length alignment and chronological order
affects:
  - 16-02-health-page-components (needs run_ids for sparkline tooltips and getForgeResults for forge card)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Parallel array extraction: push runData.id in the same loop branch as history value to guarantee alignment"

key-files:
  created: []
  modified:
    - app/shared/types.ts
    - app/server/routes/health-api.ts
    - app/frontend/lib/api.ts
    - app/tests/server/health-api.test.ts

key-decisions:
  - "run_ids is optional (run_ids?: string[]) so existing callers with no run_ids don't break"
  - "indicatorRunIds pushed in same branch as indicatorHistory to guarantee parallel alignment (per RESEARCH Pitfall 2)"
  - "getForgeResults() placed after getCalibration() to maintain logical API grouping"

patterns-established:
  - "Parallel array alignment: push both history value and run ID in the same if-initialized branch"

requirements-completed: [VIZ-03, FORGE-01]

# Metrics
duration: 10min
completed: 2026-03-26
---

# Phase 16 Plan 01: Health Page Data Enrichment — run_ids + getForgeResults Summary

**HealthIndicatorData extended with run_ids parallel array (VIZ-03) and api.getForgeResults() added for forge card data (FORGE-01), with 2 new test cases confirming alignment**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-03-26T08:45:00Z
- **Completed:** 2026-03-26T08:55:00Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- Added `run_ids?: string[]` field to `HealthIndicatorData` interface in types.ts
- Extracted run IDs parallel to history values in health-api.ts indicatorRunIds map
- Added `getForgeResults()` client method to api.ts calling `GET /api/forge/results`
- Added 2 new test cases: run_ids length === history length, run_ids in chronological order
- All 20 health-api tests pass (18 existing + 2 new)

## Task Commits

Each task was committed atomically:

1. **Task 1: Add run_ids to HealthIndicatorData type and extract in health-api.ts** - `060b796` (feat)
2. **Task 2: Add run_ids test assertions and getForgeResults() API client method** - `a35413b` (feat)

**Plan metadata:** (see final docs commit)

## Files Created/Modified
- `app/shared/types.ts` - Added `run_ids?: string[]` to HealthIndicatorData interface
- `app/server/routes/health-api.ts` - Added indicatorRunIds extraction parallel to indicatorHistory, included in indicators build
- `app/frontend/lib/api.ts` - Added ForgeResultData import and getForgeResults() method
- `app/tests/server/health-api.test.ts` - Added 2 new test cases for run_ids alignment and chronological order

## Decisions Made
- `run_ids` is optional (`run_ids?: string[]`) — existing downstream code won't break if field absent
- `indicatorRunIds` pushed in the same `if (!indicatorHistory[name])` branch as `indicatorHistory` to guarantee parallel alignment (Pitfall 2 from RESEARCH.md)
- `getForgeResults()` placed after `getCalibration()` in api.ts to maintain logical API method grouping

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

Pre-existing flaky tests found in `tests/worker/auto-action.test.ts` (2 timeout failures during concurrent full suite run). These fail due to process isolation race conditions under parallel test execution, not related to this plan's changes. The tests pass when run in isolation. Logged as out-of-scope discovery.

## Next Phase Readiness
- `HealthIndicatorData.run_ids` is now available to phase 16-02 frontend components for sparkline tooltip display
- `api.getForgeResults()` is available for forge card data fetching
- No blockers for 16-02

---
*Phase: 16-health-page-enrichment*
*Completed: 2026-03-26*
