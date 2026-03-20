# Milestones

## v1.1 Dashboard UX Polish (Shipped: 2026-03-20)

**Phases completed:** 3 phases, 5 plans | **Timeline:** 1 day | **App commits:** 13

**Key accomplishments:**

- Queue awareness: `queued_at` timestamps on all 4 enqueue paths, GET /api/worker/state endpoint, run:failed SSE broadcast
- Toast notification system: signal-backed toast queue with auto-dismiss, z-index layering above dialogs
- Browser notifications: desktop alerts for run completion/failure with user-gesture-gated permission
- Unified polling: `usePoll` hook with `refreshTrigger` signal replacing inline setInterval patterns
- Dead code cleanup: orphaned chat-drawer.ts deleted, phases_completed wired into target-detail, sidebar Add Target functional

---

## v1.0 Nightwatch Dashboard MVP (Shipped: 2026-03-19)

**Phases completed:** 4 phases, 15 plans | **Timeline:** 2 days | **App LOC:** ~8.8K

**Key accomplishments:**

- Two-process architecture: Bun server + worker with native IPC, crash recovery, orphan cleanup
- Dashboard cockpit: target cards, run trigger with real-time log streaming, run history with filters
- Flywheel core: NW-Claude chat with auto-brief, YAML config editor with 4-step validation, feedback calibration
- MCP server: 12 tools exposing nightwatch state to any Claude session
- Flywheel health: indicator sparklines, reject rate charts, per-target health arrows

---
