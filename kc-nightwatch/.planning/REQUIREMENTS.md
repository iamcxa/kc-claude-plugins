# Requirements: Nightwatch Dashboard

**Defined:** 2026-03-21
**Core Value:** The closed-loop feedback flywheel — NW monitors, proposes, learns from feedback, and gets measurably better over time.

## v2.0 Requirements

Requirements for parallel execution + auto-action milestone. Each maps to roadmap phases (continuing from Phase 7).

### Parallel Execution

- [ ] **PARA-01**: Worker supports per-target queue isolation — different targets execute concurrently, same target queues
- [x] **PARA-02**: `activePids` migrated from Set to Map<runId, pid> — cancel targets only the intended run
- [x] **PARA-03**: IPC state shape updated from `current?: Run` to `active: Run[]` — server and frontend see all concurrent runs
- [ ] **PARA-04**: Dashboard shows per-target running status with independent progress when multiple targets execute simultaneously

### Per-Target Scheduling

- [x] **SCHED-04**: Target config supports optional `schedule.interval_hours` override; targets without it inherit global interval
- [ ] **SCHED-05**: Minimum interval enforcement at 10 minutes — scheduler rejects shorter intervals
- [ ] **SCHED-06**: Each target card displays its own "next run at" timestamp based on its individual schedule
- [ ] **SCHED-07**: Add/Edit Target wizard includes schedule configuration step

### Auto-Action

- [ ] **AUTO-01**: Worker auto-creates PR via `gh pr create` when a run produces a branch with code changes
- [ ] **AUTO-02**: Worker auto-creates Linear issue when a run produces improvement signals
- [ ] **AUTO-03**: Dedup check before PR/Linear creation — skip if matching PR/issue already exists
- [ ] **AUTO-04**: Action cards display PR status badge (open/merged/closed) via gh status polling

### Outcomes

- [ ] **OUT-01**: Action cards show clickable PR URL and Linear issue link in run detail
- [ ] **OUT-02**: Dedicated Outcomes page listing all NW-created PRs and Linear issues, filterable by target and status
- [ ] **OUT-03**: NW-Claude chat can answer questions about outcomes ("what PRs did NW create this week?") via new MCP tool
- [ ] **OUT-04**: Phase 0.6 implementation outcome tracking — poll merged PR status, re-measure indicators, record whether intervention was effective

### UI Polish

- [ ] **UI-01**: Fix bottom nav gap (black line between content area and navigation bar)

## v3 Requirements

### Extended Feedback

- **EXTFEED-01**: Slack reaction parsing on reports
- **EXTFEED-02**: PR review comment parsing for nightwatch feedback

## Out of Scope

| Feature | Reason |
|---------|--------|
| Cron expression scheduling | Interval scheduling is sufficient; cron adds complexity without value for single user |
| Auto-merge PRs | Safety net requires human review; auto-create is the boundary |
| Global unbounded parallelism | Per-target isolation prevents API rate limit issues and confused output |
| Outcome analytics charts | Health page already has indicator-level sparklines; outcomes chart layer is v3+ |
| Real-time outcomes push | PR merge is async human action; polling every 60s is fine |
| Per-target auth tokens in UI | Schema prepared, defer implementation; manage via YAML config |
| Mobile responsive design | Desktop-first local tool |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PARA-01 | Phase 9 | Pending |
| PARA-02 | Phase 8 | ✓ Done |
| PARA-03 | Phase 8 | ✓ Done |
| PARA-04 | Phase 11 | Pending |
| SCHED-04 | Phase 8 | ✓ Done |
| SCHED-05 | Phase 9 | Pending |
| SCHED-06 | Phase 11 | Pending |
| SCHED-07 | Phase 11 | Pending |
| AUTO-01 | Phase 10 | Pending |
| AUTO-02 | Phase 10 | Pending |
| AUTO-03 | Phase 10 | Pending |
| AUTO-04 | Phase 11 | Pending |
| OUT-01 | Phase 11 | Pending |
| OUT-02 | Phase 11 | Pending |
| OUT-03 | Phase 10 | Pending |
| OUT-04 | Phase 11 | Pending |
| UI-01 | Phase 11 | Pending |

**Coverage:**
- v2.0 requirements: 17 total
- Mapped to phases: 17
- Unmapped: 0

---
*Requirements defined: 2026-03-21*
*Last updated: 2026-03-21 after roadmap created (v2.0 Phases 8-11)*
