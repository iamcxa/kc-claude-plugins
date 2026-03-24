# Milestones

## v3.0 Worktree Isolation + Extended Feedback (Shipped: 2026-03-24)

**Phases completed:** 3 phases, 9 plans | **Timeline:** 1 day | **App commits:** 17 | **+2037 / -309 lines**

**Key accomplishments:**

- Test suite reliability: fixed Bun mock.module cross-file contamination (21 false failures → 0) via spyOn conversion
- Completed run log display: GET /api/runs/:id/log endpoint + LogStream fetch for completed runs (no more "Waiting for output...")
- Add Target path validation: server-side 400 for empty/invalid paths + frontend inline error
- Git worktree isolation: each nightwatch run executes in a temporary worktree, leaving target's working directory untouched
- PR review feedback: auto-parses GitHub reviewer verdicts (approve/request-changes/comment) into calibration entries
- Slack reaction feedback: reads 👍/👎/🤔 reactions on nightwatch reports as signal-correlated feedback
- Dashboard feedback display: all 5 sources (user, PR status, Linear, Slack reaction, PR review) visible with source labels and 3-state verdict

---

## v2.0 Parallel Execution + Auto-Action (Shipped: 2026-03-23)

**Phases completed:** 4 phases, 9 plans | **Timeline:** 3 days

**Key accomplishments:**

- Parallel execution: executor runs multiple targets concurrently with configurable max_concurrent_runs
- Auto-action pipeline: nightwatch automatically creates PRs and Linear issues from proposals
- Outcome tracking: PR/Linear outcomes tracked with dedup, status polling, and dashboard display
- Outcomes page: filterable outcome list with status badges, links, and signal correlation

---

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
