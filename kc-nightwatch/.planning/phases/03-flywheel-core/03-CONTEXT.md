# Phase 3: Flywheel Core - Context

**Gathered:** 2026-03-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Turn nightwatch from automation into a learning system. Users can interact with NW-Claude about run results, edit config with validation, submit structured feedback that calibrates future runs, and see per-run self-assessment and indicator baselines. Four subsystems: Chat, Config Editor, Feedback Pipeline, Self-Assessment + Measurement.

</domain>

<decisions>
## Implementation Decisions

### Chat Panel Placement & Behavior
- Right-side slide-over drawer (overlay, ~400px), not a new page or inline panel
- Drawer can be opened from any page (Dashboard, Runs, Config) — use `position: fixed` overlay
- Does not displace or shrink main content
- Run completion triggers auto-open of chat drawer with NW-Claude briefing the run summary
- Auto-brief mechanism: Worker IPC `run:completed` → server SSE `brief-ready` event → frontend auto-opens drawer
- Need a global SSE connection (not per-run) so auto-brief works from any page

### Chat Backend
- Claude CLI `--input-format stream-json` as primary chat engine (inherits all plugin/MCP/permission settings)
- First task in plan must be a minimal spike: spawn `claude -p --input-format stream-json`, send a message, verify response
- If spike fails → fallback to Anthropic SDK (loses plugin context, document the tradeoff)
- If spike succeeds → full CLI route

### Chat Session Lifecycle
- Each target gets its own claude -p process (no sharing)
- Switch target → kill old process → spawn new with target-specific context
- Close drawer → keep process alive in background → reopen = continue conversation
- Reset button → kill + respawn fresh session
- NW-Claude has NW journal access for the focused target (via `--mcp-config`)

### Config Editor
- YAML textarea as main editor with syntax highlighting (if achievable without heavy deps)
- Edit lock: read-only by default, explicit "Edit" button to unlock
- 4-step save validation flow: static YAML parse → Haiku semantic check → diff preview → confirm save
- Validation UX: Claude's discretion (wizard-style or inline feedback — whatever fits best)
- Config page uses tab layout: Targets tab + Safety tab, each with its own YAML editor
- Config warnings from self-repair.yaml displayed inline in the relevant tab
- $0.05 cap on Haiku semantic validation call (from PROJECT.md constraints)

### Add/Edit/Remove Target
- Add Target: 4-step modal wizard (consistent with TriggerDialog pattern) — type → goals → monitors/respond → validate
- Edit Target: same modal wizard, pre-filled with existing values
- Remove Target: confirm dialog (like existing remove pattern in TargetDetail)
- Wizard generates YAML and appends to targets.yaml → runs 4-step validation before writing

### Feedback Buttons
- Thumbs up/down on each action card in run detail (per signal granularity)
- POST /api/feedback with signal_id, verdict (accepted/rejected), optional reason
- MCP feedback tool (nw_submit_feedback) for NW-Claude to also submit feedback
- Visual: compact 👍/👎 icons, fills/highlights on selection, disabled after submission

### Implicit Feedback Collection
- Worker polls PR and Linear issue status periodically (every 6h or before each run)
- Uses `gh` CLI for PR status (merged = accepted, closed without merge = rejected)
- Uses Linear MCP for issue status (closed/done = accepted)
- Results written to feedback store and NW journal

### Reject Rate Calibration
- Both: Config page shows per-indicator calibration data (reject rate + current confidence threshold) for transparency
- AND: feedback trends written to NW journal for NW-Claude slow learning path
- Calibration adjustments happen automatically — user can see but not manually override

### Self-Assessment Display
- Phase 3.5 (pre-action strategy) and Phase 4.5 (post-action reflection) embedded inside action cards
- Action card expanded view: top = strategy rationale, bottom = reflection on outcome
- Co-located with feedback buttons — user reads assessment then gives feedback

### Indicator Baseline Display
- Phase 0.5 baselines shown as a summary card at top of run detail
- Each indicator: one row with name, current_value, trend arrow (↑/↓/→)
- Compact, always visible (not collapsible) — provides context for all action cards below

