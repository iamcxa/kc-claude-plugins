# Phase 4: Full Flywheel - Research

**Researched:** 2026-03-18
**Domain:** MCP Server (Streamable HTTP), Inline SVG charts, Linear GraphQL API, MCP client integration in chat
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**MCP Server Library & Transport**
- `@modelcontextprotocol/sdk` (official SDK), NOT `@hono/mcp`
- Streamable HTTP transport at `/mcp` route on the existing Hono server
- Single McpServer instance created at startup, tools registered once
- **Stateless**: each request creates new `WebStandardStreamableHTTPServerTransport` (no `sessionIdGenerator`)
- Token auth: same Bearer token as REST API routes (reuse existing `tokenAuth` middleware)

**MCP Tool Scope (13 tools)**
- Query (7): `nw_get_targets`, `nw_get_latest_run`, `nw_get_run`, `nw_get_proposals`, `nw_get_config_warnings`, `nw_get_schedule`, `nw_read_journal`
- Search (1): `nw_search_journal`
- Action (4): `nw_trigger_run`, `nw_submit_feedback`, `nw_update_schedule`, `nw_implement_proposal`
- `nw_implement_proposal` is a **stub** returning a workaround message (full pipeline is v2 scope)
- `nw_read_journal` + `nw_search_journal` read from `~/.claude/nightwatch/memory/{target}/.private-journal/`

**Health Page Navigation & Layout**
- New 4th page in bottom nav: Dashboard · Runs · Health · Config
- Layout (top to bottom): aggregate health summary bar → per-target sections (name + arrow + sparklines) → reject rate charts per indicator → acceptance rate with trend arrow

**Chart Rendering**
- **Inline SVG** in Preact components — zero chart library dependency
- Sparklines: SVG polyline (~30 lines of code)
- Reject rate charts: SVG line chart with axes

**Per-Target Health Arrow on Dashboard**
- Arrow + label next to target name in sidebar: ↑ improving (green), → stable (gray), ↓ degrading (red)
- Derived from latest run's indicator baseline trends

**Health Data API**
- Aggregate at query time — no materialized health store
- `GET /api/health/:target` reads last 10 run summaries, extracts `indicator_baseline` per run
- Response shape: `{ target, health, indicators: { [name]: { current, trend, history[] } }, reject_rate, acceptance_rate, runs_analyzed }`
- Reject rate data from `feedback-store.ts#getCalibrationData()`

**NW-Claude MCP Access (CHAT-04)**
- Hybrid: Anthropic SDK for chat (unchanged) + MCP client for tool calls
- chat-manager defines 13 NW tools as Anthropic tool schemas in `messages.create()`
- When Claude returns `tool_use` blocks, chat-manager routes to MCP client at `http://localhost:{port}/mcp`
- MCP client uses `@modelcontextprotocol/sdk` Client class

**NW-Claude Journal Access (CHAT-05)**
- Via NW MCP server journal tools (`nw_read_journal`, `nw_search_journal`)
- No separate journal MCP server needed — consolidated into NW MCP
- Target-specific: tools accept `target` parameter

**Linear Issue Status (FEED-05)**
- Direct GraphQL fetch from worker's `feedback-collector.ts`
- Endpoint: `https://api.linear.app/graphql`
- Auth: `Authorization: <LINEAR_API_KEY>` (no Bearer prefix for personal API keys)
- `LINEAR_API_KEY` in `.env`
- Status mapping: `state.type === 'completed'` → accepted, `state.type === 'cancelled'` → rejected, else null
- Graceful skip if no `LINEAR_API_KEY`

**MCP Feedback Tool (FEED-03)**
- `nw_submit_feedback` wraps existing `POST /api/feedback` logic
- Same `FeedbackEntry` format, `source: 'user'`
- Validates `signal_id` exists in run history before recording

### Claude's Discretion
- MCP client lifecycle management (singleton vs per-message)
- Health page empty state handling (fewer than 3 data points)
- Sparkline and chart SVG sizing, colors, axis labels
- MCP error response formatting
- How tools communicate auth token requirement to Claude sessions
- Exact Anthropic tool schema definitions for the 13 tools

