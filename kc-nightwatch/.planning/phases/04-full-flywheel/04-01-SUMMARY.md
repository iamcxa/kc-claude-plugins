---
phase: 04-full-flywheel
plan: 01
subsystem: api
tags: [mcp, linear, graphql, typescript, bun, hono, zod, mcp-sdk]

requires:
  - phase: 03-flywheel-core
    provides: feedback-store, run-store, yaml-store, ipc, auth middleware — all called by MCP tools
  - phase: 02-core-cockpit
    provides: Run, RunSummary, FeedbackEntry types; server/index.ts route registration pattern

provides:
  - MCP server factory (createMcpServer) with 12 registered tools via @modelcontextprotocol/sdk
  - /mcp HTTP endpoint (POST + GET) via WebStandardStreamableHTTPServerTransport
  - Real Linear GraphQL implementation replacing Phase 3 checkLinearStatus placeholder
  - HealthIndicatorData and TargetHealthData types for Phase 4 health API
  - nw_submit_feedback validates signal_id from run history before recording
  - Token auth on /mcp via existing tokenAuth middleware (auto-protected in remote mode)

affects:
  - 04-02 (health-api and frontend will use TargetHealthData, HealthIndicatorData)
  - 04-03 (chat-manager MCP client connects to /mcp endpoint created here)

tech-stack:
  added:
    - "@modelcontextprotocol/sdk@1.27.1 — official MCP SDK with WebStandardStreamableHTTPServerTransport"
  patterns:
    - "Stateless MCP: new WebStandardStreamableHTTPServerTransport + createMcpServer() per request — no session tracking"
    - "MCP SDK internal API: _registeredTools is plain object (not Map); server._serverInfo has name — verified v1.27.1"
    - "registerTool() with raw Zod v3 shape (not z.object() wrapper) — SDK AnySchema = z3.ZodTypeAny | z4.$ZodType"
    - "setWorkerStatus() for test state control instead of mock.module — avoids ESM binding capture issue"

key-files:
  created:
    - app/server/services/mcp-tools.ts
    - app/server/routes/mcp.ts
    - app/tests/server/mcp.test.ts
    - app/tests/worker/linear-status.test.ts
  modified:
    - app/shared/types.ts (HealthIndicatorData + TargetHealthData appended)
    - app/worker/feedback-collector.ts (checkLinearStatus real implementation)
    - app/server/index.ts (mcpRoutes import + registration)

key-decisions:
  - "MCP SDK _registeredTools is a plain object in v1.27.1 (not Map) — tests use Object.keys() not tools.size"
  - "Plan spec says 13 tools but breakdown lists 12 (7+1+4) — implemented 12 actual specified tools"
  - "Test workerStatus via real ipc.ts setWorkerStatus() — mock.module getter works but ESM named binding is more reliable"
  - "nw_submit_feedback validates signal_id in run history before appendFeedback (per CONTEXT.md locked decision)"

patterns-established:
  - "Pattern: MCP tool testing — import createMcpServer, access _registeredTools[name].handler directly for unit tests"
  - "Pattern: Linear GraphQL auth — Authorization: apiKey (no Bearer prefix for personal API keys)"

requirements-completed: [MCP-01, MCP-02, MCP-03, MCP-04, FEED-03, FEED-05]

duration: 8min
completed: 2026-03-19
---

# Phase 04 Plan 01: MCP Server + Linear Integration Summary

**MCP server exposing 12 nightwatch tools via WebStandardStreamableHTTPServerTransport on /mcp, with real Linear GraphQL status check replacing the Phase 3 placeholder**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-03-19T03:00:00Z
- **Completed:** 2026-03-19T03:08:53Z
- **Tasks:** 2 of 2
- **Files modified:** 7

