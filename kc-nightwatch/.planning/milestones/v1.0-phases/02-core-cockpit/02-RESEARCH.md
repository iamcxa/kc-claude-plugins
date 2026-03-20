# Phase 2: Core Cockpit - Research

**Researched:** 2026-03-18
**Domain:** Preact+HTM SPA + Hono SSE streaming + Bun frontend serving + interval scheduler + run history + NW memory isolation
**Confidence:** HIGH (Phase 1 code is the source of truth; project-level STACK/ARCH/PITFALLS research verified via official docs; Preact/HTM patterns verified via official no-build guide)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Dashboard Layout**
- Master-detail layout, not card grid — left sidebar with target list, right panel shows selected target detail
- Left sidebar: target list (always visible, scrollable), each entry shows name + type badge + last run status
- Right panel: target north star, last run summary with phase progress, action cards, action buttons (Run / Run dry / Edit / Remove)
- Schedule status bar at top (full width): scheduler state, interval, next run countdown, last run summary
- Bottom nav: Dashboard · Runs · Config (3 pages)
- [+ Add Target] button at bottom of target list (Phase 3 implements wizard, Phase 2 just shows button)
- GitHub dark theme: `#0d1117` background, `#161b22` panels, `#30363d` borders, `#c9d1d9` text, `#58a6ff` links, `#3fb950` success, `#f85149` error

**SSE Log Presentation**
- Parsed phases with collapsible tool calls, not raw text log
- Phase headers as collapsible sections: `[timestamp] Phase N: Name ... ✓/✗/●`
- Tool calls indented under phases: `→ Agent: name dispatched` / `→ Tool: tool_name`
- Currently running phase has spinner animation, completed phases show ✓/✗
- Auto-scroll to bottom; user scrolling up pauses auto-scroll (resume button appears)
- "Show raw" toggle for full raw log (debug fallback)
- Uses existing `log-parser.ts` ParsedLogEvent types from Phase 1

**Trigger UX**
- Modal dialog (not inline form) — blocks background, prevents double-trigger
- 3 sections: Mode toggle (Production / Dry-run), Custom instructions textarea (optional), Self-repair toggle (default on)
- Mode: toggle buttons, not dropdown (only 2 options)
- "Run All" uses same modal but target field shows "All targets"
- Modal dismiss = cancel, no accidental trigger
- Start Run button disabled while a run is queued/running (max concurrency 1 enforced)

**Frontend Serving**
- Dev mode (default): Bun serves `app/frontend/*.ts` files directly with on-the-fly transpilation
- Production mode: `Bun.build()` bundles into `app/frontend/dist/app.js`
- Preact + HTM vendored locally in `app/frontend/vendor/` (not CDN — offline-friendly for mprocs)
- `index.html` uses `<script type="importmap">` pointing to vendor directory
- No Vite/esbuild/webpack — Bun's native bundler is sufficient
- package.json scripts: `"dev"` (watch mode), `"build"` (production bundle)

**Run History**
- Runs page: list of past runs with status badge, trigger type, duration, action counts, target name
- Filter by: status (completed/failed/with actions) and target
- Click a run → detail view: phase progress bar, parsed log, action cards (if any)
- Live view: during execution, auto-switches to live streaming log with phase progress bar
- Run detail is a sub-route: `/runs/:id`

**Scheduler**
- Interval scheduler (every N hours) managed by worker process
- Schedule state persisted in `nightwatch-app.yaml` (via yaml-store from Phase 1)
- Webhook endpoint: `POST /api/webhook` with optional `{ target, mode }` body
- Schedule visible in top bar: "Scheduler: every 2h · Next in 1h 23m"
- Enable/disable toggle in schedule bar

**NW Memory Isolation**
- Per-target journal directory: `~/.claude/nightwatch/memory/{target-name}/.private-journal/`
- Created on first execution of a target (not at target creation time)
- Worker injects via `--mcp-config` when spawning `claude -p`
- Isolation: running target A only loads target A's NW journal

**REST API Routes** (complete list defined in CONTEXT.md — see canonical_refs)

### Claude's Discretion
- Exact Preact component structure (number of components, nesting)
- CSS class naming convention
- SSE reconnection strategy on disconnect
- Run list pagination (simple offset or cursor-based)
- Exact schedule bar countdown update interval
- How to handle target path resolution for plugin type (auto-discover from registry)

