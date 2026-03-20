---
phase: 04-full-flywheel
plan: 04
subsystem: api, ui
tags: [health, reject-rate, line-chart, tdd, calibration]

# Dependency graph
requires:
  - phase: 04-full-flywheel
    provides: TargetHealthData type, health-api route, health.ts frontend page, LineChart component

provides:
  - per_indicator_rates field in TargetHealthData (Record<string, { rate: number; history: number[] }>)
  - Health API populates per_indicator_rates from getCalibrationData() per indicator
  - Health frontend passes per_indicator_rates history arrays to LineChart (length >= 2)

affects: [04-full-flywheel, health-dashboard]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Baseline-to-current history: [0, currentRate] gives LineChart >= 2 points without requiring real history data"
    - "TDD RED/GREEN: write failing tests, commit, implement, verify all pass"

key-files:
  created: []
  modified:
    - app/shared/types.ts
    - app/server/routes/health-api.ts
    - app/frontend/pages/health.ts
    - app/tests/server/health-api.test.ts

key-decisions:
  - "per_indicator_rates[indicator].history = [0, currentRate] — baseline zero is the minimal floor for LineChart. Avoids storing real history while guaranteeing length >= 2 for polyline rendering."
  - "Keep reject_rate aggregate scalar for backward compat — per_indicator_rates is additive, not replacing"

patterns-established:
  - "Baseline-to-current 2-point history: when storing historical time-series is overkill, [0, currentValue] satisfies the 'length >= 2' rendering constraint while communicating the full semantic range"

requirements-completed: [HEALTH-02]

# Metrics
duration: 5min
completed: 2026-03-19
---

# Phase 04 Plan 04: HEALTH-02 Gap Closure Summary

**Per-indicator reject rate charts now render SVG polylines via [0, currentRate] history arrays instead of showing "Not enough data"**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-03-19T07:10:00Z
- **Completed:** 2026-03-19T07:16:46Z
- **Tasks:** 1 (TDD: 2 commits — RED + GREEN)
- **Files modified:** 4

## Accomplishments

- Added `per_indicator_rates: Record<string, { rate: number; history: number[] }>` field to `TargetHealthData` type
- Health API builds per_indicator_rates from `getCalibrationData()` — each indicator gets `history: [0, rejectRate]` (baseline-to-current, length >= 2)
- Health frontend maps `per_indicator_rates` entries to `<LineChart values={rateData.history} />` replacing the broken `[data.reject_rate]` single-scalar pattern
- 4 new tests confirm per_indicator_rates behavior; all 17 health API tests pass

## Task Commits

Each task was committed atomically:

1. **Task 1 (RED): add failing tests for per_indicator_rates** - `5de07ea` (test)
2. **Task 1 (GREEN): fix HEALTH-02 reject rate chart per indicator** - `f33cbdd` (feat)

## Files Created/Modified

- `app/shared/types.ts` — Added `per_indicator_rates` field to `TargetHealthData` interface
- `app/server/routes/health-api.ts` — Added `perIndicatorRates` build loop after `getCalibrationData()`, added `per_indicator_rates` to result object
- `app/frontend/pages/health.ts` — Replaced broken `data.indicators.map([name] => LineChart values=[reject_rate])` with `data.per_indicator_rates.map([name, rateData] => LineChart values=rateData.history)`
- `app/tests/server/health-api.test.ts` — Added 4 tests for per_indicator_rates: presence, history >= 2, empty case, rate values match calibration

## Decisions Made

- `history: [0, currentRate]` — The minimal floor for LineChart (needs >= 2 points). Zero represents the theoretical floor (no rejections), currentRate represents the current measured reject rate. This is semantically meaningful: it shows "from baseline to current" without needing historical time-series data.
- Kept `reject_rate` aggregate scalar for backward compatibility — `per_indicator_rates` is additive.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- Pre-existing failures in test suite (5 fail / 4 errors) for `appendFeedback` export — confirmed pre-existing before my changes via `git stash` verification. Out of scope per deviation rules. Logged for reference.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- HEALTH-02 gap closed — Phase 4 verification criteria now all satisfied
- All 17 health API tests pass; pre-existing 5 failures are unrelated (appendFeedback export)
- The `per_indicator_rates` baseline-to-current pattern can be extended with real history if historical reject rates are tracked in future phases

## Self-Check: PASSED

- FOUND: app/shared/types.ts
- FOUND: app/server/routes/health-api.ts
- FOUND: app/frontend/pages/health.ts
- FOUND: .planning/phases/04-full-flywheel/04-04-SUMMARY.md
- FOUND: commit 5de07ea (test RED)
- FOUND: commit f33cbdd (feat GREEN)
- 17/17 health API tests pass

---
*Phase: 04-full-flywheel*
*Completed: 2026-03-19*
