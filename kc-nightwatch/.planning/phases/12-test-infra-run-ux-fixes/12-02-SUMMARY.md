---
phase: 12-test-infra-run-ux-fixes
plan: 02
subsystem: api, ui
tags: [hono, bun, preact, log-parser, sse, tdd]

# Dependency graph
requires:
  - phase: 12-test-infra-run-ux-fixes
    provides: "Plan 01 test infrastructure patterns (mock.module, spyOn)"
provides:
  - "GET /api/runs/:id/log endpoint returning raw JSONL lines for completed runs"
  - "parseStreamJsonLine moved to app/shared/log-parser.ts for frontend+worker reuse"
  - "LogStream fetches completed run log via fetch instead of hanging on SSE"
  - "bun --watch in start script for auto-restart on code changes"
affects: [log-stream, run-detail-page, frontend-components, dev-workflow]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Option C for TDD file tests: create fixture files at RUNS_DIR using known test UUID, clean up in afterAll"
    - "Worker module as re-export shim: replace implementation with `export { fn } from '../shared/fn.ts'`"
    - "IPC mock for route tests: mock.module ipc.ts before importing streamRoutes to prevent SSE setup hangs"

key-files:
  created:
    - app/tests/server/log-route.test.ts
    - app/shared/log-parser.ts
  modified:
    - app/worker/log-parser.ts
    - app/server/routes/stream.ts
    - app/frontend/components/log-stream.ts
    - app/package.json

key-decisions:
  - "Option C for test fixture: create log.jsonl at real RUNS_DIR/test-uuid instead of mocking Bun.file — simpler and reliable"
  - "Return { lines: string[] } (raw JSONL) not parsed objects — frontend handles parsing with parseStreamJsonLine"
  - "Worker log-parser.ts becomes a re-export shim to zero-cost preserve existing imports"
  - "Both start and dev scripts use --watch — start for production use, dev kept as alias"

patterns-established:
  - "Shared parser pattern: pure utility in shared/, worker/frontend both import from there"
  - "Completed run fetch pattern: isCompleted useEffect fetches file endpoint; SSE useEffect returns early when isCompleted"

requirements-completed: [RUNUX-01, RUNUX-03]

# Metrics
duration: 15min
completed: 2026-03-24
---

# Phase 12 Plan 02: Log Endpoint + Auto-Restart Summary

**GET /api/runs/:id/log endpoint reading log.jsonl for completed runs, parseStreamJsonLine moved to shared/, and bun --watch auto-restart added to start script**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-03-24T08:05:00Z
- **Completed:** 2026-03-24T08:18:19Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments
- Created 4 behavioral TDD tests for the log route (RED then GREEN)
- Moved parseStreamJsonLine from worker/ to shared/ with zero-friction re-export shim preserving existing imports
- Added GET /api/runs/:id/log to streamRoutes with UUID validation and 404/400 error handling
- Fixed LogStream to fetch /api/runs/:id/log for completed runs (was stuck at "Waiting for output...")
- Enabled bun --watch in start script for auto-restart during development

## Task Commits

Each task was committed atomically:

1. **Task 1: Create behavioral tests for GET /api/runs/:id/log** - `e7483a4` (test)
2. **Task 2: Move parseStreamJsonLine to shared/ and add GET /api/runs/:id/log endpoint** - `652f591` (feat)
3. **Task 3: Fix LogStream to fetch completed run log and enable auto-restart** - `99106aa` (feat)

_Note: Task 1 was TDD RED phase (tests written before implementation), Task 2 made them GREEN._

## Files Created/Modified
- `app/tests/server/log-route.test.ts` - 4 behavioral tests for GET /api/runs/:id/log (200/404/400/raw-strings)
- `app/shared/log-parser.ts` - parseStreamJsonLine moved here from worker/ for frontend+worker reuse
- `app/worker/log-parser.ts` - Replaced with re-export shim: `export { parseStreamJsonLine } from '../shared/log-parser.ts'`
- `app/server/routes/stream.ts` - Added GET /api/runs/:id/log with UUID validation, Bun.file read, { lines } response
- `app/frontend/components/log-stream.ts` - Added parseStreamJsonLine import + completed-run useEffect fetching /api/runs/:id/log
- `app/package.json` - start script now includes --watch flag

## Decisions Made
- Option C for test fixtures: create log.jsonl at real RUNS_DIR/test-uuid path rather than mocking Bun.file — simpler and aligns with how the production route resolves paths
- Return raw JSONL strings in { lines: string[] }, not parsed objects — frontend already has parseStreamJsonLine and the separation keeps the API simple
- Worker log-parser.ts becomes a thin re-export shim — zero cost, zero import breakage, no test changes needed
- Both `start` and `dev` scripts use `--watch` — aligns them for consistency; the `dev` alias remains for backward compatibility

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. The TDD RED/GREEN cycle worked cleanly. The IPC mock approach (mock.module before import) prevented SSE routes from hanging test setup as anticipated in the plan.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- GET /api/runs/:id/log endpoint available for any component needing completed run logs
- parseStreamJsonLine available from shared/ for future frontend components
- Auto-restart enabled — code changes during development no longer require manual server restart
- Plan 03 (target path validation) can proceed independently

## Self-Check: PASSED

All created files found. All task commits verified:
- e7483a4: test(12-02) TDD RED tests
- 652f591: feat(12-02) shared log-parser + endpoint
- 99106aa: feat(12-02) LogStream fix + --watch
- 6b5387f: docs(12-02) SUMMARY + STATE

---
*Phase: 12-test-infra-run-ux-fixes*
*Completed: 2026-03-24*
