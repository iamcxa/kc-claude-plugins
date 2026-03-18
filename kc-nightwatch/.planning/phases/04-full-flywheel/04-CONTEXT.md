# Phase 4: Full Flywheel - Context

**Gathered:** 2026-03-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Make the entire nightwatch state queryable and actionable from any Claude session via MCP server, and make flywheel health visible as charts and trends on a dedicated Health page. Also wires up deferred Phase 3 capabilities: NW-Claude MCP access (CHAT-04/05), MCP feedback tool (FEED-03), and Linear issue status collection (FEED-05). This completes the closed-loop improvement system.

</domain>

<decisions>
## Implementation Decisions

### MCP Server Library & Transport
- **@modelcontextprotocol/sdk** (official SDK), NOT @hono/mcp
- Streamable HTTP transport at `/mcp` route on the existing Hono server
- Single McpServer instance created at startup, tools registered once
- **Stateless**: each request creates new `StreamableHTTPServerTransport` with `sessionIdGenerator: undefined`
- Token auth: same Bearer token as REST API routes (reuse existing `tokenAuth` middleware)

### MCP Tool Scope
- **13 tools total** (full design spec + journal access):
  - Query (7): `nw_get_targets`, `nw_get_latest_run`, `nw_get_run`, `nw_get_proposals`, `nw_get_config_warnings`, `nw_get_schedule`, `nw_read_journal`
  - Search (1): `nw_search_journal`
  - Action (4): `nw_trigger_run`, `nw_submit_feedback`, `nw_update_schedule`, `nw_implement_proposal`
- `nw_implement_proposal` is a **stub with clear error** — returns workaround message pointing to `nw_trigger_run`. Full implementation deferred to v2 Proposal Pipeline.
- `nw_read_journal` + `nw_search_journal` read from per-target NW journal directory (`~/.claude/nightwatch/memory/{target}/.private-journal/`). These fulfill CHAT-05.

### Health Page Navigation & Layout
- **New 4th page** in bottom nav: Dashboard · Runs · Health · Config
- Health page layout (top to bottom):
  1. Aggregate health summary bar (overall trend)
  2. Per-target sections with target name + health arrow (↑/↓/→) + indicator sparklines (last 10 runs)
  3. Reject rate charts per indicator (line chart)
  4. Acceptance rate (proposals accepted / total) with trend arrow

### Chart Rendering
- **Inline SVG** in Preact components — zero chart library dependency
- Sparklines: SVG polyline (~30 lines of code)
- Reject rate charts: SVG line chart with axes
- Consistent with no-bundler architecture (no vendoring needed)

### Per-Target Health Arrow on Dashboard
- Arrow + label next to target name in sidebar: ↑ improving (green), → stable (gray), ↓ degrading (red)
- Derived from latest run's indicator baseline trends

### Health Data API
- **Aggregate at query time** — no materialized health store
- `GET /api/health/:target` reads last 10 run summaries from run-store, extracts `indicator_baseline` per run, returns time-series data
- Response shape: `{ target, health, indicators: { [name]: { current, trend, history[] } }, reject_rate, acceptance_rate, runs_analyzed }`
- Reject rate data from feedback-store's `getCalibrationData()`

### NW-Claude MCP Access (CHAT-04)
- **Hybrid approach**: Anthropic SDK for chat (unchanged) + MCP client for tool calls
- Chat-manager defines all 13 NW tools as Anthropic tool schemas in the `messages.create()` call
- When Claude returns `tool_use` blocks, chat-manager routes to an MCP client connected to `http://localhost:{port}/mcp`
- MCP client uses `@modelcontextprotocol/sdk` Client class (same package as server)
- Tool results fed back as `tool_result` messages in the conversation

### NW-Claude Journal Access (CHAT-05)
- Via NW MCP server journal tools (nw_read_journal, nw_search_journal)
- Chat-manager's MCP client calls these tools on behalf of NW-Claude
- Target-specific: journal tools accept `target` parameter, read from that target's journal directory
- No separate journal MCP server needed — consolidated into NW MCP

### Linear Issue Status (FEED-05)
- **Direct GraphQL fetch** from worker's feedback-collector (same process context as checkPrStatus)
- Endpoint: `https://api.linear.app/graphql`
- Auth: `Authorization: <LINEAR_API_KEY>` (no Bearer prefix, per Linear docs)
- LINEAR_API_KEY in `.env` (alongside ANTHROPIC_API_KEY)
- Graceful skip: if no LINEAR_API_KEY, return null (same as Phase 3 behavior)
- Status mapping: `state.type === 'completed'` → accepted, `state.type === 'cancelled'` → rejected, else null
- Issue ID extraction from URL: `linear.app/team/issue/SC-123` → `SC-123`

### MCP Feedback Tool (FEED-03)
- `nw_submit_feedback` MCP tool wraps existing `POST /api/feedback` logic
- Same FeedbackEntry format, source: 'user' (MCP submissions treated as explicit user feedback)
- Validates signal_id exists in run history before recording

