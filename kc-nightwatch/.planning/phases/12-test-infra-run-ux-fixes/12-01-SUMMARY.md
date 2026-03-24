---
phase: 12-test-infra-run-ux-fixes
plan: 01
subsystem: testing
tags: [bun-test, spyOn, mock-module, test-contamination, test-isolation]

requires: []
provides:
  - Full test suite passes in full-suite mode (bun test) with 0 failures
  - All internal module mocks converted from mock.module to spyOn + mockRestore
  - Two previously unidentified contaminating files (log-route.test.ts, target-validation.test.ts) also fixed
affects: [all future test work in phase 12+]

tech-stack:
  added: []
  patterns:
    - "spyOn pattern: import * as module from '...', spyOn(module, 'fn').mockResolvedValue(...), mockRestore() in afterEach"
    - "Never use mock.module() for internal modules that have downstream real-I/O test files — use spyOn instead"
    - "Class-level mocks (@anthropic-ai/sdk, MCP SDK) still require mock.module — no downstream victims"

key-files:
  created: []
  modified:
    - app/tests/server/mcp.test.ts
    - app/tests/server/mcp-outcomes.test.ts
    - app/tests/server/chat-tools.test.ts
    - app/tests/server/health-api.test.ts
    - app/tests/server/outcomes-api.test.ts
    - app/tests/server/log-route.test.ts
    - app/tests/server/target-validation.test.ts

key-decisions:
  - "Convert ALL internal module mock.module() calls to spyOn (not just the 5 listed in plan — found 2 additional contaminating files)"
  - "target-validation.test.ts: spyOn withWriteLock to be a no-op avoids TARGETS_YAML_PATH constant mocking problem"
  - "log-route.test.ts: only subscribeToRun + subscribeGlobal from ipc.ts need spyOn (stream.ts only imports those two)"
  - "chat-tools.test.ts: refresh spy in resetMocks() function instead of separate beforeEach/afterEach (matches existing test reset pattern)"

requirements-completed: [TEST-01]

duration: 15min
completed: 2026-03-24
---

# Phase 12 Plan 01: Test Mock Contamination Fix Summary

**All 299 Bun tests pass in full-suite run after converting 7 test files from mock.module to spyOn+mockRestore, eliminating permanent module registry pollution**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-03-24T08:15:00Z
- **Completed:** 2026-03-24T08:25:01Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments

- Converted 7 test files from `mock.module()` to `spyOn()` + `mockRestore()` for all internal module mocks
- Full test suite went from 21 failures + 8 errors to **299 pass, 0 fail**
- Previously contaminated test files (yaml-store, outcome-store, auto-action, linear-status, ipc, sse, api, health) all green in full-suite mode
- Only remaining `mock.module()` calls are for external SDKs with class constructors (`@anthropic-ai/sdk`, `@modelcontextprotocol/sdk`) — legitimate and have no downstream victims

## Task Commits

1. **Task 1: Convert mcp.test.ts and mcp-outcomes.test.ts** - `28b1886` (fix)
2. **Task 2: Convert remaining contaminating files and verify full suite** - `3dff0f3` (fix)

## Files Created/Modified

- `app/tests/server/mcp.test.ts` - Removed 5 mock.module calls, added namespace imports + spyOn in beforeEach/afterEach
- `app/tests/server/mcp-outcomes.test.ts` - Same pattern as mcp.test.ts for outcome tools
- `app/tests/server/chat-tools.test.ts` - Converted yaml-store to spyOn (kept SDK mocks), spy reset in resetMocks()
- `app/tests/server/health-api.test.ts` - Converted run-store + feedback-store to spyOn with closures over control variables
- `app/tests/server/outcomes-api.test.ts` - Converted outcome-store to spyOn
- `app/tests/server/log-route.test.ts` - Converted ipc.ts to spyOn (subscribeToRun + subscribeGlobal only)
- `app/tests/server/target-validation.test.ts` - Converted yaml-store + config-validator + ipc to spyOn; withWriteLock spy executes fn() callback

## Decisions Made

- Used `spyOn` with `mockImplementation` for functions that need closure-based state (health-api control variables `mockRunsResult`, `mockRunMap`, `mockCalibration`)
- For `target-validation.test.ts`: spied on `withWriteLock` to execute the fn() callback (not a pure no-op) to preserve behavioral correctness while avoiding `TARGETS_YAML_PATH` constant override limitation
- For `log-route.test.ts`: only spy on the two functions `stream.ts` actually imports from `ipc.ts` (subscribeToRun + subscribeGlobal) — not the full module

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed 2 additional contaminating files not listed in plan**
- **Found during:** Task 2 (full suite run still had 21 failures after converting 5 planned files)
- **Issue:** `target-validation.test.ts` and `log-route.test.ts` also used `mock.module()` on internal modules (`yaml-store.ts` and `ipc.ts` respectively), poisoning `yaml-store.test.ts`, `outcome-store.test.ts`, and `ipc.test.ts`
- **Fix:** Converted both files using the same spyOn pattern; identified that only the 2 functions `stream.ts` actually imports from `ipc.ts` needed spying
- **Files modified:** `app/tests/server/log-route.test.ts`, `app/tests/server/target-validation.test.ts`
- **Verification:** `bun test` — 299 pass, 0 fail
- **Committed in:** `3dff0f3` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - bug — additional contaminating files not listed in plan)
**Impact on plan:** Essential for achieving the stated goal (full suite passes). The RESEARCH.md file actually listed these two files as contaminating but they were omitted from the PLAN.md task list. Auto-fix restored correctness.

## Issues Encountered

None beyond the deviation above.

## Known Stubs

None — all test files now use real mock data through spyOn, no hardcoded stub returns that would prevent plan goal.

## Next Phase Readiness

- TEST-01 complete: full test suite green, safe to run `bun test` at any point
- Plans 12-02 and 12-03 can proceed — test suite is a reliable baseline now

---
*Phase: 12-test-infra-run-ux-fixes*
*Completed: 2026-03-24*
