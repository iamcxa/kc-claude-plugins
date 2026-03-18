---
phase: 03-flywheel-core
plan: "03"
subsystem: feedback
tags: [feedback, calibration, hono, preact, yaml, gh-cli, bun]

# Dependency graph
requires:
  - phase: 03-flywheel-core/03-01
    provides: FeedbackEntry and CalibrationData types in shared/types.ts
  - phase: 03-flywheel-core/03-01
    provides: yaml-store readYamlFile/writeYamlFile pattern

provides:
  - Feedback store with YAML persistence (explicit_feedback / pr_feedback / linear_feedback)
  - Reject rate calibration with per-indicator threshold adjustment
  - POST /api/feedback, GET /api/feedback/:runId, GET /api/feedback/calibration routes
  - Frontend API client methods: submitFeedback, getFeedback, getCalibration
  - ActionCard component with expandable layout and +1/-1 feedback buttons
  - Implicit feedback collector via gh CLI PR status polling
  - Feedback trends markdown writer for NW journal integration

affects:
  - 03-04 (Phase 4 MCP: Linear MCP integration for checkLinearStatus placeholder)
  - any phase that needs reject rate data for threshold calibration

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "YAML feedback store: separate keys for explicit_feedback / pr_feedback / linear_feedback"
    - "Calibration formula: threshold = clamp(0.1, 0.9, 0.5 + (rejectRate - 0.5) * 0.5)"
    - "Optimistic disable on feedback buttons: setSubmitted(verdict) before await, revert on error"
    - "Route ordering in Hono: /api/feedback/calibration MUST precede /api/feedback/:runId"

key-files:
  created:
    - app/server/services/feedback-store.ts
    - app/server/routes/feedback.ts
    - app/frontend/components/action-card.ts
    - app/worker/feedback-collector.ts
    - app/tests/server/feedback.test.ts
    - app/tests/server/calibration.test.ts
    - app/tests/server/feedback-polling.test.ts
  modified:
    - app/server/index.ts (feedbackRoutes registration)
    - app/frontend/lib/api.ts (submitFeedback, getFeedback, getCalibration methods)
    - app/frontend/pages/runs.ts (ActionCard import and usage in run detail)

key-decisions:
  - "calibration route defined before :runId param route — prevents 'calibration' being parsed as a run ID"
  - "checkLinearStatus returns null (Phase 3 placeholder) — Linear MCP integration deferred to Phase 4"
  - "writeFeedbackTrends writes to journalDir/feedback-trends.md as markdown table for NW slow learning path"
  - "ActionCard uses optimistic disable: setSubmitted(verdict) before API call, revert on failure"

patterns-established:
  - "Calibration formula: threshold = clamp(0.1, 0.9, 0.5 + (rejectRate - 0.5) * 0.5) — moves threshold toward reject direction at half-rate"
  - "Route ordering guard: fixed routes must precede parameterized routes in Hono to avoid param capture"

requirements-completed: [FEED-01, FEED-02, FEED-04, FEED-06, FEED-07]

# Metrics
duration: 24min
completed: 2026-03-18
---

# Phase 3 Plan 03: Feedback Pipeline Summary

**YAML-backed feedback store with reject-rate calibration, Hono API routes, ActionCard component with +1/-1 buttons, and gh CLI implicit feedback collector for the flywheel learning loop**

## Performance

- **Duration:** 24 min
- **Started:** 2026-03-18T10:18:52Z
- **Completed:** 2026-03-18T10:42:52Z
- **Tasks:** 3
- **Files modified:** 10 (7 created, 3 modified)

## Accomplishments

- Feedback store persists entries in nightwatch-feedback.yaml with separate keys per source (explicit_feedback, pr_feedback, linear_feedback)
- Reject rate calibration computes per-indicator confidence thresholds with formula: `threshold = clamp(0.1, 0.9, 0.5 + (rejectRate - 0.5) * 0.5)`
- Feedback API routes handle submit (POST /api/feedback), query by run (GET /api/feedback/:runId), and calibration data (GET /api/feedback/calibration)
- ActionCard component renders expandable action cards with +1/-1 feedback buttons, aria accessibility attributes, and optimistic disable on click
- Implicit feedback collector polls gh CLI for PR merge/close status, handles errors gracefully, Linear MCP placeholder for Phase 4
- All 140 tests pass (from 129 before this plan)

## Task Commits

Each task was committed atomically:

1. **Task 1: Feedback store service + API routes + tests** - `b187127` (feat)
2. **Task 2: ActionCard component + feedback buttons + runs.ts integration** - `c8001f9` (feat)
3. **Task 3: Implicit feedback collector (PR/Linear polling) + NW journal integration** - `0609857` (feat)

## Files Created/Modified

- `app/server/services/feedback-store.ts` - appendFeedback, getFeedbackForRun, getCalibrationData, writeFeedbackTrends
- `app/server/routes/feedback.ts` - Hono routes for submit/query/calibration
- `app/server/index.ts` - feedbackRoutes registered after chatRoutes
- `app/frontend/lib/api.ts` - submitFeedback, getFeedback, getCalibration added to api object
- `app/frontend/components/action-card.ts` - Expandable action card with feedback buttons
- `app/frontend/pages/runs.ts` - ActionCard import and per_target rendering in run detail
- `app/worker/feedback-collector.ts` - collectImplicitFeedback, checkPrStatus, checkLinearStatus
- `app/tests/server/feedback.test.ts` - 5 tests for FeedbackEntry and calibration logic
- `app/tests/server/calibration.test.ts` - 6 tests for threshold formula
- `app/tests/server/feedback-polling.test.ts` - 6 tests for feedback collector

## Decisions Made

- **Calibration route ordering**: `GET /api/feedback/calibration` must be defined before `GET /api/feedback/:runId` in Hono — otherwise "calibration" string is captured as a runId parameter
- **Linear placeholder**: checkLinearStatus returns null in Phase 3; full Linear MCP integration deferred to Phase 4 as planned
- **writeFeedbackTrends**: Writes markdown table to `journalDir/feedback-trends.md` for NW slow learning path — NW journal reads this during next run

## Deviations from Plan

None - plan executed exactly as written.

The only minor deviation was adding `void` before `handleFeedback()` calls in the event handlers to satisfy TypeScript's no-floating-promise rule — a correctness fix, not a scope change.

## Issues Encountered

None - all tasks executed cleanly. The linter auto-completed the index.ts and api.ts updates (added configRoutes from Phase 3 Plan 01 that was already in-flight).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Feedback pipeline is fully operational: explicit user feedback (buttons) + implicit PR status (gh CLI)
- Calibration data available at /api/feedback/calibration for Phase 4 threshold tuning
- Linear MCP hook point (`checkLinearStatus`) is in place — Phase 4 wires it to actual MCP call
- writeFeedbackTrends function ready to be called from worker after each run completes

---
*Phase: 03-flywheel-core*
*Completed: 2026-03-18*