### Deferred Ideas (OUT OF SCOPE)
- Full Proposal Pipeline (PROP-01..05) — `nw_implement_proposal` is a stub
- Implementation Outcome Tracking (OUT-01..03) — v2 scope
- Slack reaction feedback (EXTFEED-01)
- PR review comment parsing (EXTFEED-02)
- Health page live updates via SSE — polling on page load is sufficient for MVP

</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| MCP-01 | Hono route at /mcp using Streamable HTTP transport | WebStandardStreamableHTTPServerTransport works natively with Bun+Hono; no bridge library needed |
| MCP-02 | Query tools (nw_get_targets, nw_get_latest_run, nw_get_run, nw_get_proposals, nw_get_schedule) + journal tools | registerTool() with z.object inputSchema; tools read from existing stores |
| MCP-03 | Action tools (nw_trigger_run, nw_submit_feedback, nw_update_schedule) | Same registerTool() pattern; tools call existing REST API logic directly |
| MCP-04 | Token auth for remote mode | Reuse existing `tokenAuth` middleware at `app.use('*')` — already guards all routes when remote mode enabled |
| HEALTH-01 | Indicator trend sparklines (last 10 runs) | Inline SVG polyline; health API aggregates indicator_baseline from run-store last 10 runs |
| HEALTH-02 | Reject rate chart per indicator | SVG line chart with axes; data from getCalibrationData() |
| HEALTH-03 | Acceptance rate (proposals accepted / total) | Computed from run summaries' actions + feedback entries |
| HEALTH-04 | Per-target health indicator on target cards (up/stable/down arrow) | trendArrow() pattern already exists in baseline-card.ts; sidebar gets health prop |
| HEALTH-05 | Aggregate health summary bar | Aggregate across all targets; derive from indicator_baseline trends in latest run |
| CHAT-04 | NW-Claude has NW-MCP access (trigger runs, query state, submit feedback) | Hybrid: Anthropic SDK messages.create() with tools array + MCP Client routes tool_use blocks to localhost /mcp |
| CHAT-05 | NW-Claude has target-specific NW journal access | nw_read_journal + nw_search_journal MCP tools; chat-manager's MCP client calls these |
| FEED-03 | MCP feedback tool (nw_submit_feedback) | registerTool() wrapping appendFeedback(); validates signal_id from run history |
| FEED-05 | Linear issue status collection | Direct GraphQL fetch replacing checkLinearStatus placeholder; Authorization header is `<API_KEY>` without Bearer prefix |

</phase_requirements>

---

## Summary

Phase 4 completes the closed-loop improvement system by exposing all nightwatch state via an MCP server, adding a Flywheel Health page, wiring NW-Claude chat to use MCP tools, and completing the feedback loop with Linear issue status.

The key technical discovery is that `@modelcontextprotocol/sdk` v1.27.1 ships a `WebStandardStreamableHTTPServerTransport` that works natively on Bun (no `fetch-to-node` bridge needed). The official SDK example `honoWebStandardStreamableHttp.ts` demonstrates the exact pattern: create a new transport + McpServer per request for stateless operation. Tools are registered once on a factory function that creates fresh McpServer instances.

For NW-Claude MCP integration, the design uses a hybrid: Anthropic SDK `messages.create()` carries the 13 NW tools as schemas, and `tool_use` blocks are routed to a `StreamableHTTPClientTransport` connected to `localhost:{port}/mcp`. The MCP client passes `requestInit: { headers: { Authorization: 'Bearer ...' } }` for auth when remote mode is active.

**Primary recommendation:** Use `WebStandardStreamableHTTPServerTransport` (not `StreamableHTTPServerTransport`) — the Web Standard variant is the modern Bun-native approach and requires no Node.js http compatibility layer.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `@modelcontextprotocol/sdk` | 1.27.1 (latest) | MCP server + client | Official SDK; ships WebStandard transport native to Bun |
| `fetch-to-node` | NOT NEEDED | (alternative bridge) | WebStandardStreamableHTTPServerTransport makes this unnecessary |