### Claude's Discretion
- 4-step validation UX specifics (wizard vs inline — whatever works best for the flow)
- YAML syntax highlighting approach (simple regex vs library)
- Chat drawer animation/transition details
- Auto-brief prompt construction (how to summarize run for NW-Claude context)
- Exact polling interval for implicit feedback (6h is suggested, not mandatory)
- Baseline summary card visual design

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Design Spec
- `docs/superpowers/specs/2026-03-18-nightwatch-dashboard-design.md` — Full design spec (812 lines), covers chat architecture, config validation, feedback pipeline, self-assessment phases

### Existing Codebase
- `app/server/ipc.ts` — IPC message handling, SSE fan-out pattern (reuse for global events)
- `app/server/routes/api.ts` — REST API patterns (reuse for /api/feedback, /api/config)
- `app/server/routes/stream.ts` — SSE streaming pattern (reuse for global brief-ready events)
- `app/frontend/lib/api.ts` — Frontend API client (extend with new endpoints)
- `app/frontend/components/trigger-dialog.ts` — Modal dialog pattern (reuse for Add Target wizard)
- `app/frontend/pages/config.ts` — Placeholder page to replace
- `app/worker/executor.ts` — Run execution + NW journal MCP injection pattern
- `app/shared/types.ts` — Shared type definitions (extend for feedback, assessment, baseline)

### Config Files
- `config/safety.yaml` — Safety config structure (one of the two editable files)
- `~/.claude/kc-plugins-config/nightwatch-targets.yaml` — Targets config structure (the other editable file)
- `~/.claude/kc-plugins-config/nightwatch-self-repair.yaml` — Self-repair warnings to display inline

### Plugin Reference
- `reference/ROADMAP.md` — Plugin evolution roadmap
- `CLAUDE.md` — Plugin-specific conventions and file ownership rules

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `TriggerDialog` component: modal pattern with role="dialog", backdrop, buttons — reuse for Add Target wizard
- `LogStream` component: SSE connection + auto-scroll — pattern for chat message stream
- `api.ts` client: get/post/put/del helpers — extend for feedback/config/chat endpoints
- `ipc.ts` SSE fan-out: Map<runId, Set<SSEWriter>> — adapt for global event broadcasting
- `Sidebar` + `TargetDetail`: master-detail layout — chat drawer overlays this

### Established Patterns
- Preact + HTM, no bundler, vendor ESM + Bun.Transpiler for .ts serving
- Server routes in `routes/*.ts` mounted via `app.route('/', ...)`
- Worker IPC messages typed as `IpcMessage` / `WorkerToServer` / `ServerToWorker`
- Config stored in `~/.claude/kc-plugins-config/` YAML files, read via `yaml-store.ts`

### Integration Points
- Dashboard page: add chat drawer toggle button + global SSE listener for brief-ready
- Run detail page: extend with action card feedback buttons + baseline summary card + assessment sections
- Config page: replace placeholder with YAML editor + tabs + Add Target wizard
- Worker: add implicit feedback polling step (before or after runs)
- Server: new routes — /api/feedback, /api/config/:file, /api/chat (WebSocket or SSE)
- Shared types: extend with FeedbackEntry, Assessment, IndicatorBaseline, ChatMessage

</code_context>

<specifics>
## Specific Ideas

- Chat drawer should feel like a helper that's always available but never intrusive — slide-over, not takeover
- Auto-brief on run complete: NW-Claude proactively opens and says "Run done. Here's what happened..." — user doesn't have to initiate
- Config editor: professional but simple — YAML is the truth, UI just adds safety rails (validation, diff, lock)
- Feedback: per-action-card granularity is essential — the flywheel needs to know which signals are good/bad, not just "this run was ok"
- Assessment text should be readable prose, not raw JSON — NW-Claude writes it in natural language

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-flywheel-core*
*Context gathered: 2026-03-18*
