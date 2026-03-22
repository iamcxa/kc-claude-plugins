---
phase: 10-auto-action-output-loop
plan: 02
subsystem: server
tags: [bun, mcp, anthropic, tdd, outcome-tools]

requires:
  - phase: 10-01
    provides: outcome-store.ts with queryOutcomes/readOutcomes, feedback-collector.ts with checkPrStatus/checkLinearStatus

provides:
  - 3 MCP tools registered in mcp-tools.ts (nw_get_outcomes, nw_get_outcome_status, nw_outcome_summary)
  - 3 Anthropic tool definitions added to NW_TOOLS in chat-manager.ts
  - NW-Claude can answer questions about nightwatch-created PRs and Linear issues

affects:
  - NW-Claude chat interface (can now call outcome tools in responses)
  - MCP server (external MCP clients can access outcome tools)

tech-stack:
  added: []
  patterns:
    - TDD-first MCP tool registration (RED with mock module isolation, GREEN with implementation)
    - Mock accumulation guard: beforeEach mockClear() to prevent inter-test call count contamination
    - Cross-import mock chain: when a new import is added to a tested module, all test files that mock that module's chain need updating

key-files:
  created:
    - app/tests/server/mcp-outcomes.test.ts (8 TDD tests for 3 new MCP tools)
  modified:
    - app/server/services/mcp-tools.ts (added 3 outcome tools + 2 new imports)
    - app/server/services/chat-manager.ts (added 3 Anthropic tool definitions to NW_TOOLS, updated count 12→15)
    - app/tests/server/mcp.test.ts (added outcome-store + feedback-collector mocks, updated tool count 12→15)
    - app/tests/server/chat-tools.test.ts (updated tool count + added 3 new tool name assertions)

key-decisions:
  - "Mock reset with beforeEach mockClear(): inter-test mock call accumulation caused Tests 2-4 to check stale calls[0]; fixed with beforeEach reset per describe block"
  - "mcp.test.ts needed outcome-store + feedback-collector mocks after mcp-tools.ts added those imports — auto-fixed as Rule 1 deviation"
  - "NW_TOOLS comment updated to reflect 15 tools (7 query + 1 search + 4 action + 3 outcome)"

requirements-completed: [OUT-03]

duration: 15min
completed: 2026-03-22
---

# Phase 10 Plan 02: MCP Outcome Tools Summary

**3 MCP tools (nw_get_outcomes, nw_get_outcome_status, nw_outcome_summary) registered for NW-Claude chat awareness of nightwatch-created PRs and Linear issues**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-03-22T08:20:00Z
- **Completed:** 2026-03-22T08:35:00Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- 3 MCP tools registered in mcp-tools.ts with imports from outcome-store.ts and feedback-collector.ts
- nw_get_outcomes supports target/type/status/since filters via queryOutcomes()
- nw_get_outcome_status polls live PR/Linear status using existing checkPrStatus/checkLinearStatus
- nw_outcome_summary returns aggregated stats (total, recent_7d, by_type_status, by_target)
- 3 matching Anthropic tool definitions added to NW_TOOLS in chat-manager.ts
- 8 new tests in mcp-outcomes.test.ts; all pass
- mcp.test.ts updated: new mocks + tool count 12→15 (13 tests still pass)
- chat-tools.test.ts updated: tool count + 3 new name assertions (13 tests still pass)

## Task Commits

Each task was committed atomically:

1. **Task 1: Register 3 outcome MCP tools in mcp-tools.ts** - `a8012a2` (feat)
2. **Task 2: Add 3 Anthropic tool definitions to NW_TOOLS in chat-manager.ts** - `cab755d` (feat)

**Plan metadata:** (docs commit follows)

_Note: TDD used for Task 1 (RED→GREEN). Task 2 had no TDD requirement — updated existing tests to reflect new tool count._

## Files Created/Modified

- `app/server/services/mcp-tools.ts` - Added imports from outcome-store.ts + feedback-collector.ts; registered 3 outcome tools with Zod schemas
- `app/server/services/chat-manager.ts` - Added 3 Anthropic tool definitions to NW_TOOLS array; updated comment 12→15
- `app/tests/server/mcp-outcomes.test.ts` - 8 TDD tests for nw_get_outcomes (4 tests), nw_get_outcome_status (3 tests), nw_outcome_summary (1 test)
- `app/tests/server/mcp.test.ts` - Added outcome-store + feedback-collector mocks; updated tool count assertion 12→15
- `app/tests/server/chat-tools.test.ts` - Updated tool count 12→15; added 3 new tool name assertions

## Decisions Made

- **Mock reset with beforeEach**: Tests 2-4 for nw_get_outcomes were checking `calls[0]` but mock calls accumulated across tests without reset. Added `beforeEach(() => { mockQueryOutcomes.mockClear() })` per describe block to isolate assertions.
- **mcp.test.ts mock expansion**: Adding imports to mcp-tools.ts required updating all test files that mock its transitive dependencies. mcp.test.ts needed `writeYamlFile` in yaml-store mock, plus new mocks for outcome-store.ts and feedback-collector.ts modules.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] mcp.test.ts broken by new mcp-tools.ts imports**
- **Found during:** Task 1 verification (running `bun test app/tests/server/mcp.test.ts`)
- **Issue:** `outcome-store.ts` imports `writeYamlFile` from `yaml-store.ts` — the mcp.test.ts mock for yaml-store.ts didn't include `writeYamlFile`, causing SyntaxError at import time. Also needed mocks for `outcome-store.ts` and `feedback-collector.ts` modules.
- **Fix:** Added `writeYamlFile` to yaml-store mock in mcp.test.ts; added outcome-store mock (`queryOutcomes`, `readOutcomes`, `appendOutcome`); added feedback-collector mock (`checkPrStatus`, `checkLinearStatus`). Updated tool count assertion 12→15.
- **Files modified:** `app/tests/server/mcp.test.ts`
- **Commit:** `a8012a2`

**2. [Rule 1 - Bug] Test mock calls not reset between tests**
- **Found during:** Task 1 TDD GREEN phase
- **Issue:** Tests 2-4 checked `mockQueryOutcomes.mock.calls[0]` but call index 0 was always from Test 1 (mocks accumulate across tests in same describe block). Test 6 called `expect(mockCheckPrStatus).not.toHaveBeenCalled()` but it had been called in Test 5.
- **Fix:** Added `beforeEach` with `.mockClear()` calls to each describe block in mcp-outcomes.test.ts.
- **Files modified:** `app/tests/server/mcp-outcomes.test.ts`
- **Commit:** `a8012a2`

## Issues Encountered

None beyond the auto-fixed items above.

## User Setup Required

None.

## Next Phase Readiness

- Phase 11 (Outcomes page): queryOutcomes API ready; page can call it directly
- NW-Claude is fully aware of outcomes: can answer "what PRs did nightwatch create this week?" by calling nw_get_outcomes with since filter

## Known Stubs

None — all 3 tools are fully implemented and wired to real data sources.

## Self-Check: PASSED

Verified:
- `app/server/services/mcp-tools.ts` — exists, contains `nw_get_outcomes`, `nw_get_outcome_status`, `nw_outcome_summary`
- `app/server/services/chat-manager.ts` — exists, contains 3 new tool definitions in NW_TOOLS
- `app/tests/server/mcp-outcomes.test.ts` — exists, 8 tests all pass
- Commits `a8012a2` and `cab755d` — exist in git log

---
*Phase: 10-auto-action-output-loop*
*Completed: 2026-03-22*
