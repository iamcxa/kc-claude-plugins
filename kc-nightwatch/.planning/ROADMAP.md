# Roadmap: Nightwatch Dashboard

## Overview

Build a web-based autonomous improvement platform that replaces the launchd cron job with a persistent Bun server + worker architecture. The journey starts with a crash-proof foundation (all 6 critical infrastructure pitfalls solved before any UI), advances to a working cockpit that replaces daily YAML-file inspection, layers in the flywheel differentiators (NW-Claude chat, config editor, feedback calibration, self-assessment), and culminates in the MCP server and health metrics that make the flywheel observable and programmable from any Claude session.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Foundation** - Two-process architecture with all 6 critical pitfalls resolved (completed 2026-03-18)
- [x] **Phase 2: Core Cockpit** - Working dashboard: targets, run trigger, SSE logs, history, scheduler, memory isolation (completed 2026-03-18)
- [ ] **Phase 3: Flywheel Core** - NW-Claude chat, config editor, feedback calibration, self-assessment, baseline measurement
- [ ] **Phase 4: Full Flywheel** - MCP server + flywheel health metrics + deferred chat/feedback capabilities (data-dependent, deferred until Phase 3 produces sufficient feedback data)

## Phase Details

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
**Deferred to Phase 4**: CHAT-04 (NW-MCP access -- requires MCP server), CHAT-05 (NW journal access via MCP -- requires MCP config injection), FEED-03 (nw_submit_feedback MCP tool -- requires MCP server), FEED-05 (Linear issue status collection -- requires Linear MCP integration)
**Success Criteria** (what must be TRUE):
  1. After a run completes, NW-Claude chat panel auto-briefs with a run summary; user can ask follow-up questions; switching target focus prompts a context switch
  2. User opens Config page, unlocks editing, modifies targets.yaml or safety.yaml, and the 4-step validation flow (syntax -> Haiku semantic -> diff -> confirm) runs before any write; config warnings from self-repair.yaml appear inline
  3. User adds a new target via the 4-step wizard (type -> goals -> monitors/respond -> validate) and sees it appear on the dashboard; user can edit or remove targets
  4. User thumbs-up or thumbs-down an action card; feedback is stored per signal; PR merges are collected as implicit feedback; reject rate per indicator adjusts confidence thresholds; feedback trends are written to the NW journal
  5. Run detail shows Phase 3.5 pre-action strategy and Phase 4.5 post-action reflection per action card; Phase 0.5 indicator baselines with quantified values appear in run detail with trend direction
  6. Orchestrator skill produces assessment and baseline data during runs; executor parses structured summary.yaml output
**Plans**: 4 plans

Plans:
- [ ] 03-01-PLAN.md — Phase 3 shared types + global SSE broadcast + chat session manager (Anthropic SDK) + chat routes + ChatDrawer UI + auto-brief wiring
- [ ] 03-02-PLAN.md — Config validation service (4-step flow) + config API routes + YAML editor page (tabs, edit lock, warnings) + AddTargetWizard + Edit/Remove target
- [ ] 03-03-PLAN.md — Feedback store + feedback API routes + ActionCard component with feedback buttons + implicit feedback collector (PR polling) + reject rate calibration
- [ ] 03-04-PLAN.md — Orchestrator skill phases (0.5, 3.5, 4.5) + executor summary parsing + Slack assessment + BaselineCard + ActionCard assessment + human verification

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
**Plans**: TBD

Plans:
- [ ] 04-01: MCP server — Hono /mcp route, Streamable HTTP transport, 10 tools (query + action), token auth for remote mode
- [ ] 04-02: Flywheel health UI — sparkline charts, reject rate charts, acceptance rate, per-target health indicators, aggregate health summary bar

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 3/3 | Complete | 2026-03-18 |
| 2. Core Cockpit | 3/3 | Complete | 2026-03-18 |
| 3. Flywheel Core | 1/4 | In Progress|  |
| 4. Full Flywheel | 0/2 | Not started | - |
