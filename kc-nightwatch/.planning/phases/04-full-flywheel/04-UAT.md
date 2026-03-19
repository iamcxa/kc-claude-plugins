---
status: complete
phase: 04-full-flywheel
source: [04-01-SUMMARY.md, 04-02-SUMMARY.md, 04-03-SUMMARY.md, 04-04-SUMMARY.md]
started: 2026-03-19T07:30:00Z
updated: 2026-03-19T09:30:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Cold Start Smoke Test
expected: Kill any running nightwatch server. Start fresh with `bun run app/server/index.ts`. Server boots without errors, binds to localhost:3200. `curl http://localhost:3200/health` returns JSON with `{ status: 'ok', worker: '...' }`.
result: pass

### 2. Bottom Nav Shows 4 Tabs
expected: Open http://localhost:3201 in browser. Bottom navigation shows exactly 4 tabs: Dashboard, Runs, Health, Config. Clicking Health navigates to the Health page.
result: pass

### 3. Health Page Empty State
expected: Navigate to Health page with no prior run data. Page shows "Gathering data" heading with a message like "Health metrics are available after completed runs." No broken charts or JS errors in console.
result: pass

### 4. MCP Endpoint Responds
expected: POST to /mcp with tools/list returns JSON-RPC response listing 12 MCP tools.
result: pass

### 5. MCP Query Tool Returns State
expected: Call nw_get_targets via MCP returns current targets from nightwatch-targets.yaml.
result: pass

### 6. MCP Action Tool Triggers Run
expected: Call nw_trigger_run with target and mode=dry-run. Response returns run_id and status "queued".
result: pass

### 7. MCP Auth in Remote Mode
expected: Start server with host=0.0.0.0 + auth_token in config. Request without auth header returns 401. With correct token returns 200.
result: pass

### 8. Health Page With Run Data
expected: With completed run data, Health page shows aggregate health summary bar, per-target sparklines, reject rate charts, and acceptance rate.
result: pass

### 9. Sidebar Health Arrows
expected: Dashboard sidebar shows trend arrows next to target names with color coding.
result: pass

### 10. NW-Claude Chat Uses Tools
expected: Open chat drawer, send a message. NW-Claude calls tools and responds with actual state.
result: issue
reported: "Send 按了沒反應，似乎不能按"
severity: major

### 11. NW-Claude Journal Access
expected: In chat drawer, ask about past runs. NW-Claude accesses target-specific journal.
result: skipped
reason: Blocked by Test 10 issue (chatTarget=null prevents Send)

### 12. Linear Status Collection
expected: Without LINEAR_API_KEY, collection gracefully skips (null, no errors). Bad URLs also return null.
result: pass

### 13. MCP Submit Feedback Validates Signal
expected: nw_submit_feedback with non-existent signal_id returns isError. With valid signal_id, feedback recorded.
result: pass

## Summary

total: 13
passed: 10
issues: 1
pending: 0
skipped: 2

## Gaps

- truth: "NW-Claude chat drawer Send button works when opened without a run-complete event"
  status: failed
  reason: "User reported: Send 按了沒反應，似乎不能按"
  severity: major
  test: 10
  root_cause: "app.ts line 28: chatTarget initialized as null. Only set on SSE brief-ready event (line 47-48). ChatDrawer.handleSend() guards on !targetName (chat-drawer.ts line 104). Without a completed run triggering brief-ready, chatTarget stays null and Send is effectively disabled."
  artifacts:
    - path: "app/frontend/app.ts"
      issue: "chatTarget useState(null) — no default target selection"
    - path: "app/frontend/components/chat-drawer.ts"
      issue: "handleSend() returns early when targetName is falsy (line 104)"
  missing:
    - "ChatDrawer should allow selecting a target when opened without brief context"
    - "OR app.ts should default chatTarget to first target from /api/targets on mount"
  debug_session: ""
