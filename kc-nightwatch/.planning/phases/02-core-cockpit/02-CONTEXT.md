# Phase 2: Core Cockpit - Context

**Gathered:** 2026-03-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Working dashboard that replaces the current cron + YAML-file workflow. Users can monitor targets, trigger runs (production/dry-run) with optional custom prompt, watch real-time SSE log streaming with parsed phase progress, browse run history with detail views, and control the interval scheduler. Includes NW memory isolation (per-target journal directories) and frontend serving. This is the first visual + interactive phase.

</domain>

<decisions>
## Implementation Decisions

### Dashboard Layout
- **Master-detail** layout, not card grid — left sidebar with target list, right panel shows selected target detail
- Left sidebar: target list (always visible, scrollable), each entry shows name + type badge + last run status
- Right panel: target north star, last run summary with phase progress, action cards, action buttons (Run / Run dry / Edit / Remove)
- Schedule status bar at top (full width): scheduler state, interval, next run countdown, last run summary
- Bottom nav: Dashboard · Runs · Config (3 pages)
- [+ Add Target] button at bottom of target list (Phase 3 implements wizard, Phase 2 just shows button)
- GitHub dark theme: `#0d1117` background, `#161b22` panels, `#30363d` borders, `#c9d1d9` text, `#58a6ff` links, `#3fb950` success, `#f85149` error

### SSE Log Presentation
- **Parsed phases with collapsible tool calls**, not raw text log
- Phase headers as collapsible sections: `[timestamp] Phase N: Name ... ✓/✗/●`
- Tool calls indented under phases: `→ Agent: name dispatched` / `→ Tool: tool_name`
- Currently running phase has spinner animation, completed phases show ✓/✗
- Auto-scroll to bottom; user scrolling up pauses auto-scroll (resume button appears)
- "Show raw" toggle for full raw log (debug fallback)
- Uses existing `log-parser.ts` ParsedLogEvent types from Phase 1

### Trigger UX
- **Modal dialog** (not inline form) — blocks background, prevents double-trigger
- 3 sections: Mode toggle (Production / Dry-run), Custom instructions textarea (optional), Self-repair toggle (default on)
- Mode: toggle buttons, not dropdown (only 2 options)
- "Run All" uses same modal but target field shows "All targets"
- Modal dismiss = cancel, no accidental trigger
- Start Run button disabled while a run is queued/running (max concurrency 1 enforced)

### Frontend Serving
- **Dev mode** (default): Bun serves `app/frontend/*.ts` files directly with on-the-fly transpilation
- **Production mode**: `Bun.build()` bundles into `app/frontend/dist/app.js`
- Preact + HTM **vendored locally** in `app/frontend/vendor/` (not CDN — offline-friendly for mprocs)
- `index.html` uses `<script type="importmap">` pointing to vendor directory
- No Vite/esbuild/webpack — Bun's native bundler is sufficient
- package.json scripts: `"dev"` (watch mode), `"build"` (production bundle)

### Run History
- Runs page: list of past runs with status badge, trigger type, duration, action counts, target name
- Filter by: status (completed/failed/with actions) and target
- Click a run → detail view: phase progress bar, parsed log, action cards (if any)
- Live view: during execution, auto-switches to live streaming log with phase progress bar
- Run detail is a sub-route: `/runs/:id`

### Scheduler
- Interval scheduler (every N hours) managed by worker process
- Schedule state persisted in `nightwatch-app.yaml` (via yaml-store from Phase 1)
- Webhook endpoint: `POST /api/webhook` with optional `{ target, mode }` body
- Schedule visible in top bar: "Scheduler: every 2h · Next in 1h 23m"
- Enable/disable toggle in schedule bar

### NW Memory Isolation
- Per-target journal directory: `~/.claude/nightwatch/memory/{target-name}/.private-journal/`
- Created on first execution of a target (not at target creation time)
- Worker injects via `--mcp-config` when spawning `claude -p`
- Isolation: running target A only loads target A's NW journal

### REST API Routes
- `GET /api/targets` — list targets (reads nightwatch-targets.yaml via yaml-store)
- `GET /api/targets/:name` — single target details
- `POST /api/runs` — trigger a run (body: { target, mode, custom_prompt?, self_repair? })
- `GET /api/runs` — list runs (from nightwatch-runs.yaml + run artifacts)
- `GET /api/runs/:id` — single run detail (summary + log)
- `GET /api/runs/:id/stream` — SSE endpoint for real-time log streaming
- `DELETE /api/runs/:id` — cancel a running run
- `POST /api/webhook` — external trigger (optional target + mode)
- `GET /api/schedule` — current scheduler state
- `PUT /api/schedule` — update scheduler config (enable/disable, interval)

