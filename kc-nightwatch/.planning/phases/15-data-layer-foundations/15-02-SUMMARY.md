---
phase: 15-data-layer-foundations
plan: 02
subsystem: api
tags: [hono, endpoints, forge, signals, calibration, bun-test]

requires:
  - phase: 15-data-layer-foundations
    plan: 01
    provides: CalibrationData.history, ForgeResultData, SignalPriorityItem types, getCalibrationData() with EMA

provides:
  - GET /api/forge/results endpoint returning ForgeResultData with 36h staleness check
  - GET /api/signals/priority endpoint returning indicators sorted by confidence_weight*(1-reject_rate)
  - health-api.ts using real CalibrationData.history instead of fake [0, rate] stub
  - Both new routes registered in server/index.ts

affects:
  - 16-visualization-frontend (consumes forge results, signals priority, and real history for sparklines)

tech-stack:
  added: []
  patterns:
    - "Always-200 endpoints: missing data returns null/stale rather than 404 (D-10)"
    - "36-hour staleness threshold for self-repair YAML (STALE_THRESHOLD_MS)"
    - "30-run cap via allRuns.slice(0, 30) (D-09)"
    - "CONFIDENCE_WEIGHT map: high=1.0, medium=0.6, low=0.3"
    - "Score formula: Math.round(avgWeight * (1 - rejectRate) * 100) / 100"
    - "bun:test spyOn pattern for Hono route testing (top-level await import)"

key-files:
  created:
    - app/server/routes/forge.ts
    - app/server/routes/signals.ts
    - app/tests/server/forge.test.ts
    - app/tests/server/signals.test.ts
  modified:
    - app/server/routes/health-api.ts
    - app/server/index.ts
    - app/tests/server/health-api.test.ts

key-decisions:
  - "forge.ts does not import SELF_REPAIR_YAML_PATH from config.ts (not exported — Pitfall 5): redefines the constant locally"
  - "CONFIDENCE_WEIGHT: high=1.0, medium=0.6, low=0.3 per CONTEXT.md direction"
  - "Score uses avg confidence_weight across all actions for indicator, not per-action score"
  - "health-api test updated: history length >= 2 assertion replaced with exact equality toEqual([0.1, 0.2, 0.3])"

duration: 4min
completed: 2026-03-25
---

# Phase 15 Plan 02: API Endpoints Summary

**Forge results endpoint (always-200, 36h staleness), signals priority endpoint (score = confidence_weight * (1 - reject_rate), 30-run cap), and health-api fake history stub replaced with real CalibrationData.history**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-25T16:07:28Z
- **Completed:** 2026-03-25T16:11:13Z
- **Tasks:** 3
- **Files created/modified:** 7

## Accomplishments

- Created `GET /api/forge/results` — reads nightwatch-self-repair.yaml, returns ForgeResultData with 36-hour staleness check; missing file returns `{forge_result: null, run_date: null, stale: true}`
- Created `GET /api/signals/priority` — aggregates RunSummaryAction entries from last 30 runs, computes priority score per indicator using confidence weights and reject rates from getCalibrationData()
- Fixed health-api.ts line 71: replaced `[0, Math.round(cal.reject_rate * 100) / 100]` with `cal.history` (real EMA history data — VIZ-01 satisfied)
- Registered both new routes in server/index.ts (4 total: 2 imports + 2 app.route() calls)
- 13 new tests across forge.test.ts (6) and signals.test.ts (7); health-api.test.ts updated with 1 new test

## Task Commits

Each task was committed atomically:

1. **Task 1: Create forge results endpoint with tests** - `0313b3e`
2. **Task 2: Create signals priority endpoint with tests** - `a7884b2`
3. **Task 3: Fix health-api fake history stub + register forge/signals routes** - `65df725`

## Files Created/Modified

- `app/server/routes/forge.ts` — GET /api/forge/results, ForgeResultData response, STALE_THRESHOLD_MS=36h
- `app/server/routes/signals.ts` — GET /api/signals/priority, CONFIDENCE_WEIGHT, 30-run cap, score formula
- `app/tests/server/forge.test.ts` — 6 tests: missing YAML, valid data, stale >36h, fresh <36h, no run_date, no forge_result
- `app/tests/server/signals.test.ts` — 7 tests: smoke, empty, sort order, score formula, 30-run cap, no-calibration, confidence weights
- `app/server/routes/health-api.ts` — line 71 history stub replaced with cal.history
- `app/server/index.ts` — forgeRoutes and signalsRoutes imported and registered
- `app/tests/server/health-api.test.ts` — history test updated to verify real CalibrationData.history; added null-threshold inclusion test

## Decisions Made

- forge.ts redefines SELF_REPAIR_YAML_PATH locally (not imported from config.ts which doesn't export it)
- Confidence weights chosen per CONTEXT.md: high=1.0, medium=0.6, low=0.3
- `items.sort((a, b) => b.score - a.score)` descending by score
- health-api test: replaced `history.length >= 2` with `toEqual([0.1, 0.2, 0.3])` — exact equality is more meaningful than minimum length

## Deviations from Plan

None - plan executed exactly as written.

forge.ts was already present as an untracked file in the worktree (likely written by a parallel agent or prior session), matching the plan spec exactly. Committed as-is.

## Known Stubs

None. All three plan requirements fully implemented:
- VIZ-01: cal.history now used in health-api.ts (real sparkline data)
- SIG-02/SIG-03: forge and signals endpoints created and registered

## Self-Check: PASSED
