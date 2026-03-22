# Roadmap: Nightwatch Dashboard

## Milestones

- ✅ **v1.0 MVP** — Phases 1-4 (shipped 2026-03-19) → [archive](milestones/v1.0-ROADMAP.md)
- ✅ **v1.1 Dashboard UX Polish** — Phases 5-7 (shipped 2026-03-20) → [archive](milestones/v1.1-ROADMAP.md)
- 🚧 **v2.0 Parallel Execution + Auto-Action** — Phases 8-11 (in progress)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1-4) — SHIPPED 2026-03-19</summary>

- [x] Phase 1: Foundation (3/3 plans) — completed 2026-03-18
- [x] Phase 2: Core Cockpit (3/3 plans) — completed 2026-03-18
- [x] Phase 3: Flywheel Core (5/5 plans) — completed 2026-03-18
- [x] Phase 4: Full Flywheel (4/4 plans) — completed 2026-03-19

</details>

<details>
<summary>✅ v1.1 Dashboard UX Polish (Phases 5-7) — SHIPPED 2026-03-20</summary>

- [x] Phase 5: Schema + Server Infrastructure (1/1 plan) — completed 2026-03-20
- [x] Phase 6: Frontend Wiring (3/3 plans) — completed 2026-03-20
- [x] Phase 7: Cleanup (1/1 plan) — completed 2026-03-20

</details>

### v2.0 Parallel Execution + Auto-Action (In Progress)

**Milestone Goal:** Enable parallel target execution with per-target scheduling, auto-create PRs and Linear issues from run results, and surface outcomes in a dedicated page and NW-Claude chat.

- [x] **Phase 8: Schema + Safety Foundation** - Type system and IPC shape changes that unblock all downstream work — completed 2026-03-21
- [x] **Phase 9: Worker Parallel Execution + Scheduling** - Per-target queue isolation and multi-timer scheduler — completed 2026-03-22
- [x] **Phase 10: Auto-Action Output Loop** - Worker auto-creates PRs and Linear issues; server exposes outcomes API and MCP tools — completed 2026-03-22
- [x] **Phase 11: Frontend Outcomes + UI Polish** - Dashboard parallel status, Outcomes page, action card links, schedule display, nav fix — completed 2026-03-22

## Phase Details

### Phase 8: Schema + Safety Foundation
**Goal**: All shared types, IPC state shape, and schema migrations that every downstream phase depends on are in place and correct
**Depends on**: Phase 7 (complete)
**Requirements**: PARA-02, PARA-03, SCHED-04
**Success Criteria** (what must be TRUE):
  1. Cancel for a single run kills only that run's process — other concurrent runs continue unaffected
  2. Server and frontend can observe an array of active runs (not a single current run) from worker IPC state
  3. Target interface has an optional `schedule.interval_hours` field; per-target override behavior ships in Phase 9
  4. `app-config.yaml` files containing the old `max_concurrent_runs` field load without startup error
**Plans:** 2 plans
Plans:
- [x] 08-01-PLAN.md — Types, schema, constants, and activePids Map migration
- [x] 08-02-PLAN.md — IPC state shape consumers (worker, server, frontend) and cancel handler

### Phase 9: Worker Parallel Execution + Scheduling
**Goal**: Different targets execute concurrently in the worker, same-target runs queue behind each other, and each target has its own independently ticking scheduler
**Depends on**: Phase 8
**Requirements**: PARA-01, SCHED-05
**Success Criteria** (what must be TRUE):
  1. Two different targets triggered simultaneously both begin executing without one waiting for the other to finish
  2. Two runs for the same target queue — the second run does not start until the first completes
  3. A target with `interval_hours: 0.1` (6 minutes) is rejected at config save time with a clear error message
  4. One target's scheduler firing does not reset or delay any other target's countdown
  5. A target with `schedule.interval_hours` set uses its own interval; targets without it inherit the global interval
