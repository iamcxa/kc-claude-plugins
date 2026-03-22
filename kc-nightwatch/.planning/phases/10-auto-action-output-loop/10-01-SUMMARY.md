---
phase: 10-auto-action-output-loop
plan: 01
subsystem: worker
tags: [bun, yaml, tdd, outcome-tracking, dedup]

requires:
  - phase: 09-worker-parallel-scheduling
    provides: executor.ts post-run hook point with per-target RunSummary

provides:
  - OutcomeRecord type in shared/types.ts (D-06 schema)
  - outcome-store.ts with readOutcomes/appendOutcome/queryOutcomes (YAML data layer)
  - auto-action.ts with recordRunOutcomes (post-run recording with dedup)
  - executor.ts wired to call recordRunOutcomes after collectImplicitFeedback

affects:
  - phase 10-02 (MCP tools reading from outcome-store.ts)
  - phase 11 (Outcomes page querying queryOutcomes)

tech-stack:
  added: []
  patterns:
    - Optional path param for testability (outcome-store accepts outcomesPath argument for test isolation without mocks)
    - TDD-first YAML data layer (tests use temp dirs, no mocks needed for data layer itself)
    - spyOn-based isolation for worker logic tests (mock appendOutcome/queryOutcomes to test recordRunOutcomes independently)

key-files:
  created:
    - app/shared/types.ts (OutcomeRecord interface added)
    - app/server/services/outcome-store.ts
    - app/tests/server/outcome-store.test.ts
    - app/worker/auto-action.ts
    - app/tests/worker/auto-action.test.ts
  modified:
    - app/worker/executor.ts (import + recordRunOutcomes call in post-run hook)

key-decisions:
  - "Test isolation via optional path param (outcomesPath) rather than module-level mocking — outcome-store accepts optional path for TDD without complex mocking"
  - "Dedup checks outcomes.yaml first (primary), then gh pr list --head {branch} for PRs (secondary) — gracefully degrades when gh unavailable"
  - "recordRunOutcomes placed inside !timedOut block in executor, matching existing collectImplicitFeedback placement"

patterns-established:
  - "Optional path parameter pattern: service functions accept optional {serviceName}Path param for testability (matches run-store.ts convention)"

requirements-completed: [AUTO-01, AUTO-02, AUTO-03]

duration: 20min
completed: 2026-03-22
---

# Phase 10 Plan 01: Auto-Action Output Loop Summary

**YAML outcome data layer (outcome-store.ts) + post-run recorder (auto-action.ts) that persists PR and Linear issue URLs with dedup to ~/.claude/kc-plugins-config/nightwatch-outcomes.yaml after production runs**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-03-22T08:00:00Z
- **Completed:** 2026-03-22T08:19:01Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- OutcomeRecord interface with all D-06 fields added to shared/types.ts
- outcome-store.ts providing readOutcomes/appendOutcome/queryOutcomes backed by YAML file at ~/.claude/kc-plugins-config/nightwatch-outcomes.yaml
- auto-action.ts with full mode-gating (D-02), dedup strategy (D-08/D-09/D-10), and AutoActionResult summary
- executor.ts wired to call recordRunOutcomes in post-run hook (fire-and-forget, error-logged)
- 20 new tests across 2 test files; all 110 worker tests pass

## Task Commits

Each task was committed atomically:

1. **Task 1: OutcomeRecord type + outcome-store.ts data layer** - `5b7c7d4` (feat)
2. **Task 2: auto-action.ts with dedup + executor.ts wiring** - `e23898b` (feat)

**Plan metadata:** (docs commit follows)

_Note: Both tasks used TDD (RED → GREEN). No REFACTOR phase needed — code was clean on first pass._

## Files Created/Modified

- `app/shared/types.ts` - Added OutcomeRecord interface (id, type, target, signal_id, run_id, url, branch?, status, created_at)
- `app/server/services/outcome-store.ts` - YAML data layer: readOutcomes, appendOutcome, queryOutcomes with filter support
- `app/tests/server/outcome-store.test.ts` - 10 TDD tests for all store behaviors
- `app/worker/auto-action.ts` - recordRunOutcomes with mode-gating, isDuplicate with outcomes.yaml + gh pr list checks
- `app/tests/worker/auto-action.test.ts` - 10 TDD tests for mode-gating, recording, dedup, and executor wiring
- `app/worker/executor.ts` - Added import + recordRunOutcomes call after writeFeedbackTrends block

## Decisions Made

- **Optional path parameter for testability**: outcome-store functions accept `outcomesPath = OUTCOMES_YAML_PATH` as optional second arg. This enables test isolation using temp directories without module-level mocking — matching the pattern in yaml-store.ts tests.
- **Auto-action tests use spyOn**: recordRunOutcomes isolates from filesystem by spying on appendOutcome and queryOutcomes from outcome-store. This decouples worker-level logic from YAML I/O.
- **dedup is outcomes.yaml-first**: queryOutcomes({ target, type, status: 'open' }) is the primary dedup check. gh pr list is a secondary fallback for PRs with a known branch. Linear has outcomes.yaml-only dedup (no external API in dedup path).

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- outcome-store.ts ready for Phase 10-02 MCP tools (nw_get_outcomes, nw_get_outcome_status, nw_outcome_summary)
- queryOutcomes filter API supports all D-12/D-14 MCP tool use cases
- Outcomes page (Phase 11) can call queryOutcomes directly

## Known Stubs

None - all functions are fully implemented and wired.

## Self-Check: PASSED

Verified:
- `app/server/services/outcome-store.ts` — exists
- `app/worker/auto-action.ts` — exists
- `app/tests/server/outcome-store.test.ts` — exists
- `app/tests/worker/auto-action.test.ts` — exists
- Commits `5b7c7d4` and `e23898b` — exist in git log

---
*Phase: 10-auto-action-output-loop*
*Completed: 2026-03-22*