### Claude's Discretion
- MCP client lifecycle management (singleton vs per-message)
- Health page empty state handling (fewer than 3 data points)
- Sparkline and chart SVG sizing, colors, axis labels
- MCP error response formatting
- How tools communicate auth token requirement to Claude sessions
- Exact Anthropic tool schema definitions for the 13 tools

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Design Spec
- `docs/superpowers/specs/2026-03-18-nightwatch-dashboard-design.md` — Full design spec. §MCP Server (line ~433): 11 tools, transport config, usage pattern. §Flywheel Health (line ~484): metrics table, display per indicator. §Appendix (line ~887): MCP transport config JSON, client configuration.
- `docs/superpowers/specs/2026-03-18-nightwatch-dashboard-design.md` §Appendix B — RunSummary type (per_target.indicator_baseline is the health data source)

### Existing Codebase (build on top of)
- `app/server/services/chat-manager.ts` — Current Anthropic SDK chat implementation. Phase 4 adds tool_use handling + MCP client.
- `app/server/services/feedback-store.ts` — Feedback YAML store with explicit/pr/linear partitions + getCalibrationData()
- `app/worker/feedback-collector.ts` — checkPrStatus pattern (Bun.spawn gh CLI) + checkLinearStatus placeholder to replace
- `app/server/routes/feedback.ts` — POST /api/feedback endpoint (MCP tool wraps this)
- `app/server/services/run-store.ts` — Run history access (health API reads from this)
- `app/server/services/auth.ts` — tokenAuth middleware (reuse for MCP route)
- `app/frontend/components/baseline-card.ts` — Existing baseline display (health page extends this pattern)
- `app/frontend/components/bottom-nav.ts` — 3-page nav (add Health as 4th)
- `app/frontend/components/sidebar.ts` — Target list (add health arrow)
- `app/shared/types.ts` — Shared types (extend for health API response, MCP tool schemas)

### External APIs
- Linear GraphQL API: `https://api.linear.app/graphql` — Auth: `Authorization: <API_KEY>`, query: `issue(id: "SC-123") { state { type name } }`, state.type values: `started`, `completed`, `cancelled`
- MCP SDK: `@modelcontextprotocol/sdk` — Server: `McpServer` + `StreamableHTTPServerTransport`. Client: `Client` + `StreamableHTTPClientTransport`.

### Plugin Config
- `config/safety.yaml` — Safety limits (unchanged)
- `CLAUDE.md` — Plugin conventions

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `feedback-store.ts`: getCalibrationData() — already computes reject rate per indicator, reuse for health API
- `run-store.ts`: run history access — read last N runs for indicator trend data
- `auth.ts`: tokenAuth middleware — apply to MCP route for remote mode
- `baseline-card.ts`: indicator display pattern — adapt for health page sparklines
- `bottom-nav.ts`: page routing — extend with Health page
- `sidebar.ts`: target list — add health arrow indicator

### Established Patterns
- Hono route modules: `routes/*.ts` exports Hono app, mounted via `app.route('/', ...)`
- Preact + HTM with vendored ESM, no bundler, Bun.Transpiler for .ts serving
- Worker feedback collection: checkPrStatus pattern (Bun.spawn, graceful null on error)
- SSE fan-out: Map-based subscriber tracking, reuse for health page live updates

### Integration Points
- `app/server/index.ts`: mount new `routes/mcp.ts` via `app.route('/', mcpRoutes)`
- `app/server/services/chat-manager.ts`: add tools array to `messages.create()`, handle tool_use/tool_result loop
- `app/worker/feedback-collector.ts`: replace checkLinearStatus placeholder with GraphQL fetch
- `app/frontend/pages/`: add `health.ts` page component
- `app/frontend/components/`: add sparkline.ts, line-chart.ts, health-summary.ts components
- `.env`: add LINEAR_API_KEY

</code_context>

<specifics>
## Specific Ideas

- MCP server is the capstone — it makes nightwatch programmable from any Claude session, not just the dashboard
- Hybrid chat approach (SDK + MCP client) keeps the reliable Anthropic SDK for streaming while adding tool capabilities through the same MCP server external clients use
- Health page should be useful even with sparse data — the first few runs should show something meaningful (even if sparklines have only 2-3 points)
- Linear integration follows the same "graceful skip" pattern as PR status — no API key = silently skip, never block runs
- `nw_implement_proposal` stub establishes the tool in the schema so Claude sessions discover it now, with a helpful workaround message until v2

</specifics>

<deferred>
## Deferred Ideas

- Full Proposal Pipeline (PROP-01..05) — v2 scope, `nw_implement_proposal` is a stub for now
- Implementation Outcome Tracking (OUT-01..03) — v2, Phase 0.6 measurement
- Slack reaction feedback (EXTFEED-01) — requires Slack MCP read capability
- PR review comment parsing (EXTFEED-02) — requires gh API comment parsing
- Health page live updates via SSE — could push health changes in real-time, but polling on page load is sufficient for MVP

</deferred>

---

*Phase: 04-full-flywheel*
*Context gathered: 2026-03-18*