**Plans:** 2 plans
Plans:
- [x] 09-01-PLAN.md — Per-target queue isolation in worker/index.ts (parallel execution model)
- [x] 09-02-PLAN.md — Per-target multi-timer scheduler and server-side min interval validation

### Phase 10: Auto-Action Output Loop
**Goal**: The worker automatically creates PRs and Linear issues after runs that produce actionable output, skipping creation when duplicates already exist, and NW-Claude can answer questions about outcomes via MCP
**Depends on**: Phase 8 (schema); Phase 9 (worker state shape for server IPC consumption)
**Requirements**: AUTO-01, AUTO-02, AUTO-03, OUT-03
**Success Criteria** (what must be TRUE):
  1. After a run that proposes code changes, a PR appears on GitHub without any manual step — the PR URL is stored in the run record
  2. After a run that classifies a signal as a Linear issue, a Linear issue appears without any manual step — the issue URL is stored in the run record
  3. Running the same target twice on the same unresolved signal does not create a second PR or Linear issue
  4. Asking NW-Claude "what PRs did nightwatch create this week?" returns a list of outcomes with links
**Plans:** 2 plans
Plans:
- [x] 10-01-PLAN.md — Outcome store and auto-action post-run hook with dedup
- [x] 10-02-PLAN.md — MCP outcome tools and chat manager tool definitions

### Phase 11: Frontend Outcomes + UI Polish
**Goal**: The dashboard visually reflects parallel execution, all run detail views surface PR and Linear links, a dedicated Outcomes page aggregates all created PRs and issues, and the nav gap visual bug is gone
**Depends on**: Phase 10
**Requirements**: PARA-04, SCHED-06, SCHED-07, AUTO-04, OUT-01, OUT-02, OUT-04, UI-01
**Success Criteria** (what must be TRUE):
  1. When two targets are running simultaneously, each target card shows its own live progress indicator independently
  2. Each target card and detail panel shows "next run at HH:MM" based on that target's own schedule
  3. An action card for a PR shows a badge indicating open, merged, or closed status (updated via polling)
  4. Clicking a PR link or Linear issue link in an action card opens the correct URL in a new tab
  5. The Outcomes page lists all NW-created PRs and Linear issues, filterable by target and status
  6. The Add/Edit Target wizard includes a schedule configuration step where interval can be set
  7. The black line between content area and nav bar is gone
**Plans:** 3 plans
Plans:
- [x] 11-01-PLAN.md — Outcomes API routes, Outcomes page, bottom nav 5th tab, app router, nav gap fix
- [x] 11-02-PLAN.md — Sidebar parallel dots, dashboard summary line, target-detail schedule, wizard schedule step
- [x] 11-03-PLAN.md — Action card status badges + URLs, runs.ts outcome pre-fetch, full phase visual checkpoint

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Foundation | v1.0 | 3/3 | Complete | 2026-03-18 |
| 2. Core Cockpit | v1.0 | 3/3 | Complete | 2026-03-18 |
| 3. Flywheel Core | v1.0 | 5/5 | Complete | 2026-03-18 |
| 4. Full Flywheel | v1.0 | 4/4 | Complete | 2026-03-19 |
| 5. Schema + Server Infrastructure | v1.1 | 1/1 | Complete | 2026-03-20 |
| 6. Frontend Wiring | v1.1 | 3/3 | Complete | 2026-03-20 |
| 7. Cleanup | v1.1 | 1/1 | Complete | 2026-03-20 |
| 8. Schema + Safety Foundation | v2.0 | 2/2 | Complete | 2026-03-21 |
| 9. Worker Parallel Execution + Scheduling | v2.0 | 2/2 | Complete | 2026-03-22 |
| 10. Auto-Action Output Loop | v2.0 | 2/2 | Complete | 2026-03-22 |
| 11. Frontend Outcomes + UI Polish | v2.0 | 3/3 | Complete | 2026-03-22 |
