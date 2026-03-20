---
phase: 03-flywheel-core
plan: 01
subsystem: chat, api, frontend
tags: [anthropic-sdk, server-sent-events, hono, preact, streaming]

# Dependency graph
requires:
  - phase: 02-core-cockpit
    provides: "Hono server + Preact frontend + SSE fan-out infrastructure (subscribeToRun, fanOutLogEvent)"
provides:
  - "ChatMessage, FeedbackEntry, CalibrationData, ConfigValidationResult types for all Phase 3 plans"
  - "Global SSE broadcast (subscribeGlobal, broadcastGlobal) in server/ipc.ts"
  - "GET /api/events global SSE endpoint for lifecycle events"
  - "Per-target chat sessions via Anthropic SDK streaming (chat-manager.ts)"
  - "Chat API routes: POST /api/chat/:target/message, GET /stream, POST /reset, POST /brief"
  - "ChatDrawer slide-over component with streaming text display"
  - "Auto-brief on run completion: global SSE -> chat drawer auto-opens"
affects:
  - 03-02-feedback-loop
  - 03-03-config-validator

# Tech tracking
tech-stack:
  added:
    - "@anthropic-ai/sdk@0.79.0 — Anthropic SDK for Haiku chat streaming"
  patterns:
    - "Global SSE broadcast via Set<SSEWriter> — mirrors run-scoped SSE pattern from Phase 2"
    - "Per-target chat sessions as Map<string, ChatSession> — same Map pattern as SSE subscribers"
    - "Fire-and-forget POST + SSE response — POST /message returns 202 immediately, response streams via GET /stream"
    - "useRef for EventSource instance — avoids stale closure bugs (RESEARCH.md Pitfall 7)"
    - "Custom event (open-chat) for page-to-app communication — decoupled chat target selection"

key-files:
  created:
    - app/shared/types.ts (extended — ChatMessage, FeedbackEntry, CalibrationData, ConfigValidationResult)
    - app/server/services/chat-manager.ts
    - app/server/routes/chat.ts
    - app/frontend/components/chat-drawer.ts
    - app/tests/server/auto-brief.test.ts
    - app/tests/server/chat.test.ts
  modified:
    - app/server/ipc.ts (subscribeGlobal, broadcastGlobal, handleWorkerMessage run:completed)
    - app/server/routes/stream.ts (GET /api/events)
    - app/server/index.ts (chatRoutes registration)
    - app/frontend/app.ts (global SSE, ChatDrawer, chat toggle)
    - app/frontend/lib/api.ts (sendChatMessage, resetChatSession, briefChat)
    - app/frontend/index.html (--chat-user-bg, --chat-nw-bg CSS tokens)
    - app/package.json + bun.lock (@anthropic-ai/sdk)

key-decisions:
  - "Anthropic SDK used as default chat backend — claude-haiku-4-5 model for cost/speed balance"
  - "Fire-and-forget POST /message + SSE GET /stream — decouples HTTP request lifecycle from LLM streaming"
  - "Global subscribers as Set<SSEWriter> — consistent with per-run SSE fan-out pattern from ipc.ts"
  - "briefChat injects RunSummary into system prompt — chat has full run context without user asking"
  - "open-chat custom event for page-level target switching — pages can open chat without prop drilling"

patterns-established:
  - "Global SSE broadcast pattern: broadcastGlobal(event, data) sends to all connected /api/events clients"
  - "Chat session lifecycle: getOrCreateSession per target, killSession on target switch (STATE.md decision)"
  - "Per-target SSE subscription: subscribeToTarget mirrors subscribeToRun from Phase 2"

requirements-completed: [CHAT-01, CHAT-02, CHAT-03, CHAT-06, CHAT-07]

# Metrics
duration: 15min
completed: 2026-03-18
---

# Phase 3 Plan 01: NW-Claude Chat System Summary

**Anthropic SDK chat drawer with per-target sessions, streaming text via SSE, and auto-brief on run completion wired through global /api/events**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-03-18T10:00:00Z
- **Completed:** 2026-03-18T10:15:32Z
- **Tasks:** 3
- **Files modified:** 13 (7 created, 6 modified)

