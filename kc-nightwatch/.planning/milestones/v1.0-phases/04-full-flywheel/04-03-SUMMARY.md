---
phase: 04-full-flywheel
plan: 03
subsystem: api
tags: [chat, mcp, anthropic-sdk, tool-use, typescript, bun, tdd]

requires:
  - phase: 04-full-flywheel
    plan: 01
    provides: "/mcp HTTP endpoint via WebStandardStreamableHTTPServerTransport — chat-manager MCP client connects here"
  - phase: 03-flywheel-core
    plan: 01
    provides: "chat-manager.ts with Anthropic SDK chat session management — this plan extends sendMessage"

provides:
  - "NW_TOOLS: 12 Anthropic tool schemas (7 query + 1 search + 4 action) exported from chat-manager.ts"
  - "sendMessage() with full tool_use loop: tools passed to messages.create, tool_use blocks routed to MCP client"
  - "getMcpClient(): lazy MCP client per session via StreamableHTTPClientTransport with bearer auth"
  - "MAX_TOOL_ROUNDS=10 guard prevents infinite tool_use loops"
  - "killSession() closes MCP client (best-effort) on session cleanup"
  - "13 passing tests covering tool schemas, tool_use routing, multi-round loops, lazy init, cleanup, streaming"

affects:
  - "NW-Claude chat sessions — now have full tool access for querying state, triggering runs, submitting feedback"

tech-stack:
  added:
    - "@modelcontextprotocol/sdk (client/index.js, client/streamableHttp.js) — MCP client in chat-manager"
  patterns:
    - "Hybrid Anthropic+MCP: messages.create with tools array + StreamableHTTPClientTransport for tool_use routing"
    - "Lazy MCP client per session: initialize on first tool_use, reuse for session lifetime, close on killSession"
    - "Tool_use loop with MAX_TOOL_ROUNDS guard: while(rounds < 10) { create → process → if tool_use continue }"
    - "Tool result injection: role:user content:[{type:tool_result, tool_use_id, content}] cast via unknown as string"

key-files:
  created:
    - app/tests/server/chat-tools.test.ts
  modified:
    - app/server/services/chat-manager.ts (NW_TOOLS + getMcpClient + full tool_use sendMessage loop)

key-decisions:
  - "12 unique tools (not 13): Plan spec says 13 but 7+1+4=12 unique tools — duplicate nw_get_config_warnings removed (per existing STATE.md decision from 04-01)"
  - "messages.create() replaces messages.stream() — tool_use protocol requires non-streaming response to inspect stop_reason and content blocks"
  - "Mock reset order in tests: killAllSessions() BEFORE mockClear() prevents close() call counts bleeding across tests"
  - "loadOrCreateAppConfig used for port/token discovery in getMcpClient — consistent with existing server pattern"

patterns-established:
  - "Pattern: Mock reset order — call killAllSessions() before mockClear() when mocks track method calls on session-owned objects"
  - "Pattern: Tool_use loop — process all content blocks per round, collect tool_results, push tool_result messages, loop if stop_reason===tool_use"

requirements-completed: [CHAT-04, CHAT-05]

duration: 7min
completed: 2026-03-19
---

# Phase 04 Plan 03: NW-Claude MCP Tool Integration Summary

**NW-Claude chat wired to 12 MCP tools via Anthropic tool_use protocol with lazy MCP client per session and MAX_TOOL_ROUNDS guard**

## Performance

- **Duration:** ~7 min
- **Started:** 2026-03-19T03:12:30Z
- **Completed:** 2026-03-19T03:19:44Z
- **Tasks:** 1 of 1 (TDD: 2 commits — test RED + feat GREEN)
- **Files modified:** 2

## Accomplishments
- Exported `NW_TOOLS` const with 12 Anthropic tool schemas from `chat-manager.ts` — all 12 MCP server tools mirrored as Anthropic tools
- Replaced `messages.stream()` with `messages.create()` + tool_use loop — enables stop_reason inspection and multi-round tool calls
- `getMcpClient()` lazy-initializes `StreamableHTTPClientTransport` per session with bearer auth from config, reused across messages
- `killSession()` extended to close MCP client on session cleanup (best-effort)
- 13 tests covering all specified behaviors — all pass; full suite: 163 pass (vs 152 baseline), 5 fail (all pre-existing)