### Claude's Discretion
- Exact Preact component structure (number of components, nesting)
- CSS class naming convention
- SSE reconnection strategy on disconnect
- Run list pagination (simple offset or cursor-based)
- Exact schedule bar countdown update interval
- How to handle target path resolution for plugin type (auto-discover from registry)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Design Spec
- `docs/superpowers/specs/2026-03-18-nightwatch-dashboard-design.md` — Full architecture, data model, API routes, UI mockups, safehouse policy. **Note: Dashboard layout changed from card grid to master-detail per CONTEXT decision above.**
- `docs/superpowers/specs/2026-03-18-nightwatch-dashboard-design.md` §Appendix A — Migration/compatibility layer for field renaming (monitors/watch/respond/indicators)
- `docs/superpowers/specs/2026-03-18-nightwatch-dashboard-design.md` §Appendix B — RunSummary type definition (per_target structure)
- `docs/superpowers/specs/2026-03-18-nightwatch-dashboard-design.md` §Appendix E — Monitor-to-agent mapping, __all__ target semantics

### Phase 1 Code (build on top of)
- `app/server/index.ts` — Hono server entry point, worker spawn, crash recovery
- `app/server/ipc.ts` — IPC state management, heartbeat watchdog
- `app/server/services/yaml-store.ts` — YAML read/write with Zod validation
- `app/server/services/auth.ts` — Bearer token middleware
- `app/worker/index.ts` — Worker IPC handler, executor dispatch
- `app/worker/executor.ts` — executeRun, force-kill, PID tracking, artifact cleanup
- `app/worker/log-parser.ts` — parseStreamJsonLine (ParsedLogEvent)
- `app/worker/policy.ts` — buildSafehouseFlags (PolicyTarget)
- `app/shared/types.ts` — Run, RunSummary, AppConfig, IpcMessage types
- `app/shared/constants.ts` — Timing constants, defaults

### Plugin Config
- `config/safety.yaml` — max_runtime_minutes, max_concurrent_runs, limits
- `CLAUDE.md` — Plugin conventions, branch naming, file ownership

### Project-Level Research
- `.planning/research/STACK.md` — Bun, Hono 4.12, Preact 10.23, HTM 3.1 versions and patterns
- `.planning/research/ARCHITECTURE.md` — SSE fan-out, WebSocket patterns, data flow
- `.planning/research/PITFALLS.md` — SSE subscriber leak, disconnect handling

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `yaml-store.ts`: loadOrCreateAppConfig, readYamlFile, writeYamlFile — use for targets.yaml and runs.yaml reads
- `auth.ts`: tokenAuth middleware — already applied at app level, all new routes get auth for free
- `log-parser.ts`: parseStreamJsonLine → ParsedLogEvent — feed into SSE stream
- `executor.ts`: executeRun with IPC callbacks — onMessage callback is the SSE data source
- `ipc.ts`: workerStatus state — used by health endpoint, reuse for dashboard status
- `shared/types.ts`: Run, IpcMessage, WorkerToServer — extend for new API response types

### Established Patterns
- Hono route modules: `routes/health.ts` exports a `healthRoutes` Hono app, mounted via `app.route('/', healthRoutes)`
- IPC message flow: worker sends typed messages → server `handleWorkerMessage` dispatches → state updates
- Zod validation for config: AppConfigSchema validates YAML before use
- `import.meta.dir` for relative path resolution in Bun

### Integration Points
- `app/server/index.ts` line 129: `app.route('/', healthRoutes)` — add new route modules here
- `app/server/ipc.ts`: `handleWorkerMessage` switch — extend for SSE fan-out on `run:log` events
- `app/worker/index.ts` case 'enqueue': currently minimal — Phase 2 wires up full target resolution
- `app/server/index.ts` line 143-145: startup sequence (cleanupOrphans → heartbeatWatchdog → spawnWorker) — add scheduler after worker spawn

</code_context>

<specifics>
## Specific Ideas

- Master-detail layout chosen over card grid for always-on mprocs usage — left sidebar is persistent, context switching is fast
- Parsed phase log with collapsible sections — not raw text dump — makes 30-minute runs scannable
- Modal trigger blocks background to prevent double-trigger (max concurrency 1)
- Vendor Preact+HTM locally for offline mprocs — no CDN dependency
- STATE.md notes "Feedback buttons land in Phase 2" — but REQUIREMENTS.md assigns FEED-01..07 to Phase 3. Follow REQUIREMENTS.md (Phase 2 scope is already 24 reqs). Feedback buttons come in Phase 3.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-core-cockpit*
*Context gathered: 2026-03-18*