### Deferred Ideas (OUT OF SCOPE)
- None — discussion stayed within phase scope
- Feedback buttons explicitly deferred to Phase 3 (despite STATE.md note — REQUIREMENTS.md is authoritative: FEED-01..07 = Phase 3)
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DASH-01 | Target cards showing name, type, north star, last run summary, health indicator | Master-detail layout: sidebar items + right panel components. Target data from `GET /api/targets`. |
| DASH-02 | Per-target context menu (Run / Run dry / Edit / Chat / Remove) | Modal trigger pattern; Edit/Remove stubs for Phase 3; Chat stub for Phase 3. |
| DASH-03 | Global Run All / Run All (dry-run) buttons | Same modal trigger; target = `__all__`. |
| DASH-04 | Schedule status bar (interval, next run countdown, last run summary) | `GET /api/schedule` → countdown computed client-side via `setInterval`. |
| DASH-05 | Navigation between Dashboard, Runs, and Config pages | Client-side router in `app.ts` — hash-based or History API; 3-tab bottom nav. |
| EXEC-01 | Manual run trigger with mode selection (production/dry-run) | Modal dialog → `POST /api/runs` → returns `{run_id}` immediately (202). |
| EXEC-02 | Custom prompt field on manual trigger (saved to run artifacts) | Modal textarea → included in POST body; executor writes to `runs/{id}/custom-prompt.txt`. |
| EXEC-03 | Self-repair toggle on manual trigger | Modal toggle field → `self_repair: boolean` in POST body. |
| EXEC-04 | Per-target safehouse policy generation (read-only vs read-write by mode) | `policy.ts` already exists from Phase 1; Phase 2 extends `PolicyTarget` with full `Target` type. |
| EXEC-05 | `claude -p --output-format stream-json` spawning with target cwd | `executor.ts` already spawns; Phase 2 wires real `target.resolved_path` from yaml-store. |
| EXEC-06 | Real-time log streaming from worker to browser via SSE | SSE fan-out pattern: `Map<run_id, Set<SSEWriter>>` in server; `ipc.ts` extended to fan-out `run:log` events. |
| EXEC-07 | Phase progress extraction from stream-json (Phase 0-5 detection) | `log-parser.ts` already detects phase markers; Phase 2 enriches `ParsedLogEvent` with `phase` field. |
| EXEC-08 | Run cancellation (SIGTERM to claude -p child) | Worker `cancel` IPC case (Phase 1 stub) → `activePids` map lookup + `process.kill(pid, 'SIGTERM')`. |
| EXEC-09 | Execution queue with max concurrency 1 | Worker in-memory queue + gate: if `current !== undefined`, push to queue; dequeue on `run:completed`. |
| SCHED-01 | Interval scheduler (every N hours, configurable) | `worker/scheduler.ts` (new): `setInterval` wrapping enqueue; interval from `AppConfig.schedule`. |
| SCHED-02 | Webhook endpoint (POST /api/webhook with optional target + mode) | New Hono route in `routes/api.ts`; validates body, creates Run, enqueues via IPC. |
| SCHED-03 | Schedule state persisted in nightwatch-app.yaml | `yaml-store.ts` already reads/writes `nightwatch-app.yaml`; add `writeAppConfig()` function. |
| HIST-01 | Run history list with status, trigger type, duration, action counts | `services/run-store.ts` (new): reads `nightwatch-runs.yaml` + `runs/{id}/summary.yaml`; `GET /api/runs`. |
| HIST-02 | Run detail view with phase progress, log, action cards | `GET /api/runs/:id` returns summary; log served from `runs/{id}/log.jsonl`; phase progress from summary. |
| HIST-03 | Filter runs by status (failed, with actions) and target | `GET /api/runs?status=failed&target=e2e-pipeline` — server-side filter over `nightwatch-runs.yaml`. |
| HIST-04 | Live view during execution (auto-switch from history to live) | Frontend: if run status = `running`, auto-connect to SSE stream and render live log panel. |
| MEM-01 | Per-target NW journal directory (`~/.claude/nightwatch/memory/{target}/`) | Created in executor before spawning claude if not exists: `fs.mkdir(..., { recursive: true })`. |
| MEM-02 | NW journal MCP injection into worker's claude -p sessions | `executor.ts`: generate `nw-journal.json` MCP config per run, pass as `--mcp-config` flag. |
| MEM-03 | Journal isolation (no cross-target memory) | Each `--mcp-config` points to `memory/{target.name}/` — never shared path. |
</phase_requirements>

---

## Summary

Phase 2 builds on a solid Phase 1 foundation (two-process server+worker, Bun native IPC, auth, YAML store, orphan cleanup, executor with force-kill workaround). The new work falls into five domains: (1) REST API routes + data services for targets and runs, (2) SSE fan-out wiring from existing IPC to browser, (3) interval scheduler and webhook in the worker, (4) Preact+HTM frontend serving with master-detail layout and live log streaming, and (5) NW memory isolation (per-target journal MCP injection).

The most technically complex items are the SSE fan-out (server must intercept IPC `run:log` messages and push to multiple browser connections per run) and the Preact+HTM frontend without a build step (import maps for vendored Preact, HTM tagged template syntax in `.ts` files). Both have verified patterns. The Type system needs extending: `ParsedLogEvent` needs a `phase` field for the collapsible log UI, and `RunSummary` needs the full design-spec structure (per Appendix B of the design spec) to drive history and run detail views.

**Primary recommendation:** Build backend routes + SSE wiring first (verifiable via curl/EventSource), then wire the frontend. This ensures real data flows before UI polish.

---

## Standard Stack

### Core (all already installed in package.json)

| Library | Version | Purpose | Notes |
|---------|---------|---------|-------|
| Hono | 4.12.8 (installed) | HTTP routes, SSE streaming, static serving | `streamSSE` from `hono/streaming`; `serveStatic` from `hono/bun` |
| Bun | 1.2.x | Runtime, transpile frontend `.ts`, `Bun.build()` for prod | Serves frontend files directly via `Bun.serve({ static })` |
| Preact | 10.23.1 (vendor) | Frontend component model + hooks | No JSX — use HTM tagged templates exclusively |
| HTM | 3.1.1 (vendor) | Tagged template → Preact vdom | `html\`<div>...\`` syntax, zero runtime deps |
| `@preact/signals` | 1.3.0 (vendor) | Fine-grained reactivity for SSE log stream + run status | Avoids full re-render on each log line |
| yaml | 2.8.2 (installed) | YAML read/write for targets + runs | Already used in yaml-store |
| zod | 3.x (installed) | Schema validation at API boundaries | Already used for AppConfig |

### New for Phase 2 (not yet installed)

None required — all dependencies are already in `package.json` or vendored as frontend files.

**Vendor files to download** (for `app/frontend/vendor/`):

