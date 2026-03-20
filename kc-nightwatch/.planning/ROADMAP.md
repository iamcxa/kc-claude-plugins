# Roadmap: Nightwatch Dashboard

## Milestones

- ✅ **v1.0 MVP** - Phases 1-4 (shipped 2026-03-19)
- 🚧 **v1.1 Dashboard UX Polish** - Phases 5-7 (in progress)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1-4) - SHIPPED 2026-03-19</summary>

### Phase 1: Foundation
**Goal**: The two-process app starts, stays up across crashes, and handles every process-lifecycle failure mode before any feature work starts
**Depends on**: Nothing (first phase)
**Requirements**: FOUND-01, FOUND-02, FOUND-03, FOUND-04, FOUND-05, FOUND-06, FOUND-07, FOUND-08, SEC-01, SEC-02, SEC-03
**Success Criteria** (what must be TRUE):
  1. Server and worker start together; worker connects to server via Bun native IPC and sends a heartbeat every 30 seconds; server marks worker offline if heartbeat is >90s stale (3 missed)
  2. Killing the worker process causes the server to detect disconnect, clean up orphaned safehouse+claude processes (pgrep scan), and enter exponential backoff restart (2s/5s/15s); after 3rd crash enters read-only mode
  3. Restarting the server after a crash starts cleanly — Bun native IPC eliminates socket file/EADDRINUSE; orphan scan covers stale state from prior crash
  4. A claude run that completes (result event received) is force-killed within 10 seconds even if MCP connections keep the process alive
  5. The app binds to 127.0.0.1 by default; remote mode requires explicit opt-in and a token on all API endpoints
**Plans**: 3 plans

Plans:
- [x] 01-01-PLAN.md — Project scaffold, shared types/constants/logger, Bun native IPC, heartbeat + liveness detection, GET /health (completed 2026-03-18, 13 tests)
- [x] 01-02-PLAN.md — Worker executor: safehouse chain, PID tracking, force-kill after result event, timeout enforcement, artifact rolling cleanup (completed 2026-03-18)
- [x] 01-03-PLAN.md — Server startup: orphan cleanup, crash recovery backoff, graceful shutdown, yaml-store bootstrap, Bearer token security gate (completed 2026-03-18, 20 tests)

### Phase 2: Core Cockpit
**Goal**: Users can monitor targets, trigger runs with real-time log streaming, view run history, and control the interval scheduler — replacing the current cron + YAML-file workflow entirely
**Depends on**: Phase 1
**Requirements**: DASH-01, DASH-02, DASH-03, DASH-04, DASH-05, EXEC-01, EXEC-02, EXEC-03, EXEC-04, EXEC-05, EXEC-06, EXEC-07, EXEC-08, EXEC-09, SCHED-01, SCHED-02, SCHED-03, HIST-01, HIST-02, HIST-03, HIST-04, MEM-01, MEM-02, MEM-03
**Success Criteria** (what must be TRUE):
  1. User opens the dashboard and sees target cards with name, type, north star, last run summary, and health indicator; a schedule status bar shows interval, next run countdown, and last run summary
  2. User triggers a run (production or dry-run) with an optional custom prompt; the log panel shows real-time output line by line via SSE; user can cancel the run and it terminates cleanly
  3. User navigates to Run History, filters by status or target, opens a run detail with phase progress (Phase 0-5 detected), log, and action cards
  4. User enables the interval scheduler, sets hours, and the scheduler persists across server restarts; webhook endpoint accepts POST requests to trigger a run
  5. Each run executes in an isolated agent-safehouse context with per-target policy (read-only vs read-write by mode); max 1 concurrent run; second trigger queues rather than overlapping
**Plans**: 3 plans

Plans:
- [x] 02-01-PLAN.md — Shared type extensions (Target, RunSummary, ParsedLogEvent) + REST API routes (targets, runs, webhook, schedule) + SSE fan-out wiring + run-store service + yaml-store extensions (completed 2026-03-18)
- [x] 02-02-PLAN.md — Worker execution queue (max concurrency 1) + target path resolution + interval scheduler + cancel implementation + NW memory isolation (ensureNwMemoryDir, nw-journal MCP injection) (completed 2026-03-18)
- [x] 02-03-PLAN.md — Frontend: Preact+HTM vendor setup, import map, app router, dashboard master-detail layout, trigger modal, log-stream SSE component, run history/detail pages, config stub + human verification (completed 2026-03-18, human-verified)

