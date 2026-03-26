---
phase: 17-signal-priority-display
plan: 01
subsystem: ui
tags: [signal-priority, action-card, scoring, dashboard]

# Dependency graph
requires:
  - phase: 14-extended-feedback
    provides: FeedbackEntry with 3-state verdict + 5 source values (calibration context)
  - phase: 10-auto-action-output-loop
    provides: RunSummaryAction with assessment.confidence + closer_to_north_star
provides:
  - Signal priority scoring service (confidence × alignment → 0.0–1.0)
  - GET /api/signals/priority?run_id endpoint
  - api.getSignalPriority() frontend client method
  - ActionCard score badge "0.72 high" with color-coded display
  - ActionCards sorted by priority score descending in runs detail view
affects: [future-flywheel-visualization, outcomes-page, health-page]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Priority score = confidence_weight × alignment_weight (high=1.0, medium=0.67, low=0.33) × (yes=1.0, uncertain=0.5, no=0.0)"
    - "Score badge format: '0.72 high' — numeric score + confidence label in one compact token"
    - "Optional prop pattern: priorityScore?: number — graceful render when API not yet loaded"

key-files:
  created:
    - app/server/services/signal-priority.ts
    - app/server/routes/signal-priority.ts
    - app/tests/server/signal-priority.test.ts
  modified:
    - app/shared/types.ts
    - app/server/index.ts
    - app/frontend/lib/api.ts
    - app/frontend/pages/runs.ts
    - app/frontend/components/action-card.ts

key-decisions:
  - "Score = confidence × alignment (not additive) — captures multiplicative relationship: high confidence + bad alignment = 0, not 1.33"
  - "Sort is client-side after priority fetch — keeps server response simple, avoids coupling sort logic to run-store"
  - "Optional priorityScore prop on ActionCard — badge renders only when data loaded, no layout shift on missing data"

patterns-established:
  - "Signal priority endpoint: GET /api/signals/priority?run_id — returns sorted entries with signal_id, score, confidence, closer_to_north_star"
  - "Color thresholds: green >= 0.67, amber >= 0.34, muted < 0.34 — mirrors confidence levels high/medium/low"

requirements-completed: []

# Metrics
duration: 25min
completed: 2026-03-27
---

# Phase 17 Plan 01: Signal Priority Display Summary

**Priority score badge (0.72 high) on ActionCards, sorted by confidence × north-star alignment, backed by new /api/signals/priority endpoint with 14 tests**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-03-27T00:00:00Z
- **Completed:** 2026-03-27T00:25:00Z
- **Tasks:** 2 complete + 1 visual checkpoint (auto-approved, auto_advance=true)
- **Files modified:** 8

## Accomplishments

- New `computePriorityScore()` service: confidence × alignment produces 0.0–1.0 score (1.0 = high confidence + yes alignment, 0.0 = low + no)
- GET /api/signals/priority?run_id returns sorted priority entries for all actions in a run
- ActionCards in runs detail view now sorted by descending priority score
- Score badge "0.72 high" in collapsed ActionCard header with color coding (green/amber/muted) and tooltip context
- 14 new tests: unit tests for score math + sort correctness + API route (183 server tests total, 0 fail)

## Task Commits

Each task was committed atomically:

1. **Task 1: Signal priority scoring + API + runs sort** - `b7164f3` (feat)
2. **Task 2: ActionCard score display** - `d6f3e5a` (feat)
3. **Task 3: Visual checkpoint** - auto-approved (auto_advance=true)

**Plan metadata:** (pending final commit)

## Files Created/Modified

- `app/server/services/signal-priority.ts` - computePriorityScore() + computePriorities() service
- `app/server/routes/signal-priority.ts` - GET /api/signals/priority?run_id route
- `app/tests/server/signal-priority.test.ts` - 14 tests covering score math, sort, API
- `app/shared/types.ts` - SignalPriorityEntry interface added
- `app/server/index.ts` - signalPriorityRoutes registered
- `app/frontend/lib/api.ts` - api.getSignalPriority() method added
- `app/frontend/pages/runs.ts` - priorityMap state + sorted ActionCard rendering
- `app/frontend/components/action-card.ts` - priorityScore prop + score badge display

## Decisions Made

- **Score formula**: confidence × alignment (multiplicative not additive). High confidence + bad alignment = 0.0 — correct behavior since alignment is the north star filter.
- **Client-side sort**: Priority fetch in runs.ts, sort inline on render. Keeps API simple and sort behavior visible in frontend code.
- **Optional prop**: `priorityScore?: number` on ActionCard. Badge only renders when score is defined — no placeholder, no layout shift.
- **Color thresholds**: >= 0.67 green, >= 0.34 amber, < 0.34 muted. Matches the three confidence levels mapped to high/medium/low.

## Deviations from Plan

None - plan executed exactly as specified. Phase 17 directory and plan file created as part of execution (phase was described in objective, no PLAN.md existed yet).

## Issues Encountered

- node_modules not present in worktree — installed with `bun install` (396ms, non-blocking)
- No regressions in existing test suite

## Known Stubs

None — score computation uses real `assessment` data from RunSummaryAction. No hardcoded values or placeholder text.

## User Setup Required

None - no external service configuration required. Score badge appears automatically when runs with actions exist.

## Next Phase Readiness

Phase 17 plan 01 complete. This is the last plan of v4.0 milestone. Signal priority scoring is live:
- `/api/signals/priority` accepts any run_id with actions
- ActionCards show score + sort by value in runs detail view
- v4.0 feature: signal prioritization (confidence × historical success ranking) — delivered

## Self-Check: PASSED

- `app/server/services/signal-priority.ts` — FOUND
- `app/server/routes/signal-priority.ts` — FOUND
- `app/tests/server/signal-priority.test.ts` — FOUND
- `app/shared/types.ts` (SignalPriorityEntry) — FOUND
- `app/frontend/components/action-card.ts` (priorityScore prop) — FOUND
- Commit b7164f3 — FOUND
- Commit d6f3e5a — FOUND

---
*Phase: 17-signal-priority-display*
*Completed: 2026-03-27*