```bash
# Download ESM builds from esm.sh or jsdelivr — pin exact versions
# preact@10.23.1 — one file: preact.module.js
# htm@3.1.1 — one file: htm.module.js
# @preact/signals@1.3.0 — one file: signals.module.js
```

### Alternatives Considered

| Instead of | Could Use | Why Not |
|------------|-----------|---------|
| Vendored Preact+HTM | CDN (esm.sh, jsdelivr) | CONTEXT decision: offline-friendly for mprocs usage |
| Hash-based client routing | History API pushState | Hash routing requires no server-side fallback config; simpler for Bun static serving |
| In-memory run log buffer | YAML polling for SSE | SSE from memory is O(1); YAML parse on each line is a performance trap (see Pitfalls) |
| `Map<run_id, Set<SSEWriter>>` fan-out | Single global SSE stream | Per-run fan-out allows multiple browser tabs on same run; easier cleanup on run complete |

---

## Architecture Patterns

### Recommended Project Structure (Phase 2 additions)

```
app/
├── server/
│   ├── index.ts                   # EXTEND: add serveStatic + new routes
│   ├── ipc.ts                     # EXTEND: add SSE fan-out on run:log events
│   ├── routes/
│   │   ├── health.ts              # EXISTING (Phase 1)
│   │   ├── api.ts                 # NEW: /api/targets, /api/runs, /api/webhook
│   │   ├── stream.ts              # NEW: /api/runs/:id/stream (SSE)
│   │   └── schedule.ts            # NEW: /api/schedule GET + PUT
│   └── services/
│       ├── yaml-store.ts          # EXTEND: add writeAppConfig(), Target reader
│       ├── auth.ts                # EXISTING (Phase 1)
│       ├── orphan-cleanup.ts      # EXISTING (Phase 1)
│       └── run-store.ts           # NEW: read run artifacts, list history
│
├── worker/
│   ├── index.ts                   # EXTEND: enqueue queue, cancel, schedule msg
│   ├── executor.ts                # EXTEND: real target path, MEM-01/02/03
│   ├── policy.ts                  # EXISTING (Phase 1)
│   ├── log-parser.ts              # EXTEND: add phase field to ParsedLogEvent
│   └── scheduler.ts               # NEW: interval timer, next-run tracking
│
├── frontend/
│   ├── index.html                 # NEW: import map + root mount
│   ├── app.ts                     # NEW: root Preact component + router
│   ├── pages/
│   │   ├── dashboard.ts           # NEW: master-detail layout
│   │   ├── runs.ts                # NEW: history list + detail + live
│   │   └── config.ts              # NEW: stub (Config page = Phase 3)
│   ├── components/
│   │   ├── sidebar.ts             # target list
│   │   ├── target-detail.ts       # right panel
│   │   ├── trigger-dialog.ts      # modal
│   │   ├── log-stream.ts          # parsed phase log with collapsibles
│   │   ├── run-timeline.ts        # phase progress bar
│   │   └── schedule-bar.ts        # top bar with countdown
│   └── vendor/
│       ├── preact.module.js       # vendored Preact ESM
│       ├── htm.module.js          # vendored HTM ESM
│       └── signals.module.js      # vendored @preact/signals ESM
│
└── shared/
    ├── types.ts                   # EXTEND: Target, RunSummary (full), ParsedLogEvent
    └── constants.ts               # EXTEND: scheduler constants
```

### Pattern 1: Preact + HTM Tagged Template Components

**What:** Write Preact components using HTM's `html` tagged template literal instead of JSX. No build step required in dev — Bun serves `.ts` files directly.

**When to use:** All frontend components in this phase.

**Critical setup — import map in `index.html`:**
```html
<!-- app/frontend/index.html -->
<script type="importmap">
{
  "imports": {
    "preact": "/vendor/preact.module.js",
    "preact/hooks": "/vendor/preact.module.js",
    "htm/preact": "/vendor/htm.module.js",
    "@preact/signals": "/vendor/signals.module.js"
  }
}
</script>
<script type="module" src="/app.ts"></script>
```

**Component pattern (TypeScript, no JSX):**
```typescript
// app/frontend/components/schedule-bar.ts
import { html } from 'htm/preact'
import { useEffect, useState } from 'preact/hooks'
import type { ScheduleConfig } from '../../shared/types.ts'

interface Props {
  schedule: ScheduleConfig
  nextRunAt: number | null
}

export function ScheduleBar({ schedule, nextRunAt }: Props) {
  const [countdown, setCountdown] = useState('')

  useEffect(() => {
    if (!nextRunAt) return
    const id = setInterval(() => {
      const diff = nextRunAt - Date.now()
      if (diff <= 0) { setCountdown('now'); return }
      const h = Math.floor(diff / 3_600_000)
      const m = Math.floor((diff % 3_600_000) / 60_000)
      setCountdown(`${h}h ${m}m`)
    }, 10_000)
    return () => clearInterval(id)
  }, [nextRunAt])

  return html`
    <div class="schedule-bar">
      <span>Scheduler: ${schedule.enabled ? `every ${schedule.interval_hours}h` : 'disabled'}</span>
      ${nextRunAt ? html`<span>· Next in ${countdown}</span>` : null}
    </div>
  `
}
```

