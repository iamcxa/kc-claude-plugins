---
phase: 12-test-infra-run-ux-fixes
plan: 03
subsystem: ui, api, testing
tags: [bun-test, hono, preact, path-validation, tdd, existsSync]

# Dependency graph
requires:
  - phase: 12-test-infra-run-ux-fixes
    provides: context on validation patterns in config.ts (D-04/D-05/D-06)

provides:
  - Server-side path validation (400) for POST /api/config/targets/add
  - Server-side path validation (400) for PUT /api/config/targets/:name
  - Frontend inline validation error and disabled Next button when path is empty
  - Behavioral tests (7) for all path validation scenarios

affects:
  - add-target-wizard.ts (consumer: all target creation/editing flows)
  - config.ts (add/edit target API)

# Tech tracking
tech-stack:
  added: [node:fs existsSync]
  patterns:
    - Defense-in-depth validation at both UI and API layers (mirrors Phase 9 D-12~D-14 interval validation)
    - TDD with Bun mock.module — mock withWriteLock as (file, fn) => fn() to match real 2-arg signature
    - Temp file setup (writeFileSync) in beforeAll for PUT tests that need pre-existing target data

key-files:
  created:
    - app/tests/server/target-validation.test.ts
  modified:
    - app/server/routes/config.ts
    - app/frontend/components/add-target-wizard.ts

key-decisions:
  - "Use existsSync (not Bun.file().exists()) for path validation — synchronous, works for both files and directories"
  - "PUT path validation guarded by `if (targetPath !== undefined)` — only validate when path explicitly provided in payload"
  - "Show Path is required error always when path empty on step 1 (not touch-gated) — consistent with existing name UX pattern"

patterns-established:
  - "TDD mock.module signature must match the real function signature exactly — withWriteLock takes (file, fn) not just (fn)"
  - "PUT tests need a real targets YAML file pre-populated in beforeAll to avoid 404 not-found responses"

requirements-completed: [RUNUX-02]

# Metrics
duration: 15min
completed: 2026-03-24
---

# Phase 12 Plan 03: Path Validation (RUNUX-02) Summary

**Defense-in-depth path validation via existsSync: Add Target wizard disables Next + shows inline error, server returns 400 for empty or non-existent paths in both Add and Edit flows, with 7 passing behavioral tests**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-03-24T08:15:00Z
- **Completed:** 2026-03-24T08:30:00Z
- **Tasks:** 2 (Task 1: TDD RED tests, Task 2: implementation + GREEN)
- **Files modified:** 3

## Accomplishments

- Created 7 behavioral tests for path validation (POST Add + PUT Edit, covering empty/missing/non-existent/valid path)
- Server-side: `existsSync` check returns 400 with `path is required` or `path does not exist: <path>` for both Add and Edit routes
- Frontend: label changed from "Path (optional)" to "Path", inline error shown when empty, Next disabled when path empty

## Task Commits

1. **Task 1: Create behavioral tests for target path validation (TDD RED)** - `28a838f` (test)
2. **Task 2: Add path validation to wizard frontend and server endpoints (GREEN)** - `e9788bb` (feat)

## Files Created/Modified

- `app/tests/server/target-validation.test.ts` - 7 behavioral tests for path validation in Add and Edit flows
- `app/server/routes/config.ts` - Added `existsSync` import and path validation in POST + PUT handlers
- `app/frontend/components/add-target-wizard.ts` - Label change, inline error, disabled Next, buildTarget path always included

## Decisions Made

- Used `existsSync` from `node:fs` (synchronous) rather than `Bun.file().exists()` (async) — cleaner inline in handlers, works for directories
- PUT handler guards path validation with `if (targetPath !== undefined)` — edit payload may omit path if unchanged
- Inline "Path is required" shown always when path is empty on step 1, not touch-gated — matches existing name UX (disabled Next is the signal)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed withWriteLock mock signature to match real 2-arg signature**
- **Found during:** Task 1 (TDD RED test execution)
- **Issue:** Initial mock used `(fn) => fn()` but real `withWriteLock` takes `(file, fn)` — mock received `'targets'` as `fn` and called it as a function, throwing `TypeError: fn is not a function`
- **Fix:** Updated mock to `(_file: string, fn: () => Promise<unknown>) => fn()`
- **Files modified:** app/tests/server/target-validation.test.ts
- **Verification:** Mock works, tests fail correctly for the right reason (400 not returned yet)
- **Committed in:** 28a838f (Task 1 TDD RED commit, updated before commit)

**2. [Rule 1 - Bug] Added beforeAll with pre-populated targets YAML for PUT tests**
- **Found during:** Task 1 (TDD RED test execution — initial run)
- **Issue:** PUT tests returned 404 (not found) instead of 400 (validation error) because the temp targets file was empty and the route returned 404 before reaching path validation
- **Fix:** Added `beforeAll(() => writeFileSync(tmpTargetsYaml, 'targets:\n  my-target:\n    type: plugin\n    path: /tmp\n'))` so `my-target` exists for PUT tests
- **Files modified:** app/tests/server/target-validation.test.ts
- **Verification:** PUT tests now reach path validation code and fail for the correct reason (200 returned instead of 400)
- **Committed in:** 28a838f (Task 1 TDD RED commit, updated before commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1 - Bug in test setup)
**Impact on plan:** Both fixes were in the test scaffolding, not production code. No scope creep.

## Issues Encountered

- Linter (biome) intercepted the first edit to `config.ts` that added `existsSync` import and removed it before the PUT validation code was applied. Resolved by reading the current state of the file before re-editing.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- RUNUX-02 complete: path is now required in Add Target and enforced on server (defense-in-depth per D-04/D-05/D-06)
- Phase 12 plans 01 and 02 cover RUNUX-01 (completed run log display) and RUNUX-03 (bun --watch auto-restart)
- Phase 12 complete when all 3 plans done and test suite contamination fixed (plan 01)

---
*Phase: 12-test-infra-run-ux-fixes*
*Completed: 2026-03-24*