### Already Installed (no new installs for non-MCP work)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `@anthropic-ai/sdk` | ^0.79.0 | Chat + tool schemas | Already in use; phase 4 extends with `tools` array |
| `hono` | ^4.12.8 | HTTP routing | Add `/mcp` route + `/api/health/:target` |
| `zod` | ^3.x (v3.25.76 installed) | Tool input validation | MCP SDK v1.27.1 supports Zod v3 (AnySchema = z3.ZodTypeAny \| z4.$ZodType) |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| WebStandardStreamableHTTPServerTransport | StreamableHTTPServerTransport + fetch-to-node | Node-compat variant works but requires extra dependency; Web Standard is the forward-looking approach |
| Direct Anthropic tool schemas in chat | @hono/mcp or separate MCP plugin | CONTEXT.md locked the hybrid Anthropic SDK approach |

**Installation:**
```bash
cd app && bun add @modelcontextprotocol/sdk
```

**Version verification (confirmed 2026-03-18):**
```bash
npm view @modelcontextprotocol/sdk version  # → 1.27.1
npm view fetch-to-node version              # → 2.1.0 (NOT needed)
```

---

## Architecture Patterns

### Recommended Project Structure (new files only)

```
app/
├── server/
│   ├── routes/
│   │   ├── mcp.ts           # NEW: MCP server endpoint (/mcp POST+GET)
│   │   └── health-api.ts    # NEW: GET /api/health/:target
│   └── services/
│       └── mcp-tools.ts     # NEW: McpServer factory + all 13 tool registrations
├── worker/
│   └── feedback-collector.ts  # MODIFY: replace checkLinearStatus stub
├── frontend/
│   ├── pages/
│   │   └── health.ts        # NEW: Health page component
│   └── components/
│       ├── sparkline.ts     # NEW: SVG polyline sparkline
│       ├── line-chart.ts    # NEW: SVG line chart with axes
│       ├── health-summary.ts # NEW: aggregate health summary bar
│       └── sidebar.ts       # MODIFY: add health arrow prop
└── shared/
    └── types.ts             # MODIFY: HealthApiResponse, HealthIndicator types
```

### Pattern 1: Stateless MCP Server with Hono (WebStandard transport)

**What:** Each POST to `/mcp` creates a fresh McpServer + WebStandardStreamableHTTPServerTransport pair.
**When to use:** All MCP requests; stateless = no session tracking, no cleanup.

```typescript
// Source: @modelcontextprotocol/sdk examples/server/honoWebStandardStreamableHttp.ts (verified from npm pack)
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js'
import { WebStandardStreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/webStandardStreamableHttp.js'

// Factory: creates fresh McpServer per request (stateless)
function createMcpServer(): McpServer {
  const server = new McpServer({ name: 'nightwatch', version: '1.0.0' })

  server.registerTool('nw_get_targets', {
    description: 'List all configured nightwatch targets',
    inputSchema: {}
  }, async () => {
    const targets = await readTargets()
    return { content: [{ type: 'text', text: JSON.stringify(Object.values(targets)) }] }
  })

  // ... register all 13 tools ...
  return server
}

// Hono route - stateless: new transport + server per request
mcpRoutes.all('/mcp', async (c) => {
  const transport = new WebStandardStreamableHTTPServerTransport()
  const server = createMcpServer()
  await server.connect(transport)
  return transport.handleRequest(c.req.raw)  // Returns Web Standard Response directly
})
```

### Pattern 2: MCP Client with Bearer Auth in chat-manager

**What:** chat-manager creates an MCP Client per session (or singleton) to route tool_use blocks.
**When to use:** When `sendMessage()` response contains `tool_use` content blocks.

```typescript
// Source: @modelcontextprotocol/sdk client/streamableHttp.d.ts (verified from npm pack)
import { Client } from '@modelcontextprotocol/sdk/client/index.js'
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js'

async function getMcpClient(port: number, token?: string): Promise<Client> {
  const client = new Client({ name: 'nw-chat', version: '1.0.0' })
  const transport = new StreamableHTTPClientTransport(
    new URL(`http://localhost:${port}/mcp`),
    token ? { requestInit: { headers: { Authorization: `Bearer ${token}` } } } : undefined
  )
  await client.connect(transport)
  return client
}

