# Requirements: Nightwatch Dashboard

**Defined:** 2026-03-18
**Core Value:** The closed-loop feedback flywheel — NW monitors, proposes, learns from feedback, and gets measurably better over time.

## v1 Requirements

### Foundation

- [ ] **FOUND-01**: Server + worker two-process architecture with Bun native IPC
- [x] **FOUND-02**: Graceful shutdown (SIGINT/SIGTERM) with child process cleanup
- [x] **FOUND-03**: Worker crash recovery — server detects disconnect, cleans orphan processes
- [x] **FOUND-04**: Socket/PID file cleanup on startup (prevent EADDRINUSE)
- [x] **FOUND-05**: Timeout enforcement per run (from safety.yaml max_runtime_minutes)
- [x] **FOUND-06**: Orphaned safehouse+claude process detection and kill on startup
- [x] **FOUND-07**: App bootstrap — create default nightwatch-app.yaml on first start
- [x] **FOUND-08**: Run artifact directory with rolling cleanup (keep last 50)

### Dashboard

- [x] **DASH-01**: Target cards showing name, type, north star, last run summary, health indicator
- [x] **DASH-02**: Per-target context menu (Run / Run dry / Edit / Chat / Remove)
- [x] **DASH-03**: Global Run All / Run All (dry-run) buttons
- [x] **DASH-04**: Schedule status bar (interval, next run countdown, last run summary)
- [x] **DASH-05**: Navigation between Dashboard, Runs, and Config pages

### Execution

- [x] **EXEC-01**: Manual run trigger with mode selection (production/dry-run)
- [x] **EXEC-02**: Custom prompt field on manual trigger (saved to run artifacts)
- [x] **EXEC-03**: Self-repair toggle on manual trigger
- [x] **EXEC-04**: Per-target safehouse policy generation (read-only vs read-write by mode)
- [x] **EXEC-05**: `claude -p --output-format stream-json` spawning with target cwd
- [x] **EXEC-06**: Real-time log streaming from worker to browser via SSE
- [x] **EXEC-07**: Phase progress extraction from stream-json (Phase 0-5 detection)
- [x] **EXEC-08**: Run cancellation (SIGTERM to claude -p child)
- [x] **EXEC-09**: Execution queue with max concurrency 1

### Scheduling

- [x] **SCHED-01**: Interval scheduler (every N hours, configurable)
- [x] **SCHED-02**: Webhook endpoint (POST /api/webhook with optional target + mode)
- [x] **SCHED-03**: Schedule state persisted in nightwatch-app.yaml

### Run History

- [x] **HIST-01**: Run history list with status, trigger type, duration, action counts
- [x] **HIST-02**: Run detail view with phase progress, log, action cards
- [x] **HIST-03**: Filter runs by status (failed, with actions) and target
- [x] **HIST-04**: Live view during execution (auto-switch from history to live)

### Config

- [ ] **CONF-01**: YAML editor for targets.yaml (read-only by default, unlock to edit)
- [ ] **CONF-02**: YAML editor for safety.yaml
- [ ] **CONF-03**: Edit lock (must explicitly enable editing)
- [ ] **CONF-04**: 4-step save validation (static → semantic via Haiku → diff → confirm)
- [ ] **CONF-05**: Config warnings panel (from self-repair.yaml, inline markers)
- [ ] **CONF-06**: Add Target wizard (4 steps: type → goals → monitors/respond → validate)
- [ ] **CONF-07**: Edit Target (same wizard, pre-filled)
- [ ] **CONF-08**: Remove Target (confirm dialog)

### Chat

- [x] **CHAT-01**: NW-Claude chat panel (right side of dashboard)
- [x] **CHAT-02**: Auto-brief after run completes (spawn Claude with run summary as context)
- [x] **CHAT-03**: Bidirectional Claude session (`--input-format stream-json`, API fallback)
- [ ] **CHAT-04**: NW-Claude has NW-MCP access (trigger runs, query state, submit feedback)
- [ ] **CHAT-05**: NW-Claude has target-specific NW journal access
- [x] **CHAT-06**: Per-target chat focus ("Chat about this" from target card)
- [x] **CHAT-07**: Session lifecycle (persist until close/reset, switch context prompt on new run)