## Accomplishments

- Phase 3 shared types established (ChatMessage, FeedbackEntry, CalibrationData, ConfigValidationResult) — all future Phase 3 plans consume from here
- Global SSE broadcast infrastructure added to ipc.ts with run:completed auto-broadcasting brief-ready events
- Chat session manager with Anthropic SDK streaming, per-target history, and SSE fan-out to subscribers
- Chat API routes (message/stream/reset/brief) registered in Hono server
- ChatDrawer slide-over with streaming block cursor, history replay on reconnect, per-target isolation
- Auto-brief: run completes -> global SSE -> drawer auto-opens, badge shown if already closed

## Task Commits

Each task was committed atomically:

1. **Task 1: Phase 3 shared types + Global SSE broadcast + install SDK** - `0113964` (feat)
2. **Task 2: Chat session manager service + chat API routes** - `63e0795` (feat)
3. **Task 3: ChatDrawer frontend component + app.ts integration + auto-brief wiring** - `0c8270f` (feat)

## Files Created/Modified

- `app/shared/types.ts` - Extended with ChatMessage, FeedbackEntry, CalibrationData, ConfigValidationResult
- `app/server/ipc.ts` - Added subscribeGlobal, broadcastGlobal; run:completed now broadcasts brief-ready
- `app/server/routes/stream.ts` - Added GET /api/events global SSE endpoint
- `app/server/services/chat-manager.ts` - Per-target chat sessions with Anthropic SDK streaming
- `app/server/routes/chat.ts` - POST /message, GET /stream, POST /reset, POST /brief routes
- `app/server/index.ts` - chatRoutes registered
- `app/frontend/lib/api.ts` - sendChatMessage, resetChatSession, briefChat added
- `app/frontend/components/chat-drawer.ts` - Slide-over chat drawer with streaming display
- `app/frontend/app.ts` - Global SSE listener, chat state, toggle FAB, ChatDrawer integration
- `app/frontend/index.html` - --chat-user-bg, --chat-nw-bg CSS tokens
- `app/tests/server/auto-brief.test.ts` - 3 tests for global SSE broadcast
- `app/tests/server/chat.test.ts` - 6 tests for chat-manager lifecycle

## Decisions Made

- Anthropic SDK as default (STATE.md pre-decision): claude-haiku-4-5 for cost/latency balance
- RunSummary injected into system prompt via /brief endpoint — chat has full context without user asking
- briefChat fires auto-message ("A run just completed. Please summarize...") — proactive briefing, no click needed
- open-chat CustomEvent for page-level target switching — decoupled from prop drilling

## Deviations from Plan

**1. [Rule 2 - Missing Critical] Added RunSummary import to chat.ts**
- **Found during:** Task 2 (chat routes creation)
- **Issue:** chat.ts used `RunSummary` type for `as RunSummary` cast in /brief handler but had no import
- **Fix:** Added `import type { RunSummary } from '../../shared/types.ts'`
- **Files modified:** app/server/routes/chat.ts
- **Verification:** TypeScript resolves correctly; tests pass
- **Committed in:** `63e0795` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 missing type import)
**Impact on plan:** Trivial correctness fix. No scope creep.

## Issues Encountered

None beyond the missing import above.

## User Setup Required

**ANTHROPIC_API_KEY environment variable required** for the chat feature to work at runtime. The Anthropic SDK reads it from `process.env.ANTHROPIC_API_KEY`. Without it, `sendMessage` will throw and error events will be streamed to the drawer. The server still starts without it — error only occurs on first chat message.

Set before starting the server:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

Or add to the nightwatch-app.yaml environment context.

## Next Phase Readiness

- All Phase 3 shared types defined — 03-02 (feedback loop) and 03-03 (config validator) can import directly
- Global SSE infrastructure ready — other Phase 3 plans can call broadcastGlobal for their events
- Chat drawer open-chat custom event established — dashboard run rows can open chat for specific target
- 113 tests green, no regressions

---
*Phase: 03-flywheel-core*
*Completed: 2026-03-18*
