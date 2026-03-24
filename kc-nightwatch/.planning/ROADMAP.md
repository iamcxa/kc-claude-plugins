# Roadmap: Nightwatch Dashboard

## Milestones

- ✅ **v1.0 MVP** — Phases 1-4 (shipped 2026-03-19) → [archive](milestones/v1.0-ROADMAP.md)
- ✅ **v1.1 Dashboard UX Polish** — Phases 5-7 (shipped 2026-03-20) → [archive](milestones/v1.1-ROADMAP.md)
- ✅ **v2.0 Parallel Execution + Auto-Action** — Phases 8-11 (shipped 2026-03-23) → [archive](milestones/v2.0-ROADMAP.md)
- ✅ **v3.0 Worktree Isolation + Extended Feedback** — Phases 12-14 (shipped 2026-03-24) → [archive](milestones/v3.0-ROADMAP.md)
- 🚧 **v4.0 Flywheel Intelligence** — Phases 15-17 (in progress)

## Phases

### 🚧 v4.0 Flywheel Intelligence (In Progress)

**Milestone Goal:** Make the feedback flywheel visible and self-adjusting — users see improvement trends, calibration tables, forge health, and priority-sorted signals

- [ ] **Phase 15: Data Layer Foundations** - Fix fake history, add calibration logic (EMA + sample gate), add forge and signal priority endpoints
- [ ] **Phase 16: Health Page Enrichment** - Wire real sparkline data, add calibration table, add tooltip, add forge results card
- [ ] **Phase 17: Signal Priority Display** - Sort run detail actions by priority score, surface calibration-driven ranking

## Phase Details

### Phase 15: Data Layer Foundations
**Goal**: Real feedback trend data and calibration math are available via server endpoints, replacing all fake stubs
**Depends on**: Phase 14 (v3.0 complete)
**Requirements**: VIZ-01, SIG-02, SIG-03
**Success Criteria** (what must be TRUE):
  1. `GET /api/feedback/trends` returns per-indicator rejection rates bucketed by run_id (not a fake 2-point array)
  2. Calibration data for indicators with fewer than 10 feedback entries returns a null threshold with "Accumulating data (N/10)" message
  3. Calibration threshold is computed using EMA smoothing (α=0.3) instead of raw all-time average
  4. `GET /api/forge/results` returns forge validation status, branch, and details from `nightwatch-self-repair.yaml`
  5. `GET /api/signals/priority` returns indicators ranked by `confidence × (1 - reject_rate)` with a 30-run window cap
**Plans**: TBD
**UI hint**: no

### Phase 16: Health Page Enrichment
**Goal**: The health page shows real sparkline history, a calibration table, hover tooltips, and forge validation results
**Depends on**: Phase 15
**Requirements**: VIZ-02, VIZ-03, FORGE-01
**Success Criteria** (what must be TRUE):
  1. Per-indicator sparklines on the health page show real multi-point rejection rate history (not a flat line from fake data)
  2. A calibration table is visible on the health page with columns for indicator, current threshold, reject rate, and feedback count; rows with fewer than 10 entries show "Accumulating data" instead of a threshold value
  3. Hovering over any sparkline data point shows a tooltip with the exact value and the associated run ID
  4. A forge results card on the health page displays the most recent self-repair run status (pass/fail), branch name, and validation details
**Plans**: TBD
**UI hint**: yes

### Phase 17: Signal Priority Display
**Goal**: Run detail actions are sorted by priority score so the most credible signals appear first
**Depends on**: Phase 15
**Requirements**: SIG-01
**Success Criteria** (what must be TRUE):
  1. Actions in the run detail view are sorted descending by a numeric priority score computed as `confidence_weight × (1 - reject_rate)`
  2. Each action displays its computed priority score alongside the existing confidence label
**Plans**: TBD
**UI hint**: yes

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1-4 | v1.0 | 15/15 | Complete | 2026-03-19 |
| 5-7 | v1.1 | 5/5 | Complete | 2026-03-20 |
| 8-11 | v2.0 | 9/9 | Complete | 2026-03-23 |
| 12-14 | v3.0 | 9/9 | Complete | 2026-03-24 |
| 15. Data Layer Foundations | v4.0 | 0/TBD | Not started | - |
| 16. Health Page Enrichment | v4.0 | 0/TBD | Not started | - |
| 17. Signal Priority Display | v4.0 | 0/TBD | Not started | - |
| **Total** | | **38** | | |
