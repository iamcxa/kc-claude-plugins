# Stack Research

**Domain:** Bun-native web dashboard — HTTP server + background worker + Preact frontend with real-time streaming, IPC, and MCP server
**Researched:** 2026-03-18 (v1.0 baseline) / 2026-03-20 (v1.1 addendum) / 2026-03-21 (v2.0 addendum)
**Confidence:** HIGH (core stack verified via official docs and Context7; v2.0 additions verified against existing codebase + official sources)

---

## v2.0 Stack Additions (NEW — 2026-03-21)

> The v1.0/v1.1 stack (Bun, Hono, Preact/HTM, Zod, yaml, MCP SDK, toast, Notification API) is complete and validated. This section covers ONLY what v2.0 adds for: parallel execution, per-target scheduling, auto PR + Linear creation, and outcome tracking.

### New Feature Areas

| Feature | Stack Needed |
|---------|-------------|
| Parallel execution (per-target isolation) | `Map<string, Run[]>` + `Map<string, boolean>` in `worker/index.ts` — zero new deps |
| Per-target scheduling | `Map<string, Timer>` in `worker/scheduler.ts` — zero new deps |
| Auto PR creation | `gh` CLI (already system-wide authed), called via `Bun.spawn` — zero new deps |
| Auto Linear issue creation | Linear GraphQL API via `fetch()` — zero new deps |
| Outcome tracking | New `outcomes.yaml` store + `ActionOutcome` type — uses existing `yaml` + `zod` |

**Summary: No new npm packages.** All five v2.0 features are implementable with existing stack.

---

### Pattern 1: Per-Target Parallel Execution

**Decision: `Map<string, Run[]>` per-target queue + `Map<string, boolean>` running flag.**

Replace the current global `queue: Run[]` + `currentRun: Run | null` in `worker/index.ts` with per-target data structures.

**Why this is enough in Bun:** Bun's event loop is single-threaded — `async/await` ensures per-target state mutations are race-free without explicit locks. Each `executeRun()` call launches a separate `Bun.spawn` child process, so different targets genuinely run in parallel at the OS level. The `Map` is just routing logic; the actual parallelism comes from `Bun.spawn` already.

**Invariant:** `processTarget(name)` is idempotent — it's a no-op if that target is already running. Different targets drain independently; same-target runs queue sequentially.

```typescript
// Conceptual replacement in worker/index.ts
const queues = new Map<string, Run[]>()     // per-target pending runs
const running = new Map<string, boolean>()  // per-target running flag

async function processTarget(targetName: string): Promise<void> {
  if (running.get(targetName)) return
  const queue = queues.get(targetName) ?? []
  if (queue.length === 0) return
  running.set(targetName, true)
  const run = queue.shift()!
  try {
    await executeRun(run, resolveTarget(targetName), { ... })
  } finally {
    running.set(targetName, false)
    void processTarget(targetName)  // drain next in same-target queue
  }
}

function enqueue(run: Run): void {
  const targetQueue = queues.get(run.target) ?? []
  targetQueue.push(run)
  queues.set(run.target, targetQueue)
  void processTarget(run.target)
}
```

**`__all__` expansion stays the same** — it creates per-target `Run` objects that flow through the new per-target queues, just like before.

**IPC state shape change:** `type: 'state'` message in `WorkerToServer` changes from `{ queue: Run[], current?: Run }` to `{ queues: Record<string, Run[]>, running: string[] }`. Server-side `workerStatus` type in `server/ipc.ts` updates accordingly.