### Phase 3: Flywheel Core
**Goal**: Users can interact with NW-Claude about run results, edit config safely, submit structured feedback that calibrates future runs, and see per-run self-assessment and indicator baselines — turning nightwatch from automation into a learning system
**Depends on**: Phase 2
**Requirements**: CONF-01, CONF-02, CONF-03, CONF-04, CONF-05, CONF-06, CONF-07, CONF-08, CHAT-01, CHAT-02, CHAT-03, CHAT-06, CHAT-07, FEED-01, FEED-02, FEED-04, FEED-06, FEED-07, ASSESS-01, ASSESS-02, ASSESS-03, ASSESS-04, MEAS-01, MEAS-02, MEAS-03
**Success Criteria** (what must be TRUE):
  1. After a run completes, NW-Claude chat panel auto-briefs with a run summary; user can ask follow-up questions; switching target focus prompts a context switch
  2. User opens Config page, unlocks editing, modifies targets.yaml or safety.yaml, and the 4-step validation flow (syntax -> Haiku semantic -> diff -> confirm) runs before any write; config warnings from self-repair.yaml appear inline
  3. User adds a new target via the 4-step wizard (type -> goals -> monitors/respond -> validate) and sees it appear on the dashboard; user can edit or remove targets
  4. User thumbs-up or thumbs-down an action card; feedback is stored per signal; PR merges are collected as implicit feedback; reject rate per indicator adjusts confidence thresholds; feedback trends are written to the NW journal
  5. Run detail shows Phase 3.5 pre-action strategy and Phase 4.5 post-action reflection per action card; Phase 0.5 indicator baselines with quantified values appear in run detail with trend direction
  6. Orchestrator skill produces assessment and baseline data during runs; executor parses structured summary.yaml output
**Plans**: 5 plans

Plans:
- [x] 03-01-PLAN.md — Phase 3 shared types + global SSE broadcast + chat session manager (Anthropic SDK) + chat routes + ChatDrawer UI + auto-brief wiring (completed 2026-03-18)
- [x] 03-02-PLAN.md — Config validation service (4-step flow) + config API routes + YAML editor page (tabs, edit lock, warnings) + AddTargetWizard + Edit/Remove target (completed 2026-03-18)
- [x] 03-03-PLAN.md — Feedback store + feedback API routes + ActionCard component with feedback buttons + implicit feedback collector (PR polling) + reject rate calibration (completed 2026-03-18)
- [x] 03-04-PLAN.md — Orchestrator skill phases (0.5, 3.5, 4.5) + executor summary parsing + Slack assessment + BaselineCard + ActionCard assessment + human verification (completed 2026-03-18)
- [x] 03-05-PLAN.md — Gap closure: wire orphaned feedback collector + trend writer into executor.ts, update REQUIREMENTS.md status (completed 2026-03-18)

### Phase 4: Full Flywheel
**Goal**: The entire nightwatch state is queryable and actionable from any Claude session via MCP, and flywheel health is visible as charts and trends — completing the closed-loop improvement system
**Depends on**: Phase 3
**Requirements**: MCP-01, MCP-02, MCP-03, MCP-04, HEALTH-01, HEALTH-02, HEALTH-03, HEALTH-04, HEALTH-05, CHAT-04, CHAT-05, FEED-03, FEED-05
**Success Criteria** (what must be TRUE):
  1. A Claude session configured with the NW MCP server can call nw_get_targets, nw_get_latest_run, nw_get_proposals, and nw_get_schedule and receive current state; it can call nw_trigger_run, nw_submit_feedback, and nw_update_schedule and see the effects in the dashboard
  2. Remote mode is enabled via config; a request to any API, MCP, or WebSocket endpoint without the token is rejected with 401; a request with the correct token succeeds
  3. Flywheel health page shows indicator trend sparklines (last 10 runs), reject rate chart per indicator, acceptance rate, and per-target health arrow (up/stable/down); aggregate health summary bar reflects overall trend
  4. NW-Claude chat has NW-MCP access to trigger runs, query state, and submit feedback (CHAT-04); NW-Claude has target-specific NW journal access (CHAT-05)
  5. nw_submit_feedback MCP tool allows NW-Claude to submit feedback programmatically (FEED-03); Linear issue status collection for implicit feedback (FEED-05)
**Plans**: 4 plans

Plans:
- [x] 04-01-PLAN.md — MCP server: shared types (health), McpServer factory with 13 tools (7 query + 1 search + 4 action + 1 stub), WebStandard Streamable HTTP transport, Linear GraphQL integration (completed 2026-03-19)
- [x] 04-02-PLAN.md — Flywheel Health: health API aggregation, sparkline SVG components, reject rate line charts, acceptance rate, per-target sidebar arrows, bottom nav Health tab, human verification (completed 2026-03-19)
- [x] 04-03-PLAN.md — Chat MCP integration: NW tool schemas in Anthropic API, MCP client for tool_use routing, multi-turn tool loop, journal access via MCP tools (completed 2026-03-19)
- [x] 04-04-PLAN.md — Gap closure: fix reject rate chart rendering (HEALTH-02) -- per-indicator reject rate data in health API, fix frontend to pass multi-value arrays to LineChart (completed 2026-03-19)