## Task Commits

1. **Task 1 RED: failing tests for NW_TOOLS + tool_use routing** - `667f9f7` (test)
2. **Task 1 GREEN: wire NW-Claude chat to MCP tools** - `eb2cdc5` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified
- `app/server/services/chat-manager.ts` — Added NW_TOOLS array (12 tools), getMcpClient(), tool_use loop in sendMessage(), MCP client cleanup in killSession()/killAllSessions()
- `app/tests/server/chat-tools.test.ts` — 13 tests: NW_TOOLS shape, tool routing, multi-round loop, MAX_TOOL_ROUNDS guard, lazy init, killSession cleanup, streaming deltas

## Decisions Made
- **12 tools not 13**: Plan spec mentions 13 but the tool breakdown (7+1+4) equals 12 unique tools. Confirmed with STATE.md decision from Plan 04-01: "Plan spec says 13 tools but breakdown totals 12 (7+1+4) — implemented 12 specified tools". Tests updated accordingly.
- **messages.create() not stream()**: Tool_use protocol requires inspecting `stop_reason` and `content` blocks in a non-streaming response. The streaming API doesn't expose these fields in the same way. Replaced the previous stream-based implementation entirely.
- **Mock reset order fix**: `resetMocks()` must call `killAllSessions()` BEFORE `mockMcpClose.mockClear()` to prevent close() call counts from leaking into subsequent tests via `beforeEach`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Duplicate nw_get_config_warnings entry removed**
- **Found during:** Task 1 (GREEN phase)
- **Issue:** Plan's NW_TOOLS code sample had a 13th entry that was a duplicate of nw_get_config_warnings (index 5). The dedup comment in the plan implied intentional de-duplication at runtime, but it's cleaner to have exactly 12 unique entries in the array definition.
- **Fix:** Wrote clean 12-entry NW_TOOLS array without any duplicate entries. Tests updated to expect 12 (matching STATE.md decision from 04-01).
- **Files modified:** app/server/services/chat-manager.ts, app/tests/server/chat-tools.test.ts
- **Verification:** Tests pass with NW_TOOLS.length === 12
- **Committed in:** eb2cdc5 (Task 1 GREEN commit)

**2. [Rule 1 - Bug] Test mock reset order fix**
- **Found during:** Task 1 (GREEN phase — test debugging)
- **Issue:** `resetMocks()` called `killAllSessions()` AFTER `mockMcpClose.mockClear()`. Sessions with MCP clients from previous tests would call `close()` AFTER the count was cleared, causing the next test's close count to be off by 1 (received: 2, expected: 1).
- **Fix:** Moved `killAllSessions()` BEFORE `mockMcpClose.mockClear()` in `resetMocks()`.
- **Files modified:** app/tests/server/chat-tools.test.ts
- **Verification:** `killSession closes MCP client` test passes (1 close call, not 2)
- **Committed in:** eb2cdc5 (Task 1 GREEN commit)

---

**Total deviations:** 2 auto-fixed (2 bugs: 1 duplicate array entry, 1 test mock ordering)
**Impact on plan:** Both auto-fixes are correctness issues. Production code changes are minimal (12 vs 13 tools — matches MCP server's actual tool count). No scope creep.

## Issues Encountered
- Pre-existing test failures (5): `writeFeedbackTrends` not exported, `appendFeedback`/`appendRun` SyntaxErrors from module mock cross-contamination — these existed before this plan (verified via git stash). Out of scope. Baseline was 152 pass / 16 fail; after this plan: 163 pass / 5 fail (improvement).

## Next Phase Readiness
- NW-Claude sessions now have full tool access: can query runs, targets, schedule, config warnings, journals; trigger runs; submit feedback; update schedule
- CHAT-04 and CHAT-05 requirements complete
- Phase 04 is now complete — all 3 plans (MCP server, health page, chat MCP integration) done

---
*Phase: 04-full-flywheel*
*Completed: 2026-03-19*