**Confidence:** HIGH — verified against Bun 1.3.9 async model; no native concurrency API needed. Confirmed: Bun has no built-in `PQueue` (GitHub Issue #15050 — feature request only).

---

### Pattern 2: Per-Target Scheduling

**Decision: `Map<string, ReturnType<typeof setInterval>>` keyed by target name.**

Replace the single global `schedulerTimer` in `worker/scheduler.ts` with per-target intervals.

**Schema addition needed** in `shared/types.ts`:
```typescript
export interface Target {
  // ... existing fields
  schedule?: {
    interval_hours: number   // per-target override; min 10min enforced in scheduler
  }
}
```

`yaml-store.ts`'s `normalizeTarget()` passes `schedule` through. The `ScheduleConfig` in `nightwatch-app.yaml` becomes the global fallback — active when a target has no `schedule` field.

**New `scheduler.ts` API:**
```typescript
startTargetSchedulers(targets: Record<string, Target>, globalConfig: ScheduleConfig, enqueue: (run: Run) => void): void
stopAllSchedulers(): void
```

Internally: iterate targets, compute effective `interval_hours` (target.schedule?.interval_hours ?? globalConfig.interval_hours), enforce 10min minimum, call `setInterval` per target, store handle in `Map<string, Timer>`. `stopAllSchedulers()` clears all handles.

**Why per-target intervals beat the `__all__` pattern:** `__all__` fires all targets simultaneously on one global timer — targets with different natural cadences end up artificially coupled. Per-target intervals let each target fire at its own rhythm.

**Confidence:** HIGH — `setInterval` is fully stable in Bun 1.3.9 (bun.sh/reference/globals/setInterval). Multiple independent intervals are cheap.

---

### Pattern 3: Auto PR Creation via `gh` CLI

**Decision: `Bun.spawn(['gh', 'pr', 'create', ...])` in new `worker/pr-creator.ts`.**

**Why `gh` CLI not GitHub REST API:** Already used in `feedback-collector.ts` for `gh pr view`. Auth is system-wide — no PAT token management needed. The Claude run in the target repo creates the branch and commits; `gh pr create` just opens the PR.

**Key flags for non-interactive mode** (verified against gh 2.83.2 official manual):
- `--title` — required, skips title prompt
- `--body` — required, skips body prompt
- `--head` — required, skips push/fork prompt
- `--base` — required, defaults to repo default branch but explicit is safer
- `--repo owner/repo` — explicit, avoids working directory confusion

When all four (`--title`, `--body`, `--head`, `--base`) are provided, `gh pr create` is fully non-interactive. Branch must already be pushed (the Claude run handles this via Phase 1/4 commit-and-push).

**Return value:** `gh pr create` prints the PR URL on stdout on success (e.g., `https://github.com/owner/repo/pull/42`). Capture `stdout` text, strip whitespace, store in `ActionOutcome.pr_url`.

**Error handling:** Fire-and-forget in `executor.ts` `finally` block. Non-zero exit (PR already exists, no remote, no commits vs base) → log warning, leave `pr_url` undefined on the outcome record. This matches the existing `collectImplicitFeedback` fire-and-forget pattern.

**New file:** `worker/pr-creator.ts` — mirrors `feedback-collector.ts` structure. Exported function: `createPr(branch: string, title: string, body: string, repoOwner: string, repoName: string): Promise<string | null>` (returns URL or null on failure).

**Confidence:** HIGH — `gh pr create` non-interactive behavior verified against official docs; pattern is identical to existing `checkPrStatus` in `feedback-collector.ts`.

---

### Pattern 4: Auto Linear Issue Creation via GraphQL API

**Decision: Direct `fetch()` call to Linear GraphQL API in new `worker/linear-creator.ts`.**

**Why not Linear MCP:** Linear MCP tools exist inside Claude sessions only (passed via `--mcp-config`). The worker is a plain Bun process. The existing `checkLinearStatus()` in `feedback-collector.ts` already proves the pattern: direct `fetch` to `https://api.linear.app/graphql` with `Authorization: <key>` (no `Bearer` prefix — verified in existing tests).

**Why not `@linear/sdk`:** Adds a dependency for a single mutation. The existing `checkLinearStatus` demonstrates raw GraphQL works without it.

**`issueCreate` mutation** (verified from Linear API docs + Apollo schema reference at studio.apollographql.com/public/Linear-API):
```graphql
mutation IssueCreate($title: String!, $description: String!, $teamId: String!) {
  issueCreate(input: { title: $title, description: $description, teamId: $teamId }) {
    success
    issue {
      id
      identifier
      url
    }
  }
}
```

The `url` field IS available on the `Issue` type in mutation responses (confirmed from Apollo schema). `identifier` gives human-readable `ENG-123` form. `url` gives the direct link.

**New `Target` field:**
```typescript
export interface Target {
  // ... existing fields
  linear_team_id?: string   // LINEAR_TEAM_ID for auto-issue creation; omit to skip
}
```

If `target.linear_team_id` is absent OR `LINEAR_API_KEY` env var is absent, issue creation is skipped gracefully — no error thrown.

**New file:** `worker/linear-creator.ts`. Exported function: `createLinearIssue(title: string, description: string, teamId: string): Promise<string | null>` (returns issue URL or null on failure).

**URL construction for Linear:** The mutation's `issue.url` field returns the full URL directly. No manual construction needed.

**Confidence:** HIGH — mutation verified from Linear API docs + Apollo schema. Auth pattern (no `Bearer`) confirmed in existing `linear-status.test.ts`.

---

### Pattern 5: Outcome Tracking via `outcomes.yaml`

**Decision: New `server/services/outcome-store.ts` + `~/.claude/kc-plugins-config/nightwatch-outcomes.yaml`.**

**Why a separate file from `runs.yaml`:** Outcomes outlive runs. Runs are pruned after 50 (KEEP_RUNS_COUNT). A PR created months ago is still worth showing on the Outcomes page after its run artifact is deleted.

**New type in `shared/types.ts`:**
```typescript
export interface ActionOutcome {
  id: string                   // randomUUID() — from node:crypto (already imported)
  run_id: string
  target: string
  signal_id: string
  signal_summary: string
  action_type: 'code-fix' | 'proposal' | 'linear-issue'
  pr_url?: string              // set if gh pr create succeeded
  linear_url?: string          // set if issueCreate succeeded
  created_at: string           // ISO timestamp
  status: 'open' | 'merged' | 'closed' | 'cancelled' | 'unknown'
}
```

**`outcome-store.ts` API** (mirrors `run-store.ts`):
```typescript
appendOutcome(outcome: ActionOutcome): Promise<void>
listOutcomes(filter?: { target?: string; status?: string; limit?: number }): Promise<ActionOutcome[]>
updateOutcomeStatus(id: string, status: ActionOutcome['status']): Promise<void>
```

Cap at 500 entries (new constant `KEEP_OUTCOMES_COUNT = 500` in `shared/constants.ts`).

**Status updates:** The existing `collectImplicitFeedback` (post-run PR status check) already calls `gh pr view`. Extend it to also call `updateOutcomeStatus()` when it detects a PR was merged/closed.

**MCP exposure:** Add `nw_get_outcomes` tool to `server/services/mcp-tools.ts`:
```typescript
server.registerTool('nw_get_outcomes', {
  description: 'List action outcomes (PRs and Linear issues) created by nightwatch runs',
  inputSchema: {
    target: z.string().optional(),
    status: z.enum(['open','merged','closed','cancelled','unknown']).optional(),
    limit: z.number().optional().default(20),
  }
}, async ({ target, status, limit }) => { ... })
```

This lets NW-Claude answer "what PRs did nightwatch create this week?" via chat.

**Outcomes page UI:** New `frontend/pages/outcomes.ts` (Preact component, same no-build pattern). New GET `/api/outcomes` route in `server/routes/api.ts`. Polled with existing `usePoll` hook — outcomes change slowly, 30s poll is fine.

**Confidence:** HIGH — extends existing `run-store.ts` pattern directly; no new libraries needed.

---

## New Files Summary for v2.0

| New File | Purpose | Pattern From |
|----------|---------|-------------|
| `worker/pr-creator.ts` | `gh pr create` wrapper | `feedback-collector.ts` (same Bun.spawn pattern) |
| `worker/linear-creator.ts` | Linear `issueCreate` mutation | `feedback-collector.ts` (same fetch pattern) |
| `server/services/outcome-store.ts` | Persist `ActionOutcome` records | `run-store.ts` (same YAML read/append pattern) |
| `frontend/pages/outcomes.ts` | Outcomes aggregate page | `frontend/pages/runs.ts` (same Preact list pattern) |

## Modified Files Summary for v2.0

| Modified File | Change |
|---------------|--------|
| `worker/index.ts` | Replace global queue with `Map<string, Run[]>` per-target queues |
| `worker/scheduler.ts` | Replace single timer with `Map<string, Timer>` per-target timers |
| `worker/executor.ts` | Add post-run `createPr()` + `createLinearIssue()` calls, write `ActionOutcome` |
| `shared/types.ts` | Add `ActionOutcome`, `Target.schedule?`, `Target.linear_team_id?`, update IPC state shape |
| `shared/constants.ts` | Add `KEEP_OUTCOMES_COUNT = 500`, `MIN_SCHEDULE_INTERVAL_MS = 600_000` |
| `server/services/mcp-tools.ts` | Add `nw_get_outcomes` tool |
| `server/routes/api.ts` | Add GET `/api/outcomes` route |
| `frontend/app.ts` | Add Outcomes page route to navigation |
| `frontend/components/bottom-nav.ts` | Add Outcomes nav item |

---

## Alternatives Considered (v2.0)

| Recommended | Alternative | Why Not |
|-------------|-------------|---------|
| `Map<string, Run[]>` per-target queue | BullMQ / p-queue / bee-queue | BullMQ requires Redis. p-queue is npm-installable but solves a harder problem (priority, concurrency across all items). The per-target-sequential, cross-target-parallel constraint is exactly solved by a `Map<string, Run[]>` — no dependency needed. |
| Per-target `setInterval` in Map | node-cron / croner | Cron expressions are explicitly Out of Scope (PROJECT.md). Interval-based is sufficient. Multiple `setInterval` handles is idiomatic JS for this. |
| Direct `fetch()` for Linear | `@linear/sdk` | One mutation. `@linear/sdk` is a full typed SDK (useful for complex integrations). For a single `issueCreate` call where auth and response shape are known, raw GraphQL fetch is simpler and adds no dep. |
| `gh` CLI for PR creation | GitHub REST API via `fetch()` | Would require managing PAT tokens separately. `gh` is already authed system-wide (same reason `checkPrStatus` uses `gh pr view`). |
| Separate `outcomes.yaml` | Embed in `runs.yaml` | Outcomes outlive runs (runs pruned at 50). Separating prevents data loss on run cleanup. |
| GET `/api/outcomes` + `usePoll` | SSE stream for outcomes | Outcomes are slow-changing (created once per action, status updates rare). Polling at 30s interval is simpler and sufficient — no need to add SSE consumers for this. |

---

## What NOT to Use (v2.0)

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Linear MCP tools from worker | MCP tools only exist inside Claude sessions — worker is a plain Bun process with no MCP client | Direct GraphQL `fetch()` to `api.linear.app/graphql` |
| `@linear/sdk` npm package | Adds dep for one mutation already demonstrated to work with raw fetch | `fetch()` with inline GraphQL mutation |
| BullMQ | Requires Redis, heavyweight for per-target isolation that's solvable with a Map | Native `Map<string, Run[]>` pattern |
| Constructing Linear URL manually | Fragile — workspace slug format can change | Request `url` field directly from `issueCreate` mutation response |
| `gh` with missing `--base` flag | Without `--base`, gh may interactively prompt if repo has multiple candidate branches | Always pass `--base main` (or repo default branch from target config) |

---

## Version Compatibility (v2.0)

| Package | Version | Notes |
|---------|---------|-------|
| Bun | 1.3.9 (current installed) | `setInterval` multi-timer, `Map`, `Bun.spawn`, `fetch` — all stable |
| `gh` CLI | 2.83.2 (current installed) | `--title --body --head --base` non-interactive verified |
| Linear API | GraphQL (current) | `issueCreate` mutation + `url` field on `Issue` type — stable, no versioning |
| `yaml` | ^2.8.2 (existing) | Handles new `outcomes.yaml` — no version change |
| `zod` | ^3.0.0 (existing) | `ActionOutcome` schema validation — no version change |

---

## Sources (v2.0)

- Bun 1.3.9 docs (bun.sh/reference/globals/setInterval) — multi-timer pattern confirmed stable, HIGH confidence
- Bun GitHub Issue #15050 (github.com/oven-sh/bun/issues/15050) — no native PQueue; custom Map pattern is idiomatic, HIGH confidence
- gh 2.83.2 official manual (cli.github.com/manual/gh_pr_create) — `--title --body --head --base` are sufficient for non-interactive mode, HIGH confidence
- Linear API docs (linear.app/developers/graphql) — `issueCreate` mutation structure, HIGH confidence
- Linear Apollo schema (studio.apollographql.com/public/Linear-API/variant/current/schema/reference/objects/Mutation) — `issue.url` field confirmed on mutation response, HIGH confidence
- Existing `worker/feedback-collector.ts` — `checkLinearStatus` uses same fetch + no-Bearer-prefix auth pattern, HIGH confidence (live code, not docs)
- Existing `worker/feedback-collector.ts` `checkPrStatus` — `Bun.spawn(['gh', ...])` pattern for CLI calls, HIGH confidence

---

## v1.1 Stack Additions (2026-03-20)

> The v1.0 baseline stack (Bun, Hono, Preact/HTM, Zod, yaml, MCP SDK) is complete and validated. This section covers ONLY what v1.1 adds.

### What v1.1 Needs

| Feature | What's needed | Source of truth |
|---------|---------------|-----------------|
| Toast notifications | Zero-dependency custom hook + component (pure Preact/HTM) | No library — handroll it |
| Browser Notification API | Built-in Web API — zero deps | MDN, globally available in secure context |
| Auto-refresh (Runs page) | `useInterval` custom hook — already the pattern in `dashboard.ts` | Copy the dashboard polling pattern |
| `queued_at` timestamp | Schema addition to `Run` type + `run-store.ts` write | No new library needed |
| Queue display in TargetDetail | Read `/api/runs?status=queued&target=X` — existing API | No new route needed |

**Summary: No new npm packages.** All five v1.1 features are implementable with existing stack.

---

### Toast Notification System

**Decision: Custom hook — no library.**

Rationale: The existing codebase is a no-build Preact/HTM app with vendored ESM. Adding a toast library (react-toastify, sonner, hot-toast) would require either a bundler step or an esm.sh CDN import. The toast requirement is simple (trigger feedback + auto-dismiss after 3s), and the dashboard's inline-style convention means a ~50-line custom component fits naturally.

**Pattern to implement:**

```typescript
// frontend/hooks/use-toast.ts
// useToast() → { toasts, addToast, removeToast }
// Toast type: { id: string, message: string, variant: 'success' | 'error' | 'info', at: number }
// Auto-dismiss: setTimeout in addToast, clearTimeout on removeToast
// Position: fixed bottom-right, z-index 200 (above dialog at z-index 100)
```

**Integration point:** App-level singleton hook in `app.ts`, passed down as a context value (or via `@preact/signals` signal) to avoid prop-drilling. The `TriggerDialog` → `handleTrigger` path in `dashboard.ts` fires the toast after `api.triggerRun()` resolves.

**Confidence:** HIGH — standard React/Preact pattern, no library coupling risk.

---

### Browser Notification API

**Decision: Raw Web API — no library, no Service Worker.**

The dashboard runs on localhost (single user, desktop-only per PROJECT.md). Service Worker notifications are needed for mobile/push scenarios. Direct `new Notification()` is the correct choice here.

**Key constraints (from MDN, HIGH confidence):**

1. **Secure context only** — Chrome and Firefox require HTTPS. Exception: `localhost` is a secure context by spec. This dashboard defaults to `127.0.0.1:3201` — no HTTPS needed for Notification API.
2. **User gesture required for `requestPermission()`** — must be called inside a click handler, not on page load. Firefox enforces this from v72+.
3. **Mobile throws TypeError** — `new Notification()` is desktop-only. Not a concern for this dashboard.

**Permission flow:**

```typescript
// frontend/lib/notifications.ts
// Check Notification.permission before requesting
// 'granted' → fire directly
// 'default' → ask once, on a user click (e.g., first run trigger)
// 'denied' → silently skip (never re-request)
```

**Integration point:** The existing global SSE in `app.ts` already listens to `brief-ready` (fires when `run:completed` IPC arrives). The same `es.addEventListener('brief-ready', ...)` handler fires the browser notification. The `run:failed` IPC case currently only calls `closeRunSubscribers()` — add a `broadcastGlobal('run-failed', ...)` call in `ipc.ts` to enable failure notifications too.

**One server change required:** Add `run-failed` global SSE event broadcast alongside the existing `brief-ready`. Currently `run:failed` only closes SSE subscribers — it does not broadcast to global listeners. This is a one-line change in `ipc.ts`.

**Confidence:** HIGH — verified via MDN official docs.

---

### Auto-Refresh (Runs Page)

**Decision: Copy the polling pattern from `dashboard.ts` exactly.**

The `Dashboard` component already has a working `useRef<ReturnType<typeof setInterval>>` + conditional start/stop pattern (poll when active runs present, clear on unmount). The `Runs` page is missing this. No new hook library is needed.

**Current gap in `Runs` component (`frontend/pages/runs.ts`):**
- `useEffect` calls `api.getRuns()` once on mount.
- No polling when a run is `running` or `queued`.
- Parity with dashboard: poll every 5s when any run is active, stop when idle.

**Implementation:** Extract the polling logic from `dashboard.ts` into a `useInterval` custom hook (`frontend/hooks/use-interval.ts`), then use it in both `Dashboard` and `Runs`. This deduplicates ~15 lines of poll/cleanup logic.

**Confidence:** HIGH — direct code pattern from existing dashboard, verified working in Phase 1–4.

---

### `queued_at` Timestamp

**Decision: Add `queued_at?: string` to `Run` type in `shared/types.ts`. Set it in `api.ts` when enqueuing.**

**Current state:**
- `Run` type has `started_at?: string` (set when worker picks up the run) and `completed_at?: string`.
- No field captures when the run was queued (i.e., when `POST /api/runs` was called).
- The Runs page displays `timeAgo(run.started_at)` — queued runs with no `started_at` show `—`.

**Change scope:**
1. `shared/types.ts` — add `queued_at?: string` to `Run` interface.
2. `server/routes/api.ts` — set `queued_at: new Date().toISOString()` when constructing the `Run` object (lines 28–37 in current `api.ts`).
3. `server/routes/api.ts` — same for the webhook route (lines 70–77).
4. `frontend/pages/runs.ts` — display `queued_at` in the run list when `started_at` is absent.
5. `shared/types.ts` — update `WorkerToServer` types if worker needs to relay queued_at (likely not needed — server sets it).

**Confidence:** HIGH — trivial schema addition, no YAML migration needed (YAML store reads with optional fields gracefully).

---

## v1.0 Baseline Stack (Unchanged)

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Bun | 1.2.x (current: 1.2.20+) | Runtime, bundler, test runner | Constraint from PROJECT.md; TypeScript-native, ESM, no config needed. Native `Bun.spawn()` for child process streaming, `Bun.serve()` for HTTP+WebSocket, built-in YAML parse. Bun 1.2 adds 90% Node.js compat, removing most shim concerns. |
| Hono | 4.12.x (current: 4.12.2) | HTTP framework | Designed for Bun — uses Web Standards APIs (Request/Response/Headers) so no adapter needed. Provides `streamSSE()` for log streaming, `upgradeWebSocket` for chat, `serveStatic` for frontend assets. Lightweight (~14KB). The `hono/bun` import gives Bun-specific WebSocket handler. |
| Preact + HTM | Preact 10.23.1, HTM 3.1.1 | Frontend UI | Constraint from design spec. ~4KB total (Preact 3KB + HTM 1KB). No build step — Bun transpiles `.ts` files on-the-fly in dev; `Bun.build()` bundles to single file for production. HTM's tagged template syntax (`html\`...\``) is zero-dependency JSX. Component model + hooks for the chat panel and SSE log stream components. |
| `@modelcontextprotocol/sdk` | 1.27.1 (latest stable v1.x) | MCP server at `/mcp` | Official SDK. Provides `McpServer` class and `StreamableHTTPServerTransport` for the Streamable HTTP transport used in `routes/mcp.ts`. The `@hono/mcp` package (v0.2.4) adds a convenience Hono middleware to mount the MCP server without writing raw transport code. v2 SDK is in pre-alpha; use v1.27.x until stable v2 releases in Q1 2026. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `yaml` (npm) | 2.x | YAML read/write for config files | Use `yaml.stringify()` to serialize targets.yaml and app config — Bun's native `Bun.YAML.parse()` is parse-only, no stringify. The `yaml` library preserves comments and formatting better than `js-yaml`. Used in `services/yaml-store.ts`. |
| `zod` | 3.x | Schema validation at config boundaries | Validate targets.yaml, app config, and IPC messages at parse time. Prevents schema drift silently corrupting runs. Use in `yaml-store.ts` and `worker/ipc.ts`. Required by PROJECT.md "Zod at boundaries" rule. |
| `@hono/mcp` | 0.2.4 | Hono middleware for MCP Streamable HTTP | Mounts `McpServer` onto a Hono app route with correct headers + JSON body parsing. Saves ~30 lines of manual transport wiring. Use in `routes/mcp.ts`. |
| `@preact/signals` | 1.3.0 | Fine-grained reactivity for live state | SSE log stream + run status updates need efficient incremental rendering without full re-renders. Signals avoid the need for Redux/Zustand while staying in the Preact ecosystem. Load via import map in `index.html`. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `bun test` | Unit + integration testing | Built into Bun. Jest-compatible API. No separate vitest/jest dependency needed. Use for yaml-store, IPC message serialization, log-parser, and safehouse flag builder tests. |
| `Bun.build()` | Production frontend bundle | `Bun.build({ entrypoints: ['frontend/app.ts'], outdir: 'dist/' })` bundles Preact+HTM into a single JS file inlined into `index.html`. Only needed for production — dev mode serves `.ts` files directly. |
| TypeScript (via Bun) | Type checking | Bun runs TypeScript natively; no `tsc` needed at runtime. Run `bun tsc --noEmit` for type-only checks during development. Keep strict mode on. |
| `biome` | Lint + format | Already established in the workspace (e2e-pipeline uses it). Consistent with existing plugin conventions. |

## Installation

```bash
# Core app (from kc-nightwatch/app/)
bun add hono zod yaml @modelcontextprotocol/sdk @hono/mcp

# Frontend (loaded via import map in index.html — no npm install needed)
# preact@10.23.1 + htm@3.1.1 + @preact/signals@1.3.0 served from esm.sh CDN
# OR vendored into frontend/lib/ for offline use

# Dev dependencies
bun add -D @types/bun biome

# v1.1 and v2.0: No new packages required
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Custom toast hook (no library) | react-toastify, sonner, hot-toast | Use a library if the toast requirements expand to include: stacking, progress bars, rich actions, or theme matching. Currently overkill — the no-build constraint means any library needs a CDN import or bundler step. |
| Raw `Notification` Web API (no library) | `react-use-notifications` or `use-notification` hooks | Use a wrapper library only if cross-browser fallback behavior needs standardizing. Desktop-only dashboard on localhost has no cross-browser concern. |
| Copy dashboard's `useRef` + `setInterval` pattern | SWR, React Query, TanStack Query | These caching/fetching libraries are excellent for complex stale-while-revalidate needs. This dashboard has simple polling (5s interval, active-only) — a full cache library would be overengineering. |
| `queued_at` field on `Run` type | Separate `queue-store` or event log | A dedicated event log is better for audit trails in multi-user systems. For a single-user dashboard, a timestamp field on the run is sufficient. |
| Bun native IPC (`Bun.spawn` + `ipc` handler) | Unix domain socket via `node:net` | Use `node:net` if the worker needs to be a non-Bun process. For this project, both server and worker are Bun, so native IPC is simpler — no socket file cleanup, no reconnect loop, structured clone serialization. |
| Preact + HTM (no build) | Preact + Vite | Vite is the right choice if the frontend grows beyond ~10 components or if tree-shaking matters. For this dashboard (internal tool, Bun serves it), no build step is simpler to maintain. Switch if performance becomes an issue. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `react-toastify` or `sonner` | Both require npm install + either bundler or esm.sh CDN. No-build constraint makes this complicated and fragile. Toast is ~50 lines of Preact — not worth the dependency. | Custom `useToast` hook |
| `Notification.requestPermission()` on page load | Chrome and Firefox block this (user gesture required). Will silently fail or show a browser warning. | Request on first run trigger (user gesture context) |
| `window.Notification` without feature detection | Throws in non-browser environments (Bun SSR tests). Always gate: `if ('Notification' in window && Notification.permission !== 'denied')` | Feature-detected notification wrapper |
| Service Worker for notifications | Needed for push/mobile; overkill for this localhost desktop dashboard. Adds 50+ lines of SW registration + caching to a zero-config app. | `new Notification()` directly |
| Adding a polling library (SWR, React Query) | Heavyweight for a 5s interval pattern. The dashboard already implements its own polling correctly. | Extract `useInterval` hook from dashboard's existing `setInterval` logic |
| Express or Fastify | Not Bun-native — wrap Node.js HTTP which is slower and heavier. Hono is designed for Web Standards runtimes. | Hono |
| React (full) | 45KB+ bundle for a single-user internal dashboard. No SSR needed. | Preact + HTM |
| `socket.io` | Requires Node.js adapter + extra binary protocol. Bun has WebSocket built into `Bun.serve()` and Hono wraps it cleanly. | Hono `upgradeWebSocket` from `hono/bun` |
| `node:child_process.spawn` | Works on Bun but misses Bun-specific features. `Bun.spawn()` returns a `ReadableStream` for stdout (cleaner async), has native timeout, and integrates with `AbortSignal`. | `Bun.spawn()` |
| MCP SDK v2 pre-alpha | "We anticipate a stable v2 release in Q1 2026" — not stable yet. v1.27.x is the recommended production version. | `@modelcontextprotocol/sdk@^1.27.1` |

## Stack Patterns by Variant

**Toast position strategy:**
- Use `position: fixed; bottom: 24px; right: 24px; z-index: 200` — above TriggerDialog (`z-index: 100`) and BottomNav.
- Stack multiple toasts vertically with `gap: 8px` using a flex column container.
- Auto-dismiss at 3s for success, 5s for error (keep error visible longer for user action).

**Browser notification permission strategy:**
- Check `Notification.permission` before every `new Notification()` call.
- Request permission inside the `handleTrigger` callback in `dashboard.ts` — this is user-gesture context (button click inside TriggerDialog → Start Run).
- Store "asked once" state in `sessionStorage` to avoid re-prompting on page refresh during the same session.

**Auto-refresh parity pattern:**
- Extract to `frontend/hooks/use-poll.ts`:
  ```typescript
  // usePoll(fn, intervalMs, enabled)
  // enabled: boolean — polling only runs when true
  // Returns: void
  // Cleanup: clearInterval on unmount or enabled→false
  ```
- `Dashboard` uses: `usePoll(loadRuns, 5_000, hasActiveRun)`
- `Runs` uses: `usePoll(loadRuns, 5_000, runs.some(r => r.status === 'running' || r.status === 'queued'))`

**`queued_at` display strategy:**
- In run list: show `timeAgo(run.queued_at ?? run.started_at)` — queued runs show time since queuing; running/completed runs show time since start.
- Queue badge in TargetDetail: filter `runs` where `status === 'queued' && target === selectedTarget`. Count > 0 → show badge "N queued".

**`run-failed` SSE event (server change):**
- In `ipc.ts`, case `'run:failed'`: add `broadcastGlobal('run-failed', { run_id: msg.run_id, error: msg.error })` after `closeRunSubscribers()`.
- In `app.ts`, add `es.addEventListener('run-failed', ...)` handler alongside `brief-ready`.
- This enables browser notification on failure without polling.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| `hono@4.12.x` | `bun@1.2.x` | Official Bun support. Import `upgradeWebSocket` from `hono/bun` specifically. |
| `@modelcontextprotocol/sdk@1.27.x` | `hono@4.x` | Use `@hono/mcp@0.2.4` for the Hono middleware. These are independent packages — SDK handles the protocol, @hono/mcp handles route mounting. |
| `preact@10.23.x` + `htm@3.1.1` | Bun frontend transpile | Bun handles `.ts` files with tagged template literals natively. No `.babelrc` or `jsxImportSource` config needed for HTM (HTM bypasses JSX transform entirely). |
| `yaml@2.x` | `zod@3.x` | No compatibility concern — independent packages. |
| `bun@1.2.x` `node:net` | Unix domain sockets | Verified: `Bun.serve({ unix: '/path/to/sock' })` and `node:net` both support Unix sockets in Bun 1.2+. Use `node:net` for the IPC transport (server + worker) to get full TCP-style socket API with reconnect support. |
| Browser Notification API | localhost (no HTTPS needed) | localhost is a secure context by spec — `Notification.requestPermission()` works without HTTPS. Verified in Chrome and Firefox. |

## Sources

**v2.0 sources:**
- Bun 1.3.9 docs (bun.sh/reference/globals/setInterval) — multi-timer pattern confirmed stable, HIGH confidence
- Bun GitHub Issue #15050 (github.com/oven-sh/bun/issues/15050) — no native PQueue; custom Map pattern is idiomatic, HIGH confidence
- gh 2.83.2 official manual (cli.github.com/manual/gh_pr_create) — `--title --body --head --base` are sufficient for non-interactive mode, HIGH confidence
- Linear API docs (linear.app/developers/graphql) — `issueCreate` mutation structure, HIGH confidence
- Linear Apollo schema (studio.apollographql.com/public/Linear-API/variant/current/schema/reference/objects/Mutation) — `issue.url` field confirmed on mutation response, HIGH confidence
- Existing `worker/feedback-collector.ts` — `checkLinearStatus` uses same fetch + no-Bearer-prefix auth pattern, HIGH confidence
- Existing `worker/feedback-collector.ts` `checkPrStatus` — `Bun.spawn(['gh', ...])` pattern for CLI calls, HIGH confidence

**v1.0 sources:**
- [Hono official docs — Bun getting started](https://hono.dev/docs/getting-started/bun) — verified Bun-native support, `serveStatic`, current version 4.12.2
- [Hono SSE streaming helper docs](https://hono.dev/docs/helpers/streaming) — `streamSSE()` API, `writeSSE()` signature
- [Hono WebSocket helper docs](https://hono.dev/docs/helpers/websocket) — `upgradeWebSocket` from `hono/bun`, header mutation limitation
- [Bun WebSocket docs](https://bun.com/docs/runtime/http/websockets) — uWebSockets-based, 7x Node throughput, pub/sub, 120s idle timeout default
- [Bun IPC docs](https://bun.com/docs/guides/process/ipc) — confirmed "only compatible with bun processes"; Unix socket via node:net as alternative
- [Bun child process docs](https://bun.com/docs/runtime/child-process) — `Bun.spawn()` stdout as ReadableStream, `proc.kill('SIGTERM')`
- [Bun YAML docs](https://bun.com/docs/runtime/yaml) — parse-only (no stringify); Zig implementation
- [MCP TypeScript SDK GitHub releases](https://github.com/modelcontextprotocol/typescript-sdk/releases) — v1.27.1 is latest stable v1.x; v2 pre-alpha in progress
- [MCP SDK GitHub README](https://github.com/modelcontextprotocol/typescript-sdk) — `@modelcontextprotocol/hono` helpers, Streamable HTTP transport added 2025-03-26
- [@hono/mcp npm](https://www.npmjs.com/package/@hono/mcp) — v0.2.4, Hono middleware for MCP server mounting
- [Preact no-build workflows guide](https://preactjs.com/guide/v10/no-build-workflows/) — HTM + import maps; Preact 10.23.1, HTM 3.1.1 current
- [yaml npm package](https://www.npmjs.com/package/yaml) — 85M weekly downloads, parse + stringify, TypeScript types (MEDIUM confidence — npm page 403'd, version from ecosystem research)
- [Bun 1.2 release notes](https://socket.dev/blog/bun-1-2-released-90-node-js-compatibility-built-in-s3-object-support) — 90% Node.js compat, Bun 1.2 current minor is 1.2.20+

**v1.1 sources:**
- [MDN: Using the Notifications API](https://developer.mozilla.org/en-US/docs/Web/API/Notifications_API/Using_the_Notifications_API) — permission states, secure context requirement, user gesture requirement, `new Notification()` signature — HIGH confidence
- [MDN: Notification.requestPermission()](https://developer.mozilla.org/en-US/docs/Web/API/Notification/requestPermission_static) — promise-based API, callback deprecated — HIGH confidence
- [Chrome Lighthouse: notification-on-start](https://developer.chrome.com/docs/lighthouse/best-practices/notification-on-start) — do not request on page load; request in user gesture — HIGH confidence
- [Preact no-build workflows guide v11](https://preactjs.com/guide/v11/no-build-workflows/) — custom hooks work identically to React hooks in HTM/Preact — HIGH confidence
- [overreacted.io: Making setInterval Declarative with React Hooks](https://overreacted.io/making-setinterval-declarative-with-react-hooks/) — canonical useInterval pattern, applies to Preact identically — HIGH confidence
- Existing codebase (dashboard.ts lines 54–62) — working polling pattern in production, Phase 1–4 validated — HIGH confidence

---
*Stack research for: Nightwatch Dashboard (Bun + Hono + Preact autonomous agent platform)*
*Researched: 2026-03-18 (v1.0) / 2026-03-20 (v1.1 addendum) / 2026-03-21 (v2.0 addendum)*