</details>

### v1.1 Dashboard UX Polish (In Progress)

**Milestone Goal:** Improve run lifecycle visibility and clean up stale v1.0 UI debt — queued_at timestamps, queue display, toast/notification system, auto-refresh consistency, and dead code removal.

#### Phase 5: Schema + Server Infrastructure
**Goal**: The data foundation is in place — queued_at timestamp exists on all runs and server exposes the queue state endpoint and run:failed SSE event that frontend phases depend on
**Depends on**: Phase 4
**Requirements**: QUEUE-01
**Success Criteria** (what must be TRUE):
  1. Every newly enqueued run has a `queued_at` ISO timestamp set at enqueue time, visible in the run store, across all 4 trigger paths (manual POST /api/runs, webhook POST /api/webhook, scheduler interval, __all__ expansion)
  2. GET /api/worker/state returns the current queue snapshot (pending runs with their target + queued_at) and is callable from the browser without side effects
  3. When a run fails, the global SSE channel broadcasts a `run:failed` event with runId and targetId — matching the existing `run:complete` pattern
**Plans**: 1 plan

Plans:
- [x] 05-01-PLAN.md — queued_at field on Run type + all 4 enqueue paths, GET /api/worker/state endpoint, run:failed SSE broadcast

#### Phase 6: Frontend Wiring
**Goal**: Users can see queue depth, trigger time, and position for every run; they receive immediate toast feedback on trigger actions; the Runs page stays current during active runs; and background completions surface as browser notifications
**Depends on**: Phase 5
**Requirements**: QUEUE-02, QUEUE-03, QUEUE-04, NOTIF-01, NOTIF-02, NOTIF-03, POLL-01, POLL-02
**Success Criteria** (what must be TRUE):
  1. Run list and run detail both show queued_at as a relative time (e.g., "queued 2m ago") alongside started_at; queued runs that have not started yet show their trigger time
  2. Triggering a run from any trigger point (dashboard button, context menu, Run All) immediately shows a toast "Run queued for {target}" at top-right; if the trigger fails, a red toast shows the error message
  3. Target detail panel shows "2 queued" count for the selected target when runs are waiting; each queued run shows its position ("#2 in queue")
  4. The Runs page auto-refreshes every 5s when active or queued runs exist and stops polling when all runs are in a terminal state — identical behavior to the dashboard
  5. When a run completes or fails while the browser tab is in the background, a desktop notification appears; first-time users are prompted for permission via a user gesture (not on page load)
**Plans**: 3 plans

Plans:
- [ ] 06-01-PLAN.md — Toast system (use-toast.ts + toast.ts), usePoll hook, api.getWorkerState() method
- [ ] 06-02-PLAN.md — App root toast/notification wiring, dashboard trigger toasts + queue state + AddTargetWizard, target-detail queue display, sidebar Add Target button
- [ ] 06-03-PLAN.md — Runs page auto-refresh polling and queued_at time display

#### Phase 7: Cleanup
**Goal**: Dead code is deleted and the sidebar Add Target button works — leaving a codebase with no orphan files, no dead variables, and no placeholder buttons
**Depends on**: Phase 6
**Requirements**: CLEAN-01, CLEAN-02, CLEAN-03
**Success Criteria** (what must be TRUE):
  1. `chat-drawer.ts` no longer exists in the codebase; `bun typecheck` exits 0 after its deletion (no dangling imports)
  2. The `phases` variable in `target-detail.ts` reads from the actual run summary rather than always returning `[]`; the target detail panel displays phase progress correctly
  3. Clicking "Add Target" in the sidebar opens the AddTargetWizard — same wizard accessible from the Config page
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Foundation | v1.0 | 3/3 | Complete | 2026-03-18 |
| 2. Core Cockpit | v1.0 | 3/3 | Complete | 2026-03-18 |
| 3. Flywheel Core | v1.0 | 5/5 | Complete | 2026-03-18 |
| 4. Full Flywheel | v1.0 | 4/4 | Complete | 2026-03-19 |
| 5. Schema + Server Infrastructure | v1.1 | 1/1 | Complete | 2026-03-20 |
| 6. Frontend Wiring | 3/3 | Complete   | 2026-03-20 | - |
| 7. Cleanup | v1.1 | 0/TBD | Not started | - |