// In sendMessage(), handle tool_use loop:
// 1. messages.create({ tools: NW_TOOL_SCHEMAS, messages })
// 2. If response has tool_use blocks → call mcpClient.callTool({ name, arguments })
// 3. Append tool_result messages → repeat until stop_reason !== 'tool_use'
```

### Pattern 3: MCP Tool Registration with Zod v3

**What:** registerTool() with Zod v3 inputSchema (compatible with SDK v1.27.1).
**When to use:** All 13 tool registrations.

```typescript
// Source: MCP SDK mcp.d.ts ZodRawShapeCompat = Record<string, AnySchema>
// AnySchema = z3.ZodTypeAny | z4.$ZodType  → Zod v3 works
import { z } from 'zod'

server.registerTool('nw_get_run', {
  description: 'Get details for a specific run by ID',
  inputSchema: { run_id: z.string().describe('The run ID to fetch') }
}, async ({ run_id }) => {
  const run = await getRun(run_id)
  if (!run) return { content: [{ type: 'text', text: 'Run not found' }], isError: true }
  return { content: [{ type: 'text', text: JSON.stringify(run) }] }
})
```

### Pattern 4: Health API Aggregation

**What:** Read last 10 run summaries, extract indicator history, compute trend.
**When to use:** `GET /api/health/:target`

```typescript
// Aggregate from run-store (no materialized store)
const runs = await listRuns({ target })  // from run-store.ts
const last10 = runs.slice(0, 10)