### Feedback

- [ ] **FEED-01**: Dashboard feedback buttons (thumbs up/down) per action card
- [ ] **FEED-02**: Feedback API endpoint (POST /api/feedback with signal_id, verdict, reason)
- [ ] **FEED-03**: MCP feedback tool (nw_submit_feedback)
- [ ] **FEED-04**: PR status collection (merged = accepted, closed = rejected)
- [ ] **FEED-05**: Linear issue status collection
- [ ] **FEED-06**: Reject rate calibration (per indicator, adjust confidence threshold)
- [ ] **FEED-07**: Feedback trends written to NW journal (slow learning path)

### Self-Assessment

- [ ] **ASSESS-01**: Phase 3.5 pre-action strategy assessment (in orchestrator skill)
- [ ] **ASSESS-02**: Phase 4.5 post-action reflection assessment (in orchestrator skill)
- [ ] **ASSESS-03**: Assessment display in run detail (per action card)
- [ ] **ASSESS-04**: Assessment in Slack report

### Measurement

- [ ] **MEAS-01**: Phase 0.5 indicator baseline measurement (quantified values per indicator)
- [ ] **MEAS-02**: Indicator trend tracking (previous_value + trend direction)
- [ ] **MEAS-03**: Baseline display in run detail

### Memory

- [x] **MEM-01**: Per-target NW journal directory (~/.claude/nightwatch/memory/{target}/)
- [x] **MEM-02**: NW journal MCP injection into worker's claude -p sessions
- [x] **MEM-03**: Journal isolation (no cross-target memory)

### MCP Server

- [ ] **MCP-01**: Hono route at /mcp using Streamable HTTP transport
- [ ] **MCP-02**: Query tools (nw_get_targets, nw_get_latest_run, nw_get_run, nw_get_proposals, nw_get_schedule)
- [ ] **MCP-03**: Action tools (nw_trigger_run, nw_submit_feedback, nw_update_schedule)
- [ ] **MCP-04**: Token auth for remote mode

### Flywheel Health

- [ ] **HEALTH-01**: Indicator trend sparklines (last 10 runs per indicator)
- [ ] **HEALTH-02**: Reject rate chart per indicator
- [ ] **HEALTH-03**: Acceptance rate (proposals accepted / total)
- [ ] **HEALTH-04**: Per-target health indicator on target cards (up/stable/down arrow)
- [ ] **HEALTH-05**: Aggregate health summary bar

### Security

- [x] **SEC-01**: Localhost binding by default (127.0.0.1)
- [x] **SEC-02**: Optional remote mode (0.0.0.0) with required token auth
- [x] **SEC-03**: Token auth on all API/MCP/WebSocket endpoints in remote mode

## v2 Requirements

### Proposal Pipeline

- **PROP-01**: Accept proposal from dashboard → spawn implementation run
- **PROP-02**: Implementation PR creation (non-draft, based on accepted proposal)
- **PROP-03**: Forge re-validation after implementation (plugin targets)
- **PROP-04**: nw_implement_proposal MCP tool
- **PROP-05**: nw_run_targeted MCP tool (focus on specific issue)

### Outcome Tracking

- **OUT-01**: Phase 0.6 implementation outcome checking (merged PR → indicator delta)
- **OUT-02**: Outcome display in run detail (before/after/effective)
- **OUT-03**: Outcome data feeding back into NW journal

### Extended Feedback

- **EXTFEED-01**: Slack reaction parsing on reports
- **EXTFEED-02**: PR review comment parsing for nightwatch feedback

## Out of Scope