## Accomplishments
- Created `createMcpServer()` factory with 12 tools (7 query, 1 search, 4 action) using @modelcontextprotocol/sdk v1.27.1
- Wired `/mcp` route via WebStandardStreamableHTTPServerTransport — stateless, per-request server+transport creation
- Replaced `checkLinearStatus` placeholder with real GraphQL fetch (api.linear.app/graphql, no Bearer prefix)
- Added `HealthIndicatorData` and `TargetHealthData` types to shared/types.ts for Phase 4 health API
- `nw_submit_feedback` validates `signal_id` exists in run history before recording (CONTEXT.md locked decision)
- 27 new tests: 20 MCP tool tests + 7 Linear status tests — all pass

## Task Commits

1. **Task 1: Shared types + MCP tool factory + Linear GraphQL** - `31d0805` (feat)
2. **Task 2: MCP route + server index wiring** - `12648c6` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified
- `app/server/services/mcp-tools.ts` — McpServer factory with 12 tools, Zod v3 inputSchema, all store integrations
- `app/server/routes/mcp.ts` — Hono /mcp route via WebStandardStreamableHTTPServerTransport
- `app/server/index.ts` — Added mcpRoutes import and registration (after auth middleware line 113, at line 160)
- `app/shared/types.ts` — Appended HealthIndicatorData and TargetHealthData interfaces
- `app/worker/feedback-collector.ts` — Real checkLinearStatus GraphQL implementation
- `app/tests/server/mcp.test.ts` — 20 tests covering all critical tool behaviors with mock stores
- `app/tests/worker/linear-status.test.ts` — 7 tests covering URL parsing, state mapping, error handling

## Decisions Made
- MCP SDK v1.27.1 `_registeredTools` is a plain object, not Map — tests use `Object.keys(tools)` not `tools.size`
- Plan states "13 tools" but the breakdown (7+1+4) totals 12 — implemented 12 specified tools
- Test `workerStatus` via real `setWorkerStatus()` from ipc.ts rather than `mock.module` — ESM binding more reliable
- `nw_submit_feedback` calls `getRun(run_id)` then checks `summary.per_target[target].actions` for signal_id match

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] MCP SDK internal API discovery**
- **Found during:** Task 1 (TDD GREEN phase)
- **Issue:** Test helper used `_registeredTools` as a Map (`.get()` method) and `_serverInfo` at wrong path — both assumptions were incorrect for SDK v1.27.1
- **Fix:** Inspected SDK via Node.js REPL: `_registeredTools` is plain object, `server._serverInfo` not `_serverInfo`
- **Files modified:** tests/server/mcp.test.ts (test helper + createMcpServer describe block)
- **Verification:** 20 tests pass after fix
- **Committed in:** 31d0805 (Task 1 commit)

**2. [Rule 1 - Bug] Worker offline test — mock.module getter not live for named ESM imports**
- **Found during:** Task 1 (TDD GREEN phase)
- **Issue:** Setting `mockWorkerStatus = 'offline'` in test didn't affect `workerStatus` read in mcp-tools.ts because ESM named bindings from mock.module work differently
- **Fix:** Removed ipc.ts from mock.module; used real ipc.ts with `setWorkerStatus('offline')` / `setWorkerStatus('online')` for test control
- **Files modified:** tests/server/mcp.test.ts
- **Verification:** nw_trigger_run offline test passes
- **Committed in:** 31d0805 (Task 1 commit)

---

**Total deviations:** 2 auto-fixed (2 bugs discovered during TDD GREEN phase)
**Impact on plan:** Both fixes needed for correct test behavior. Production code unchanged by deviations.

## Issues Encountered
- Pre-existing test failures (3): `writeFeedbackTrends` not exported from feedback-store.ts — these existed before this plan (confirmed via git stash check). Out of scope.

## Next Phase Readiness
- `/mcp` endpoint is live and protected by existing tokenAuth middleware
- All 12 tools return MCP-compliant `{ content: [{ type: 'text', text: ... }] }` format
- Linear integration ready — activate by setting `LINEAR_API_KEY` in `.env`
- Phase 4 Plan 2 (health API + frontend) can use `TargetHealthData` and `HealthIndicatorData` types immediately
- Phase 4 Plan 3 (chat MCP client) connects to the `/mcp` endpoint built here

---
*Phase: 04-full-flywheel*
*Completed: 2026-03-19*