// For each indicator, build history array
const indicatorHistory: Record<string, number[]> = {}
for (const run of last10.reverse()) {  // chronological order
  const summary = await getRun(run.id)
  const baseline = summary?.summary?.per_target[target]?.indicator_baseline ?? {}
  for (const [name, b] of Object.entries(baseline)) {
    if (!indicatorHistory[name]) indicatorHistory[name] = []
    indicatorHistory[name].push(b.value)
  }
}
```

### Pattern 5: Inline SVG Sparkline

**What:** 40x16px SVG polyline for trend visualization, zero dependencies.
**When to use:** Each indicator in Health page per-target section.

```typescript
// Source: Designed inline (standard SVG technique, ~30 lines)
function Sparkline({ values, width = 80, height = 20 }: { values: number[]; width?: number; height?: number }) {
  if (values.length < 2) return html`<span style="color:var(--muted);font-size:11px;">--</span>`

  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = max - min || 1

  const points = values.map((v, i) => {
    const x = (i / (values.length - 1)) * width
    const y = height - ((v - min) / range) * height
    return `${x},${y}`
  }).join(' ')

  const color = values[values.length - 1]! > values[0]! ? 'var(--success)' : 'var(--error)'

  return html`
    <svg width=${width} height=${height} style="overflow:visible">
      <polyline points=${points} fill="none" stroke=${color} stroke-width="1.5" />
    </svg>
  `
}
```

### Pattern 6: Linear GraphQL Issue Status Fetch

**What:** Replace `checkLinearStatus` placeholder with actual GraphQL call.
**When to use:** `feedback-collector.ts` implicit feedback collection.

```typescript
// Source: Linear Developers docs (verified 2026-03-18)
// Auth: personal API key uses "Authorization: <key>" (no Bearer prefix)
export async function checkLinearStatus(issueUrl: string): Promise<'accepted' | 'rejected' | null> {
  const apiKey = process.env.LINEAR_API_KEY
  if (!apiKey) return null  // graceful skip

  const match = issueUrl.match(/linear\.app\/[^/]+\/issue\/([A-Z]+-\d+)/)
  if (!match) return null

  const issueId = match[1]
  const query = `{ issue(id: "${issueId}") { state { type } } }`

  try {
    const res = await fetch('https://api.linear.app/graphql', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': apiKey },
      body: JSON.stringify({ query })
    })
    const data = await res.json() as { data?: { issue?: { state?: { type?: string } } } }
    const stateType = data?.data?.issue?.state?.type
    if (stateType === 'completed') return 'accepted'
    if (stateType === 'cancelled') return 'rejected'
    return null  // started, triage, backlog, unstarted = still in progress
  } catch {
    return null
  }
}
```

### Anti-Patterns to Avoid

- **Using StreamableHTTPServerTransport (Node variant) on Bun:** Requires `fetch-to-node` bridge. Use `WebStandardStreamableHTTPServerTransport` instead — returns `Promise<Response>` directly compatible with Hono and Bun.
- **Stateful MCP server (single instance, reused transport):** Transport state gets corrupted across requests. Always create new transport per request in stateless mode.
- **Shared MCP client singleton in chat-manager:** Reconnection handling is complex. Prefer creating client per-session (lazy init, cached per `targetName`).
- **Bearer prefix on Linear personal API keys:** Personal API keys use `Authorization: <key>`, NOT `Authorization: Bearer <key>`. OAuth tokens use Bearer.
- **Importing from `@modelcontextprotocol/sdk` root:** The SDK uses subpath exports. Import from `@modelcontextprotocol/sdk/server/mcp.js` and `@modelcontextprotocol/sdk/server/webStandardStreamableHttp.js`.
- **MCP route registered with Hono middleware override:** MCP's `/mcp` endpoint handles its own auth at the transport level. The existing `tokenAuth` middleware at `app.use('*')` already guards it in remote mode — do not add per-route auth that conflicts.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| MCP protocol serialization (JSON-RPC) | Custom JSON-RPC encoder | `@modelcontextprotocol/sdk` McpServer | Initialize, tools, error handling, MCP lifecycle — all handled by SDK |
| Streamable HTTP transport lifecycle | Custom SSE/POST handling | `WebStandardStreamableHTTPServerTransport` | Handles GET (SSE) + POST (JSON-RPC), returns Web Standard Response |
| MCP client connection + tool calls | Custom HTTP calls to /mcp | `Client` + `StreamableHTTPClientTransport` | listTools(), callTool(), reconnection, auth injection |
| Chart rendering | d3.js, chart.js, recharts | Inline SVG `<polyline>` / `<path>` | No bundler architecture — zero vendor ESM needed; sparklines are ~30 lines |
| Linear state resolution | Linear SDK (full package) | Direct `fetch` to GraphQL API | One query, one status field — SDK adds 50+ KB for no benefit |

**Key insight:** The MCP SDK handles the entire protocol surface. There is no MCP behavior to hand-implement. The only application-level work is registering tool handlers that call existing store methods.

---

## Common Pitfalls

### Pitfall 1: zod/v4 import in examples vs zod v3 in project

**What goes wrong:** The official SDK `honoWebStandardStreamableHttp.ts` example uses `import * as z from 'zod/v4'`. Copying this import into the project will fail because the project has Zod v3 installed (v3.25.76, pinned from Phase 1).

**Why it happens:** MCP SDK v1.27.1 supports both Zod v3 and v4. Examples use v4 syntax. The type `AnySchema = z3.ZodTypeAny | z4.$ZodType` means v3 schemas work fine.

**How to avoid:** Use `import { z } from 'zod'` (standard v3 import). Pass `z.string()`, `z.number()`, etc. directly as `inputSchema` values. Do NOT use `z.object()` wrapper — pass raw shape `{ field: z.string() }`.

**Warning signs:** TypeScript error "Module 'zod/v4' not found" or "Property ... does not exist on type ZodString" (v4 API differences).

### Pitfall 2: WebStandardStreamableHTTPServerTransport import path

**What goes wrong:** `import { WebStandardStreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server'` fails — it's not exported from the `server` subpath index, only from `server/webStandardStreamableHttp`.

**Why it happens:** SDK uses granular module paths, not a barrel re-export.

**How to avoid:** Use exact path: `@modelcontextprotocol/sdk/server/webStandardStreamableHttp.js`. Similarly `McpServer` is at `@modelcontextprotocol/sdk/server/mcp.js`.

**Warning signs:** "Module has no exported member 'WebStandardStreamableHTTPServerTransport'" TypeScript error.

### Pitfall 3: MCP client connect per tool call (too expensive)

**What goes wrong:** Creating a new `Client` + `StreamableHTTPClientTransport` + `client.connect()` on every tool invocation causes handshake overhead on every chat turn that uses tools.

**Why it happens:** Each `connect()` does MCP initialization (HTTP POST with InitializeRequest + InitializedNotification).

**How to avoid:** Cache MCP client per chat session (lazy init, reuse). Store in `ChatSession` object alongside `messages`. Reconnect only on error.

**Warning signs:** Noticeable latency (100-300ms extra) per tool call; multiple "POST /mcp" logs per chat message.

### Pitfall 4: Linear API key auth header format

**What goes wrong:** Using `Authorization: Bearer <LINEAR_API_KEY>` returns 401 for personal API keys.

**Why it happens:** Linear personal API keys don't use the Bearer scheme. Only OAuth2 access tokens use Bearer.

**How to avoid:** Use `Authorization: <LINEAR_API_KEY>` directly (no "Bearer " prefix). Source: Linear developers documentation (verified 2026-03-18).

**Warning signs:** `401 Unauthorized` from `https://api.linear.app/graphql` despite correct key in `.env`.

### Pitfall 5: Hono route registration order — /mcp must come after auth middleware

**What goes wrong:** If `/mcp` route is registered before `app.use('*', tokenAuth(...))`, remote mode auth is bypassed.

**Why it happens:** In `server/index.ts`, `app.use('*', tokenAuth(token))` is the auth guard. It must be registered before `app.route('/', mcpRoutes)`.

**How to avoid:** Follow existing `server/index.ts` pattern — auth middleware is at top, then routes are registered. `app.route('/', mcpRoutes)` added at the same level as other routes (after middleware setup).

**Warning signs:** `/mcp` accessible without auth token in remote mode.

### Pitfall 6: MCP tool_use loop termination in chat-manager

**What goes wrong:** Claude may return multiple sequential `tool_use` blocks or chain tool calls. If chat-manager only handles one round of tool_use, the conversation stalls or Claude repeats requests.

**Why it happens:** LLM tool use can be multi-turn: Claude calls tool → sees result → may call another tool.

**How to avoid:** Implement a while loop: `while (response.stop_reason === 'tool_use') { ... execute tools ... response = await messages.create(...) }`. Set a max iteration guard (e.g., 10 rounds) to prevent infinite loops.

**Warning signs:** Chat response ends with "I'll use the tool..." with no final answer.

### Pitfall 7: Health page with <2 data points

**What goes wrong:** Sparkline and trend charts crash or render empty if only 1 run exists.

**Why it happens:** SVG polyline needs 2+ points; trend arrows are undefined with single data point.

**How to avoid:** Sparkline component returns `--` placeholder for `values.length < 2`. Health page shows "Not enough data (N/10 runs)" banner when `runs_analyzed < 3`. Health arrow defaults to `→` (stable) when trend is indeterminate.

**Warning signs:** React/Preact render error in Sparkline; NaN in SVG point coordinates.

---

## Code Examples

Verified patterns from official sources and codebase inspection:

### MCP Route Registration in server/index.ts

```typescript
// Source: server/index.ts pattern (existing codebase)
// Add after existing route registrations:
import { mcpRoutes } from './routes/mcp.ts'
// ...
app.route('/', mcpRoutes)  // Add alongside feedbackRoutes, chatRoutes, etc.
```

### Tool Handler Returning Error

```typescript
// Source: MCP SDK CallToolResult type (verified from npm pack)
server.registerTool('nw_trigger_run', {
  description: 'Trigger a nightwatch run for a target',
  inputSchema: {
    target: z.string().describe('Target name or __all__'),
    mode: z.enum(['production', 'dry-run']).optional(),
  }
}, async ({ target, mode }) => {
  if (workerStatus !== 'online') {
    return { content: [{ type: 'text', text: 'Worker is offline' }], isError: true }
  }
  // ... enqueue run ...
  return { content: [{ type: 'text', text: JSON.stringify({ run_id }) }] }
})
```

### Anthropic Tool Schema Definition for NW Tools

```typescript
// Source: Anthropic SDK tool schema format (@anthropic-ai/sdk types)
const NW_TOOLS: Anthropic.Tool[] = [
  {
    name: 'nw_get_targets',
    description: 'List all configured nightwatch monitoring targets',
    input_schema: { type: 'object', properties: {}, required: [] },
  },
  {
    name: 'nw_trigger_run',
    description: 'Trigger a nightwatch run. Returns run_id.',
    input_schema: {
      type: 'object',
      properties: {
        target: { type: 'string', description: 'Target name or __all__ for all targets' },
        mode: { type: 'string', enum: ['production', 'dry-run'], description: 'Run mode' },
      },
      required: ['target'],
    },
  },
  // ... 11 more tools
]
```

### Health API Response Type

```typescript
// New type to add to shared/types.ts
export interface HealthIndicatorData {
  current: number
  trend: 'improving' | 'stable' | 'degrading'
  history: number[]  // last N values, chronological
}

export interface TargetHealthData {
  target: string
  health: 'improving' | 'stable' | 'degrading'
  indicators: Record<string, HealthIndicatorData>
  reject_rate: number
  acceptance_rate: number
  runs_analyzed: number
}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| SSE+HTTP transport (2024-11-05) | Streamable HTTP | MCP spec 2025-03-26 | Single endpoint handles both POST (JSON-RPC) and GET (SSE stream); no separate /sse route needed |
| `StreamableHTTPServerTransport` (Node.js) | `WebStandardStreamableHTTPServerTransport` | SDK v1.10+ | Works on Bun, Cloudflare Workers, Deno without `fetch-to-node` bridge |
| `server.tool()` method | `server.registerTool()` | SDK v1.x | `tool()` is deprecated; `registerTool()` is the current API |

**Deprecated/outdated:**
- `server.tool()`: Deprecated in favor of `server.registerTool()`. Still works but shows deprecation warnings.
- `StreamableHTTPServerTransport` (Node.js variant): Works but requires `fetch-to-node` on Bun. `WebStandardStreamableHTTPServerTransport` is the recommended replacement.
- HTTP+SSE transport from spec 2024-11-05: Superseded by Streamable HTTP in spec 2025-03-26. Backwards compat is maintained but new servers should use Streamable HTTP.

---

## Open Questions

1. **MCP client singleton vs per-session in chat-manager**
   - What we know: SDK recommends closing client when done; reconnect is cheap (one HTTP roundtrip)
   - What's unclear: Whether lazy-init per session with cleanup on `killSession()` is sufficient, or if per-request is needed
   - Recommendation (Claude's discretion): Lazy-init singleton per session (stored in `ChatSession`). Initialize on first tool call, reuse for session lifetime, close in `killSession()`.

2. **nw_implement_proposal stub response format**
   - What we know: Must return a helpful workaround message pointing to `nw_trigger_run`
   - What's unclear: Whether `isError: true` or just a text message is better UX for Claude
   - Recommendation: Return text-only (no `isError: true`) — it's a known limitation, not an error.

3. **Health chart minimum data requirement**
   - What we know: Sparklines need 2+ points; meaningful trend needs 3+
   - What's unclear: Exact threshold for showing "not enough data" vs partial chart
   - Recommendation (Claude's discretion): Show sparkline with 2+ points (accept sparse); show "Gathering data (N runs)" for < 3 runs.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Bun test (built-in) v1.3.9 |
| Config file | none — `bun test` auto-discovers `tests/**/*.test.ts` |
| Quick run command | `bun test --test-name-pattern "mcp\|health\|linear\|chat"` (from `app/` dir) |
| Full suite command | `bun test` (from `app/` dir) — currently 163 pass |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| MCP-01 | POST /mcp returns 200 for valid MCP init request | unit (route) | `bun test --test-name-pattern "mcp route"` | ❌ Wave 0 |
| MCP-02 | nw_get_targets returns JSON array of targets | unit (tool) | `bun test --test-name-pattern "mcp tools"` | ❌ Wave 0 |
| MCP-03 | nw_trigger_run enqueues a run and returns run_id | unit (tool) | `bun test --test-name-pattern "mcp tools"` | ❌ Wave 0 |
| MCP-04 | /mcp with no token returns 401 when auth_token set | unit (security) | `bun test --test-name-pattern "mcp auth\|security"` | ❌ Wave 0 (extend security.test.ts) |
| HEALTH-01 | Sparkline receives history array and renders SVG polyline | unit (component) | `bun test --test-name-pattern "sparkline\|health"` | ❌ Wave 0 |
| HEALTH-02 | /api/health/:target returns indicator history arrays | unit (route) | `bun test --test-name-pattern "health api"` | ❌ Wave 0 |
| HEALTH-03 | acceptance_rate computed correctly from actions + feedback | unit (service) | `bun test --test-name-pattern "health"` | ❌ Wave 0 |
| HEALTH-04 | Sidebar health arrow changes with target health prop | unit (component) | `bun test --test-name-pattern "sidebar\|health arrow"` | ❌ Wave 0 |
| HEALTH-05 | Aggregate health bar reflects worst/overall trend | unit (component) | `bun test --test-name-pattern "health summary"` | ❌ Wave 0 |
| CHAT-04 | chat-manager routes tool_use to MCP client and returns tool_result | unit (chat) | `bun test --test-name-pattern "chat.*tool\|mcp client"` | ❌ Wave 0 |
| CHAT-05 | nw_read_journal tool reads from target journal dir | unit (tool) | `bun test --test-name-pattern "journal\|mcp tools"` | ❌ Wave 0 |
| FEED-03 | nw_submit_feedback records FeedbackEntry via appendFeedback | unit (tool) | `bun test --test-name-pattern "mcp tools\|submit.*feedback"` | ❌ Wave 0 |
| FEED-05 | checkLinearStatus returns accepted for completed, rejected for cancelled | unit (worker) | `bun test --test-name-pattern "linear"` | ❌ Wave 0 |

**Note on test strategy:** Following the established project pattern (static source-read TDD for wiring tests, direct unit tests for pure logic). MCP tool tests use in-memory Hono app with mocked stores (same pattern as `feedback.test.ts`, `health.test.ts`). Chat-manager tool_use tests mock the Anthropic stream and MCP client.

### Sampling Rate
- **Per task commit:** `bun test` from `app/` — full suite in ~1.5s
- **Per wave merge:** `bun test` — all 163+ tests green
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/server/mcp.test.ts` — MCP route auth, basic tool registration shape, POST /mcp 200
- [ ] `tests/server/health-api.test.ts` — GET /api/health/:target response shape, empty state, aggregation
- [ ] `tests/worker/linear-status.test.ts` — checkLinearStatus URL parsing, state.type mapping, graceful null on missing key
- [ ] `tests/server/chat-tools.test.ts` — chat-manager tool_use routing, MCP client call, tool_result injection
- [ ] (optional) `tests/shared/health-types.test.ts` — HealthIndicatorData, TargetHealthData type shape validation

---

## Sources

### Primary (HIGH confidence)

- `@modelcontextprotocol/sdk` npm pack (v1.27.1, 2026-03-18) — verified: `WebStandardStreamableHTTPServerTransport` class, `registerTool()` API, `StreamableHTTPClientTransport` with `requestInit` option, Zod v3 compatibility via `AnySchema = z3.ZodTypeAny | z4.$ZodType`
- SDK example: `dist/esm/examples/server/honoWebStandardStreamableHttp.js` — canonical Hono+Bun stateless MCP pattern
- Codebase: `app/server/index.ts`, `app/server/services/chat-manager.ts`, `app/server/services/feedback-store.ts`, `app/worker/feedback-collector.ts`, `app/server/routes/feedback.ts`, `app/shared/types.ts` — verified existing patterns and integration points
- Linear Developer docs (`linear.app/developers/graphql`, verified 2026-03-18) — personal API key uses `Authorization: <key>` (no Bearer prefix)

### Secondary (MEDIUM confidence)

- MCP official spec (`modelcontextprotocol.io/docs/concepts/transports`) — Streamable HTTP protocol description, session management semantics
- `github.com/mhart/mcp-hono-stateless` — Hono MCP integration approach (uses `fetch-to-node`, but confirmed unnecessary for WebStandard transport)

### Tertiary (LOW confidence)

- WebSearch results for Linear API state types: `triage`, `backlog`, `unstarted`, `started`, `completed`, `cancelled` — cross-referenced with CONTEXT.md decision which already specifies `completed` → accepted, `cancelled` → rejected

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — npm pack extracted actual types and examples from SDK v1.27.1
- Architecture: HIGH — patterns derived directly from codebase + official SDK examples
- Pitfalls: HIGH — most pitfalls identified from SDK source inspection and prior project lessons (STATE.md)
- Linear API auth: MEDIUM — documented in official Linear docs; consistent with CONTEXT.md decision

**Research date:** 2026-03-18
**Valid until:** 2026-04-18 (MCP SDK updates frequently; verify transport API if >30 days old)
