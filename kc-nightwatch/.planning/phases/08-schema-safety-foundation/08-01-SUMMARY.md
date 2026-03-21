---
phase: 08-schema-safety-foundation
plan: 01
subsystem: types
tags: [typescript, zod, ipc, map, safety, parallel-execution]

# Dependency graph
requires: []
provides:
  - "activePids as Map<string, number> keyed by run_id in executor.ts"
  - "cleanupOldRuns with activeRunIds?: Set<string> safety parameter"
  - "Target.schedule?: { interval_hours? } for per-target schedule override"
  - "WorkerToServer state with active: Run[] replacing current?: Run"
  - "AppConfigSchema without max_concurrent_runs (passthrough for backward compat)"
  - "RunSummaryAction.linear_url?: string for Phase 10 auto-action"
  - "MIN_SCHEDULE_INTERVAL_HOURS = 1/6 (10 minutes) in constants"
affects:
  - "09-parallel-queue-scheduler"
  - "10-auto-action-pipeline"
  - "11-outcome-tracking"
  - "worker/index.ts (must update state messages to use active: Run[])"
  - "server/ipc.ts (must update lastWorkerState type)"
  - "frontend/lib/api.ts (must update getWorkerState return type)"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Map<run_id, pid> for per-run PID tracking enabling selective cancel"
    - "Zod .passthrough() for backward-compatible schema migration"
    - "cleanupOldRuns activeRunIds guard pattern for parallel-safe artifact cleanup"

key-files:
  created: []
  modified:
    - app/shared/types.ts
    - app/shared/constants.ts
    - app/worker/executor.ts
    - app/tests/shared/types.test.ts
    - app/tests/shared/constants.test.ts
    - app/tests/worker/executor.test.ts
    - app/tests/worker/artifact-cleanup.test.ts
    - app/server/services/yaml-store.ts
    - app/tests/server/yaml-store.test.ts

key-decisions:
  - "Used .passthrough() on AppConfigSchema instead of .strip() — passthrough lets unknown fields through (old max_concurrent_runs visible in output), strip removes them silently. Either works for backward compat; passthrough chosen to preserve the raw field for debugging"
  - "cleanupOldRuns log message only emits when deleted > 0 — avoids noise when all to-delete runs are active"

patterns-established:
  - "Map<run_id, pid> pattern: any cancel/kill operation on executor should target by run_id, not pid"
  - "activeRunIds guard: always pass new Set(activePids.keys()) to cleanupOldRuns in executeRun finally block"

requirements-completed: [PARA-02, SCHED-04]

# Metrics
duration: 15min
completed: 2026-03-21
---

# Phase 8 Plan 01: Schema Safety Foundation Summary

**activePids migrated from Set<number> to Map<string, number>, AppConfigSchema backward-compatible via .passthrough(), and WorkerToServer state shape updated to active: Run[] for parallel execution foundation**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-03-21T15:15:00Z
- **Completed:** 2026-03-21T15:27:00Z
- **Tasks:** 2
- **Files modified:** 9

## Accomplishments
- activePids is now Map<string, number> — cancel can target a specific run_id without killing other concurrent runs
- cleanupOldRuns accepts activeRunIds set and skips deletion of active run directories (parallel safety)
- AppConfigSchema uses .passthrough() — old YAML with max_concurrent_runs: 1 loads without error
- WorkerToServer state variant uses `active: Run[]` instead of `current?: Run` for multi-run support
- Target interface has optional `schedule?: { interval_hours? }` for per-target interval override
- RunSummaryAction has `linear_url?: string` ready for Phase 10 auto-action pipeline
- MIN_SCHEDULE_INTERVAL_HOURS = 1/6 added to constants (10 minute minimum)

## Task Commits

Each task was committed atomically:

1. **Task 1: Migrate types, schema, and constants** - `79af96d` (feat)
2. **Task 2: Migrate activePids Set→Map and cleanupOldRuns safety guard** - `bd31a36` (feat)