**Source:** Preact no-build workflows guide (https://preactjs.com/guide/v10/no-build-workflows/)

### Pattern 2: SSE Fan-Out (IPC → Browser)

**What:** Server intercepts `run:log` IPC messages and pushes to all browser SSE connections watching that run.

**When to use:** EXEC-06 (real-time log streaming), HIST-04 (live view during execution).

**Implementation — extend `ipc.ts` with fan-out:**
```typescript
// server/ipc.ts additions
type SSEWriter = { writeSSE: (data: { data: string; event?: string }) => Promise<void> }
const sseSubscribers = new Map<string, Set<SSEWriter>>()

export function subscribeToRun(runId: string, writer: SSEWriter, signal: AbortSignal): () => void {
  if (!sseSubscribers.has(runId)) sseSubscribers.set(runId, new Set())
  sseSubscribers.get(runId)!.add(writer)

  // CRITICAL: Use AbortSignal for disconnect detection in Bun (more reliable than stream.onAbort)
  const cleanup = () => sseSubscribers.get(runId)?.delete(writer)
  signal.addEventListener('abort', cleanup)
  return cleanup
}

// Called from handleWorkerMessage when msg.type === 'run:log'
export function fanOutLogEvent(runId: string, event: ParsedLogEvent): void {
  const writers = sseSubscribers.get(runId)
  if (!writers?.size) return
  for (const writer of writers) {
    void writer.writeSSE({ data: JSON.stringify(event), event: 'log' })
  }
}

// Called on run:completed — remove run's subscriber set
export function closeRunSubscribers(runId: string): void {
  sseSubscribers.delete(runId)
}
```

**SSE route:**
```typescript
// server/routes/stream.ts
import { streamSSE } from 'hono/streaming'
import { subscribeToRun } from '../ipc.ts'

app.get('/api/runs/:id/stream', (c) => {
  const runId = c.req.param('id')
  return streamSSE(c, async (stream) => {
    const unsub = subscribeToRun(runId, stream, c.req.raw.signal)
    // Heartbeat to keep connection alive (60s ping)
    const pingTimer = setInterval(() => {
      void stream.writeSSE({ data: '', event: 'ping' })
    }, 60_000)
    // Wait until client disconnects or run completes (max 35 min)
    await stream.sleep(35 * 60_000)
    clearInterval(pingTimer)
    unsub()
  })
})
```

**Source:** ARCHITECTURE.md Pattern 2; PITFALLS.md Pitfall 4

### Pattern 3: Bun Static File Serving + TS Transpilation

**What:** Bun serves `app/frontend/` directory with on-the-fly TypeScript transpilation. No separate dev server needed.

**When to use:** DASH-01..05 — the entire frontend.

**Server extension in `server/index.ts`:**
```typescript
// Add to Bun.serve() config
const server = Bun.serve({
  port,
  hostname,
  fetch: app.fetch,
  // Dev mode: serve frontend directory with TS transpilation
  static: {
    '/': new Response(await Bun.file(`${import.meta.dir}/../frontend/index.html`).text(), {
      headers: { 'Content-Type': 'text/html' }
    })
  }
})

// Serve frontend files — add to Hono before API routes
app.use('/vendor/*', serveStatic({ root: `${import.meta.dir}/../frontend` }))
app.use('/*.ts', serveStatic({ root: `${import.meta.dir}/../frontend` }))
app.use('/pages/*', serveStatic({ root: `${import.meta.dir}/../frontend` }))
app.use('/components/*', serveStatic({ root: `${import.meta.dir}/../frontend` }))
app.use('/lib/*', serveStatic({ root: `${import.meta.dir}/../frontend` }))
```

Note: `serveStatic` from `hono/bun` — NOT from `hono/middleware`. The Bun-specific import handles TypeScript transpilation automatically.

**Source:** STACK.md "Frontend assets in production" section; Hono docs https://hono.dev/docs/getting-started/bun

### Pattern 4: Execution Queue in Worker

**What:** Worker maintains an in-memory FIFO queue with max concurrency 1.

**When to use:** EXEC-09.

```typescript
// worker/index.ts extension
import type { Run } from '../shared/types.ts'

const queue: Run[] = []
let currentRun: Run | null = null

async function processNextRun() {
  if (currentRun || queue.length === 0) return
  const run = queue.shift()!
  currentRun = run
  // ... resolve target, executeRun(...)
  // On completion callback:
  currentRun = null
  void processNextRun()  // drain queue
}

// In case 'enqueue':
queue.push(msg.run)
void processNextRun()

// In case 'cancel':
if (currentRun?.id === msg.run_id) {
  // kill via activePids
} else {
  const idx = queue.findIndex(r => r.id === msg.run_id)
  if (idx >= 0) queue.splice(idx, 1)
}
```

### Pattern 5: Interval Scheduler

**What:** Worker-side interval timer that enqueues scheduled runs.

**When to use:** SCHED-01, SCHED-03.

```typescript
// worker/scheduler.ts
import type { ScheduleConfig } from '../shared/types.ts'

let schedulerTimer: ReturnType<typeof setInterval> | null = null
let nextRunAt: number | null = null

export function startScheduler(config: ScheduleConfig, enqueue: (run: Run) => void): void {
  stopScheduler()
  if (!config.enabled || !config.interval_hours) return
  const intervalMs = config.interval_hours * 3_600_000
  nextRunAt = Date.now() + intervalMs
  schedulerTimer = setInterval(() => {
    nextRunAt = Date.now() + intervalMs
    const run = createScheduledRun()
    enqueue(run)
  }, intervalMs)
}

export function stopScheduler(): void {
  if (schedulerTimer) clearInterval(schedulerTimer)
  schedulerTimer = null
  nextRunAt = null
}

export function getNextRunAt(): number | null { return nextRunAt }
```

Workers also need to persist schedule config changes back: when server sends `{ type: 'schedule', config }`, worker calls `startScheduler(config, ...)` and the server writes updated config to `nightwatch-app.yaml`.

### Pattern 6: NW Memory Isolation (MEM-01..03)

**What:** Before spawning `claude -p`, executor creates target-specific journal directory and generates a per-run MCP config file pointing to it.

**When to use:** Every target execution.

```typescript
// executor.ts extension
import os from 'node:os'
import fs from 'node:fs/promises'

async function ensureNwMemoryDir(targetName: string): Promise<string> {
  const dir = path.join(os.homedir(), '.claude/nightwatch/memory', targetName, '.private-journal')
  await fs.mkdir(dir, { recursive: true })
  return dir
}

async function writeNwJournalConfig(runDir: string, journalDir: string): Promise<string> {
  const configPath = path.join(runDir, 'nw-journal.json')
  await Bun.write(configPath, JSON.stringify({
    mcpServers: {
      'nw-journal': {
        type: 'stdio',
        command: 'private-journal',
        args: ['--dir', journalDir]
      }
    }
  }))
  return configPath
}

// In executeRun — before building claudeArgs:
const journalDir = await ensureNwMemoryDir(target.name)
const journalConfigPath = await writeNwJournalConfig(runDir, journalDir)

// Add to claudeArgs:
'--mcp-config', journalConfigPath,
```

### Pattern 7: Client-Side Routing (hash-based)

**What:** Hash-based SPA router in `app.ts` — no server-side config needed.

**When to use:** DASH-05 (3-page navigation).

```typescript
// frontend/app.ts
import { html } from 'htm/preact'
import { useState, useEffect } from 'preact/hooks'
import { render } from 'preact'
import { Dashboard } from './pages/dashboard.ts'
import { Runs } from './pages/runs.ts'
import { Config } from './pages/config.ts'

type Page = 'dashboard' | 'runs' | 'config'

function getPage(): Page {
  const hash = location.hash.replace('#/', '')
  if (hash.startsWith('runs')) return 'runs'
  if (hash === 'config') return 'config'
  return 'dashboard'
}

function App() {
  const [page, setPage] = useState<Page>(getPage())
  useEffect(() => {
    const handler = () => setPage(getPage())
    window.addEventListener('hashchange', handler)
    return () => window.removeEventListener('hashchange', handler)
  }, [])
  return html`
    <div class="app">
      ${page === 'dashboard' && html`<${Dashboard} />`}
      ${page === 'runs' && html`<${Runs} />`}
      ${page === 'config' && html`<${Config} />`}
      <nav class="bottom-nav">
        <a href="#/dashboard">Dashboard</a>
        <a href="#/runs">Runs</a>
        <a href="#/config">Config</a>
      </nav>
    </div>
  `
}
render(html`<${App} />`, document.getElementById('app')!)
```

### Anti-Patterns to Avoid

- **Bare specifier imports in browser HTML:** `import { html } from 'htm/preact'` without an import map fails silently. Import map in `index.html` is mandatory.
- **Reusing Bun.file handle after write:** `yaml-store.ts` already handles this — always re-create the file handle for reads. Don't regress.
- **Blocking SSE on enqueue result:** `POST /api/runs` must return `{ run_id }` immediately (202 Accepted). Never await run completion in the HTTP handler.
- **SSE writer reference retained after disconnect:** Always clean up via `signal.addEventListener('abort', cleanup)` — not `stream.onAbort()` which is Bun-unreliable.
- **Tilde paths in MEM-01/02:** `policy.ts` already enforces no-tilde rule. MEM journal paths must use `os.homedir()` + concatenation, never template literal `~`.
- **Using `import` from `hono/middleware` for static files:** Use `hono/bun`'s `serveStatic` specifically — it handles Bun's TS transpilation.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| SSE keepalive | Custom heartbeat | 60s ping via `stream.writeSSE({ data: '', event: 'ping' })` | Browser EventSource auto-reconnects; server just needs to detect TCP close |
| Run persistence | Custom DB | `nightwatch-runs.yaml` (append) + `runs/{id}/summary.yaml` (per-run) | YAML is the established store; consistent with existing nightwatch-runs.yaml format |
| Frontend bundling (dev) | Webpack/Vite/esbuild | Bun's on-the-fly TS transpilation via `serveStatic` | No config, no separate process, already works |
| Client-side state management | Redux/Zustand/Context | `@preact/signals` for live state + `useState` for forms | Signals avoid full re-render per SSE log line; `useState` for everything static |
| Countdown timer accuracy | requestAnimationFrame | `setInterval(10_000)` — 10s granularity is fine for "1h 23m" display | User doesn't need sub-second accuracy for schedule countdown |
| Target YAML reading | Custom parser | `yaml-store.ts` `readYamlFile()` + Zod schema | Already handles both old and new field names (Appendix A compat layer) |
| MCP config file format | Custom spec | `nw-journal.json` standard MCP config format | Claude CLI reads standard `--mcp-config` JSON; same format as project `.mcp.json` |

**Key insight:** The worker and server infrastructure are already built. Phase 2 is about wiring: connect IPC events to SSE streams, connect API routes to YAML stores, connect the frontend to the API.

---

## Common Pitfalls

### Pitfall 1: IPC `run:log` reaches `handleWorkerMessage` but SSE writers not yet wired

**What goes wrong:** The worker sends `run:log` events correctly. Phase 1's `handleWorkerMessage` in `ipc.ts` only has a `default: log.debug(...)` case for unknown types. Without adding a `case 'run:log': fanOutLogEvent(...)` branch, all log events are silently dropped and the browser never receives them.

**Why it happens:** Phase 1 deliberately stubbed the switch — only `heartbeat` and `state` are handled. The `run:log` path was deferred.

**How to avoid:** Extend `handleWorkerMessage` with explicit cases for `run:log`, `run:started`, `run:completed`, `run:failed`. Each triggers its corresponding SSE fan-out or state update.

**Warning signs:** SSE stream connects successfully but receives no events while run is active.

### Pitfall 2: Preact/HTM import map path mismatches

**What goes wrong:** The import map maps `"htm/preact"` but the vendored `htm.module.js` exports a default function (the `html` tag factory), not a named `{ html }`. Browser throws "SyntaxError: The requested module '/vendor/htm.module.js' does not provide an export named 'html'".

**Why it happens:** HTM's ESM build requires calling `htm.bind(h)` — the module exports `htm` as default, not `html`. The `htm/preact` CDN URL on esm.sh provides a pre-bound version.

**How to avoid:** Use the pre-bound `htm/preact` ESM from esm.sh which exports `html` directly. Vendor this pre-bound file, not the raw `htm` package. Map it as `"htm/preact"` in the import map.

**Warning signs:** Console shows import errors on page load; `html` is undefined in component files.

### Pitfall 3: Worker has real `resolved_path` gap (Phase 1 stub)

**What goes wrong:** `worker/index.ts` line 34 uses `process.env.TARGET_PATH ?? '/tmp'` as a placeholder — `"real path from Phase 2"`. If Phase 2 doesn't fix this, every run executes claude in `/tmp` instead of the actual target path.

**Why it happens:** Phase 1 deliberately deferred target resolution to Phase 2. The comment is explicit: `// real path from Phase 2`.

**How to avoid:** Phase 2 must load target definitions from `nightwatch-targets.yaml` at worker startup (via yaml-store or a passed-in config), resolve `target.path` to an absolute path, and pass the real `PolicyTarget` to `executeRun`.

**Warning signs:** Claude runs complete but find no project files; log shows it operating in `/tmp`.

### Pitfall 4: `RunSummary` type mismatch between Phase 1 and design spec

**What goes wrong:** `shared/types.ts` has a minimal `RunSummary` (`phases_completed`, `signals_found`, `actions_taken`, `errors`). The design spec Appendix B defines a far richer structure with `per_target`, `indicator_baseline`, `actions[]`, etc. Frontend components for run detail (HIST-02) need the full type. Using the minimal type means the UI can only show phase names.

**Why it happens:** Phase 1 needed just enough to get a run result over IPC. The full type was explicitly deferred.

**How to avoid:** Extend `RunSummary` in `shared/types.ts` to match the Appendix B spec at the start of Phase 2. The executor's `summary` assembly code must also be updated to populate the new fields from parsed log events.

**Warning signs:** Run detail page shows empty action cards; indicator baseline section missing.

### Pitfall 5: SSE fan-out subscriber set not cleaned up on run complete

**What goes wrong:** When a run completes, `closeRunSubscribers(runId)` must be called. If omitted, the `Map<run_id, Set<SSEWriter>>` grows with every run. The browser SSE connections for completed runs are closed, but the server's set still holds dead references.

**Why it happens:** The run completion path in `ipc.ts` handles state update but doesn't call the cleanup function.

**How to avoid:** In `handleWorkerMessage` case `'run:completed'`: after updating run state, call `closeRunSubscribers(runId)`. Also call it on `'run:failed'` and `'run:cancelled'`.

### Pitfall 6: `ParsedLogEvent` is too minimal for collapsible phase log UI

**What goes wrong:** Current `ParsedLogEvent` has only `{ type, content, raw }`. The collapsible phase log (EXEC-07) needs `phase`, `tool_name`, `agent_name`, and `is_phase_start` / `is_phase_complete` flags. Without these, the frontend has no structured data to build phase sections from.

**Why it happens:** Phase 1 parser was a minimal stub — just enough to detect phase progress with a regex in `executor.ts`.

**How to avoid:** Extend `log-parser.ts` to parse these fields from stream-json lines. Phase markers are in `assistant` messages matching `/Phase (\d+(?:\.\d+)?)/`. Tool calls are in `tool_use` blocks. Agent dispatches are in text blocks matching `/Dispatching|Running|Starting.*agent/i`.

---

## Code Examples

Verified patterns from Phase 1 code + official sources:

### API Route Module Pattern (follows Phase 1 healthRoutes convention)

```typescript
// server/routes/api.ts
import { Hono } from 'hono'
import { readYamlFile } from '../services/yaml-store.ts'
import { listRuns } from '../services/run-store.ts'
import { sendToWorker, workerStatus } from '../ipc.ts'
import type { Run } from '../../shared/types.ts'
import { randomUUID } from 'node:crypto'

export const apiRoutes = new Hono()

// GET /api/targets
apiRoutes.get('/api/targets', async (c) => {
  const targets = await readYamlFile<Record<string, unknown>>(TARGETS_YAML_PATH)
  return c.json(targets ?? {})
})

// POST /api/runs — returns 202 immediately, SSE for progress
apiRoutes.post('/api/runs', async (c) => {
  if (workerStatus !== 'online') return c.json({ error: 'worker offline' }, 503)
  const body = await c.req.json<{ target: string; mode: 'production' | 'dry-run'; custom_prompt?: string; self_repair?: boolean }>()
  const run: Run = {
    id: randomUUID(),
    target: body.target,
    mode: body.mode,
    trigger: 'manual',
    status: 'queued',
    custom_prompt: body.custom_prompt,
    log_path: `runs/${id}/log.jsonl`,
  }
  sendToWorker({ type: 'enqueue', run })
  return c.json({ run_id: run.id }, 202)
})

// mount in server/index.ts: app.route('/', apiRoutes)
```

### HTM Collapsible Log Phase Component

```typescript
// frontend/components/log-stream.ts
import { html } from 'htm/preact'
import { useState, useEffect, useRef } from 'preact/hooks'
import type { ParsedLogEvent } from '../../shared/types.ts'

interface PhaseGroup {
  phase: string
  events: ParsedLogEvent[]
  status: 'running' | 'complete' | 'failed'
}

interface Props {
  runId: string
  initialEvents?: ParsedLogEvent[]
}

export function LogStream({ runId, initialEvents = [] }: Props) {
  const [phases, setPhases] = useState<PhaseGroup[]>([])
  const [collapsed, setCollapsed] = useState<Set<string>>(new Set())
  const [autoScroll, setAutoScroll] = useState(true)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const es = new EventSource(`/api/runs/${runId}/stream`)
    es.addEventListener('log', (e) => {
      const event: ParsedLogEvent = JSON.parse(e.data)
      setPhases(prev => appendToPhases(prev, event))
    })
    es.addEventListener('ping', () => {})  // keepalive
    return () => es.close()
  }, [runId])

  useEffect(() => {
    if (autoScroll) bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [phases, autoScroll])

  return html`
    <div class="log-stream" onScroll=${(e: Event) => {
      const el = e.target as HTMLElement
      setAutoScroll(el.scrollTop + el.clientHeight >= el.scrollHeight - 50)
    }}>
      ${phases.map(g => html`
        <div class="phase-group">
          <div class="phase-header" onClick=${() => toggle(g.phase, collapsed, setCollapsed)}>
            <span class="phase-status">${g.status === 'running' ? '●' : g.status === 'complete' ? '✓' : '✗'}</span>
            <span>${g.phase}</span>
          </div>
          ${!collapsed.has(g.phase) && g.events.map(ev => html`
            <div class="log-event">${renderEvent(ev)}</div>
          `)}
        </div>
      `)}
      <div ref=${bottomRef} />
    </div>
  `
}
```

### Target YAML Loading with Compat Layer

```typescript
// server/services/yaml-store.ts — add Target reader
import type { Target } from '../../shared/types.ts'

export async function readTargets(): Promise<Record<string, Target>> {
  const raw = await readYamlFile<{ targets: Record<string, unknown> }>(TARGETS_YAML_PATH)
  if (!raw?.targets) return {}

  // Appendix A compat: accept both old and new field names
  return Object.fromEntries(
    Object.entries(raw.targets).map(([name, t]) => {
      const target = t as Record<string, unknown>
      return [name, {
        name,
        type: target.type as string,
        monitors: (target.monitors ?? target.sources) as string[],
        watch: (target.watch ?? target.keywords) as string[],
        respond: (target.respond ?? mapOldActions(target.actions)) as Record<string, boolean>,
        indicators: (target.indicators ?? target.proxy_signals) as unknown[],
        north_star: target.north_star as string,
        path: target.path as string | undefined,
      } satisfies Target]
    })
  )
}
```

---

## State of the Art

| Old Approach | Current Approach | Impact for Phase 2 |
|--------------|------------------|--------------------|
| CDN Preact (e.g. `unpkg.com/preact`) | Vendored local + import maps | Offline-friendly, faster, no CDN dependency in mprocs |
| SSE `stream.onAbort()` in Bun | `c.req.raw.signal.addEventListener('abort', ...)` | Reliable disconnect detection after Hono PR #3042 fix |
| Polling YAML for run status | SSE push from IPC fan-out | Real-time; no server polling overhead |
| Socket file IPC (`nightwatch.sock`) | Bun native IPC (no socket file) | Phase 1 already decided — eliminates EADDRINUSE entirely |
| Cron + YAML-file workflow | Dashboard + interval scheduler + webhook | This entire phase |

---

## Open Questions

1. **Target path resolution strategy**
   - What we know: `nightwatch-targets.yaml` has a `path` field for some targets, but it's optional. Plugin targets may need auto-discovery from `~/.claude/plugins/local`.
   - What's unclear: Does every target in the existing config have a `path` field, or do some rely on the skill's Phase 0 `resolve` step?
   - Recommendation: Claude's discretion (per CONTEXT.md). Implement: if `path` is set, use it; if not, look for target in `~/.claude/plugins/local/{name}/` as a fallback. Log a warning for unresolvable paths.

2. **Run list pagination**
   - What we know: `nightwatch-runs.yaml` can accumulate many entries. Simple offset pagination is sufficient for a single-user tool.
   - What's unclear: Expected volume — 2h intervals → ~12 runs/day → ~360 runs/month. Manageable without pagination.
   - Recommendation: No pagination for Phase 2. Return all runs (capped at 100 most recent). Add cursor pagination in Phase 3 if needed.

3. **ParsedLogEvent enrichment scope**
   - What we know: The current minimal type needs `phase`, `tool_name`, `agent_name` fields for the collapsible log UI.
   - What's unclear: How reliably can tool calls and agent dispatches be extracted from stream-json? (Depends on what Claude actually emits in tool_use blocks.)
   - Recommendation: Parse `tool_use` blocks for `tool_name`; extract agent name from text blocks with regex. Fall back gracefully — if extraction fails, show raw content in the phase group.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `bun test` (Jest-compatible) |
| Config file | none — `bun test` auto-discovers `*.test.ts` in `tests/` |
| Quick run command | `bun test tests/server/` |
| Full suite command | `bun test` (from `app/` directory) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DASH-01 | Target cards populated from API response | unit | `bun test tests/server/api.test.ts::targets` | ❌ Wave 0 |
| DASH-04 | Schedule state returned by GET /api/schedule | unit | `bun test tests/server/schedule.test.ts` | ❌ Wave 0 |
| DASH-05 | Navigation hash routing renders correct page | manual | (browser check) | manual-only |
| EXEC-01 | POST /api/runs returns 202 + run_id immediately | unit | `bun test tests/server/api.test.ts::runs` | ❌ Wave 0 |
| EXEC-06 | SSE stream receives run:log events | unit | `bun test tests/server/sse.test.ts` | ❌ Wave 0 |
| EXEC-07 | ParsedLogEvent includes phase field from phase markers | unit | `bun test tests/worker/log-parser.test.ts` | ✅ (extend) |
| EXEC-08 | Cancel sends SIGTERM via activePids | unit | `bun test tests/worker/executor.test.ts` | ✅ (extend) |
| EXEC-09 | Queue: second enqueue waits for first to complete | unit | `bun test tests/worker/queue.test.ts` | ❌ Wave 0 |
| SCHED-01 | Scheduler fires enqueue after interval_hours | unit | `bun test tests/worker/scheduler.test.ts` | ❌ Wave 0 |
| SCHED-02 | POST /api/webhook enqueues a run | unit | `bun test tests/server/api.test.ts::webhook` | ❌ Wave 0 |
| SCHED-03 | Schedule config persisted to nightwatch-app.yaml | unit | `bun test tests/server/schedule.test.ts` | ❌ Wave 0 |
| HIST-01 | GET /api/runs returns list from runs.yaml | unit | `bun test tests/server/api.test.ts::run-list` | ❌ Wave 0 |
| HIST-02 | GET /api/runs/:id returns summary + log path | unit | `bun test tests/server/api.test.ts::run-detail` | ❌ Wave 0 |
| HIST-03 | GET /api/runs?status=failed filters correctly | unit | `bun test tests/server/api.test.ts::run-filter` | ❌ Wave 0 |
| HIST-04 | Live view auto-connects SSE when status=running | manual | (browser check) | manual-only |
| MEM-01 | ensureNwMemoryDir creates directory if absent | unit | `bun test tests/worker/executor.test.ts::memory` | ❌ Wave 0 |
| MEM-02 | nw-journal.json MCP config written per run | unit | `bun test tests/worker/executor.test.ts::mcp-config` | ❌ Wave 0 |
| MEM-03 | Each target gets separate journal path | unit | `bun test tests/worker/executor.test.ts::isolation` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `bun test tests/worker/ tests/server/` (backend only; no browser)
- **Per wave merge:** `bun test` (full suite from `app/` directory)
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/server/api.test.ts` — covers DASH-01, EXEC-01, SCHED-02, HIST-01..03
- [ ] `tests/server/sse.test.ts` — covers EXEC-06 (SSE fan-out with mock IPC)
- [ ] `tests/server/schedule.test.ts` — covers DASH-04, SCHED-03
- [ ] `tests/worker/queue.test.ts` — covers EXEC-09
- [ ] `tests/worker/scheduler.test.ts` — covers SCHED-01
- [ ] Extend `tests/worker/log-parser.test.ts` — add phase/tool extraction test cases (EXEC-07)
- [ ] Extend `tests/worker/executor.test.ts` — add cancel (EXEC-08) and MEM-01..03 cases

---

## Sources

### Primary (HIGH confidence)

- Phase 1 source code (`app/server/`, `app/worker/`, `app/shared/`) — authoritative ground truth for what's built
- `02-CONTEXT.md` — locked user decisions, canonical refs
- `.planning/research/STACK.md` — verified stack (Hono 4.12.8, Preact 10.23.1, HTM 3.1.1, Bun 1.2.x)
- `.planning/research/ARCHITECTURE.md` — SSE fan-out pattern, IPC message types, data flow
- `.planning/research/PITFALLS.md` — SSE disconnect handling, IPC stub gap, tilde paths
- `docs/superpowers/specs/2026-03-18-nightwatch-dashboard-design.md` — full data model, Appendix A (compat), Appendix B (RunSummary), Appendix E (monitor mapping)
- Preact no-build workflows (https://preactjs.com/guide/v10/no-build-workflows/) — import maps, HTM tagged templates, vendor pattern
- Hono Bun getting-started (https://hono.dev/docs/getting-started/bun) — `serveStatic` from `hono/bun`

### Secondary (MEDIUM confidence)

- Hono streaming helper (https://hono.dev/docs/helpers/streaming) — `streamSSE()`, `writeSSE()` signature
- Bun static file serving (https://bun.com/docs/runtime/http) — on-the-fly TS transpilation

### Tertiary (LOW confidence — not needed, using vendored approach)

- esm.sh CDN for pre-bound htm/preact — not used (vendored local), referenced for vendor file origin

---

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — Phase 1 already uses Hono+Bun+yaml+zod; Preact+HTM vendoring is well-documented
- Architecture: HIGH — SSE fan-out, queue, scheduler patterns are straightforward extensions of Phase 1 IPC design
- Frontend patterns: MEDIUM-HIGH — Preact+HTM+import maps is well-documented but Phase 1 has no frontend yet; import map gotchas are real
- Pitfalls: HIGH — Most are direct gaps from Phase 1 stubs (explicitly commented in source code)

**Research date:** 2026-03-18
**Valid until:** 2026-04-17 (30 days — stable stack)