| Feature | Reason |
|---------|--------|
| Cron expression scheduling | Interval scheduling is sufficient; cron adds complexity without value for single user |
| File watch triggers | Interval + manual + webhook covers all use cases |
| Multi-user auth / RBAC | Single user tool; token auth is enough for remote access |
| Cross-machine sync | Local-only; Slack reports cover remote awareness |
| channels.yaml / language.yaml editing | Low-frequency edits, CLI is fine |
| Custom MCP/plugin marketplace per target | Use user-scope MCPs + project .mcp.json auto-discovery |
| Per-target auth tokens | Schema prepared in config, defer implementation |
| Mobile responsive design | Desktop-first local tool |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FOUND-01 | Phase 1 | Complete |
| FOUND-02 | Phase 1 | Complete |
| FOUND-03 | Phase 1 | Complete |
| FOUND-04 | Phase 1 | Complete |
| FOUND-05 | Phase 1 | Complete |
| FOUND-06 | Phase 1 | Complete |
| FOUND-07 | Phase 1 | Complete |
| FOUND-08 | Phase 1 | Complete |
| SEC-01 | Phase 1 | Complete |
| SEC-02 | Phase 1 | Complete |
| SEC-03 | Phase 1 | Complete |
| DASH-01 | Phase 2 | Complete |
| DASH-02 | Phase 2 | Pending |
| DASH-03 | Phase 2 | Complete |
| DASH-04 | Phase 2 | Complete |
| DASH-05 | Phase 2 | Pending |
| EXEC-01 | Phase 2 | Complete |
| EXEC-02 | Phase 2 | Complete |
| EXEC-03 | Phase 2 | Complete |
| EXEC-04 | Phase 2 | Complete |
| EXEC-05 | Phase 2 | Complete |
| EXEC-06 | Phase 2 | Complete |
| EXEC-07 | Phase 2 | Complete |
| EXEC-08 | Phase 2 | Complete |
| EXEC-09 | Phase 2 | Complete |
| SCHED-01 | Phase 2 | Complete |
| SCHED-02 | Phase 2 | Complete |
| SCHED-03 | Phase 2 | Complete |
| HIST-01 | Phase 2 | Complete |
| HIST-02 | Phase 2 | Complete |
| HIST-03 | Phase 2 | Complete |
| HIST-04 | Phase 2 | Pending |
| MEM-01 | Phase 2 | Complete |
| MEM-02 | Phase 2 | Complete |
| MEM-03 | Phase 2 | Complete |
| CONF-01 | Phase 3 | Pending |
| CONF-02 | Phase 3 | Pending |
| CONF-03 | Phase 3 | Pending |
| CONF-04 | Phase 3 | Pending |
| CONF-05 | Phase 3 | Pending |
| CONF-06 | Phase 3 | Pending |
| CONF-07 | Phase 3 | Pending |
| CONF-08 | Phase 3 | Pending |
| CHAT-01 | Phase 3 | Complete |
| CHAT-02 | Phase 3 | Complete |
| CHAT-03 | Phase 3 | Complete |
| CHAT-04 | Phase 3 | Pending |
| CHAT-05 | Phase 3 | Pending |
| CHAT-06 | Phase 3 | Complete |
| CHAT-07 | Phase 3 | Complete |
| FEED-01 | Phase 3 | Pending |
| FEED-02 | Phase 3 | Pending |
| FEED-03 | Phase 3 | Pending |
| FEED-04 | Phase 3 | Pending |
| FEED-05 | Phase 3 | Pending |
| FEED-06 | Phase 3 | Pending |
| FEED-07 | Phase 3 | Pending |
| ASSESS-01 | Phase 3 | Pending |
| ASSESS-02 | Phase 3 | Pending |
| ASSESS-03 | Phase 3 | Pending |
| ASSESS-04 | Phase 3 | Pending |
| MEAS-01 | Phase 3 | Pending |
| MEAS-02 | Phase 3 | Pending |
| MEAS-03 | Phase 3 | Pending |
| MCP-01 | Phase 4 | Pending |
| MCP-02 | Phase 4 | Pending |
| MCP-03 | Phase 4 | Pending |
| MCP-04 | Phase 4 | Pending |
| HEALTH-01 | Phase 4 | Pending |
| HEALTH-02 | Phase 4 | Pending |
| HEALTH-03 | Phase 4 | Pending |
| HEALTH-04 | Phase 4 | Pending |
| HEALTH-05 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 73 total
- Mapped to phases: 73
- Unmapped: 0

---
*Requirements defined: 2026-03-18*
*Last updated: 2026-03-18 after roadmap creation — all 73 requirements mapped*