_Both tasks used TDD (RED → GREEN). No REFACTOR pass needed._

## Files Created/Modified
- `app/shared/types.ts` - Target.schedule, WorkerToServer active:Run[], AppConfigSchema passthrough, RunSummaryAction.linear_url
- `app/shared/constants.ts` - Added MIN_SCHEDULE_INTERVAL_HOURS = 1/6
- `app/worker/executor.ts` - activePids Map, killAllActive with [runId, pid], cleanupOldRuns with activeRunIds
- `app/tests/shared/types.test.ts` - Updated AppConfigSchema tests, added Target.schedule and RunSummaryAction.linear_url tests, WorkerToServer active[] test
- `app/tests/shared/constants.test.ts` - Added MIN_SCHEDULE_INTERVAL_HOURS test
- `app/tests/worker/executor.test.ts` - Updated all Set API → Map API, added cancel isolation test
- `app/tests/worker/artifact-cleanup.test.ts` - Added activeRunIds skip tests
- `app/server/services/yaml-store.ts` - Removed max_concurrent_runs from DEFAULT_APP_CONFIG
- `app/tests/server/yaml-store.test.ts` - Updated tests to match new schema behavior

## Decisions Made
- Used .passthrough() on AppConfigSchema — unknown fields pass through (old max_concurrent_runs preserved in output), not silently stripped. Both options work for backward compat; passthrough was chosen to keep raw field visible for debugging.
- cleanupOldRuns log only emits when deleted > 0 to avoid noise when all candidates are active runs.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] yaml-store.ts DEFAULT_APP_CONFIG referenced removed max_concurrent_runs field**
- **Found during:** Task 1 (Migrate types, schema, and constants)
- **Issue:** `yaml-store.ts` DEFAULT_APP_CONFIG still had `max_concurrent_runs: 1` which would cause TypeScript type error since AppConfig no longer has that field
- **Fix:** Removed `max_concurrent_runs: 1` from DEFAULT_APP_CONFIG; updated yaml-store.test.ts to remove assertion on `config.max_concurrent_runs` and replace "throws on invalid max_concurrent_runs" test with "accepts YAML with max_concurrent_runs: 2 (backward compat)" test
- **Files modified:** `app/server/services/yaml-store.ts`, `app/tests/server/yaml-store.test.ts`
- **Verification:** `bun test tests/server/yaml-store.test.ts` — 5/5 pass
- **Committed in:** 79af96d (part of Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 — bug directly caused by schema change)
**Impact on plan:** Essential fix. Removing max_concurrent_runs from the schema without updating the default config would leave the codebase inconsistent.

## Issues Encountered
- Pre-existing test isolation issue: `executor-feedback-wiring.test.ts` fails when run in parallel with the full test suite due to module caching conflict for `appendFeedback` from `feedback-store.ts`, but passes in isolation. This is an out-of-scope pre-existing issue. Logged to deferred-items.

## Next Phase Readiness
- All downstream phases (9-11) can now import the correct types
- Phase 9 (parallel queue scheduler) can use activePids.keys() for activeRunIds
- Phase 9 must update `worker/index.ts` to send `active: Run[]` in state messages
- Phase 9 must update `server/ipc.ts` lastWorkerState type to use `active: Run[]`
- Phase 10 (auto-action) can use `RunSummaryAction.linear_url` field
- Phase 10 can use `Target.schedule?.interval_hours` for per-target scheduling logic

## Self-Check: PASSED

- FOUND: app/shared/types.ts
- FOUND: app/shared/constants.ts
- FOUND: app/worker/executor.ts
- FOUND: 08-01-SUMMARY.md
- FOUND commit: 79af96d (Task 1)
- FOUND commit: bd31a36 (Task 2)

---
*Phase: 08-schema-safety-foundation*
*Completed: 2026-03-21*
