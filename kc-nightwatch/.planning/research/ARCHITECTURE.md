# Architecture Research

**Domain:** Nightwatch Dashboard v2.0 — Parallel Execution + Auto-Action
**Researched:** 2026-03-21
**Confidence:** HIGH (direct codebase inspection of all affected files; v1.1 architecture fully known)

---

## Existing System Overview (v1.1 Baseline)

```
┌──────────────────────────────────────────────────────────────────────┐
│                          Browser (Preact + HTM)                       │
│  app.ts → [Dashboard | Runs | Health | Config]  +  BottomNav          │
└───────────────────────────┬──────────────────────────────────────────┘
                            │ HTTP + SSE
┌───────────────────────────▼──────────────────────────────────────────┐
│                         Hono Server (server/)                          │
│  routes/api.ts  routes/stream.ts  routes/chat.ts  routes/feedback.ts  │
│  routes/schedule.ts  routes/config.ts  routes/mcp.ts  routes/health-api│
│  ipc.ts — SSE fan-out + global broadcast + IPC handler                 │
│  services: run-store, yaml-store, feedback-store, chat-manager         │
└───────────────────────────┬──────────────────────────────────────────┘
                            │ Bun native IPC (process.send)
┌───────────────────────────▼──────────────────────────────────────────┐
│                       Bun Worker (worker/)                             │
│  index.ts    — single queue: Run[], currentRun: Run | null             │
│  executor.ts — claude -p spawn, log stream, summary write              │
│  scheduler.ts — global interval timer → enqueue(__all__)              │
│  feedback-collector.ts — PR/Linear status via gh CLI + Linear API      │
└──────────────────────────────────────────────────────────────────────┘

Storage: YAML files in ~/.claude/kc-plugins-config/
  nightwatch-targets.yaml   nightwatch-runs.yaml
  nightwatch-feedback.yaml  nightwatch-app.yaml
  nightwatch-self-repair.yaml
```

### Current Concurrency Model (v1.1)

The worker has a **single queue** and **single currentRun**. `processNextRun()` is guarded by `if (currentRun || queue.length === 0) return`. All targets share one lane. A `__all__` trigger expands into N sub-runs that all sit in the same sequential queue.

### Current Scheduling Model (v1.1)

`scheduler.ts` has a single `setInterval` driven by `ScheduleConfig.interval_hours` (global). When it fires, it enqueues `target: '__all__'`. There is no per-target schedule.

---

## v2.0 Feature Integration Analysis

### Feature 1: Parallel Execution (Per-Target Isolation)

**Goal:** Different targets run concurrently. Same target queues (max 1 active per target).

#### What Changes in the Worker

The current single `queue: Run[]` + `currentRun: Run | null` becomes a **per-target execution map**.

**New data structures:**

```typescript
// worker/index.ts (MODIFIED)
const targetQueues: Map<string, Run[]> = new Map()   // pending per target
const activeRuns: Map<string, Run> = new Map()       // running per target
```

**New `processTarget(targetName)` function (replaces `processNextRun`):**
```typescript
async function processTarget(targetName: string): Promise<void> {
  if (activeRuns.has(targetName)) return          // already running for this target
  const queue = targetQueues.get(targetName) ?? []
  if (queue.length === 0) return
  const run = queue.shift()!
  activeRuns.set(targetName, run)
  sendState()
  try {
    await executeRun(run, resolveTarget(targetName), { ... })
  } finally {
    activeRuns.delete(targetName)
    sendState()
    void processTarget(targetName)    // drain next in this target's queue
  }
}

function enqueue(run: Run): void {
  const target = run.target === SCHEDULER_RUNS_ALL_TARGET ? null : run.target
  if (target === null) {
    // expand __all__ inline (same as today)
    for (const t of Object.keys(targetsMap)) enqueue({ ...run, target: t, id: randomUUID() })
    return
  }
  if (!targetQueues.has(target)) targetQueues.set(target, [])
  targetQueues.get(target)!.push(run)
  sendState()
  void processTarget(target)     // each target drains independently
}
```

**`sendState()` shape change:**

The IPC `state` message currently carries `{ queue: Run[], current?: Run }`. With parallel execution it becomes:
```typescript
// NEW IpcMessage shape (shared/types.ts MODIFIED)
{ type: 'state'; targets: Record<string, { queue: Run[]; current?: Run }> }
```

Both the server's `getLastWorkerState()` and the frontend's `workerQueue` display must update to match.

**`killAllActive()` update:** Iterates `activeRuns` values (not a single `currentRun`). Already uses `activePids: Set<number>` so no change there.

**Cancel logic:** `cancel(run_id)` must search `activeRuns` (SIGTERM) and all `targetQueues` (splice).

**Integration points — Worker:**
- `worker/index.ts` — MODIFIED (queue model, enqueue, processTarget, cancel, state broadcast)
- `worker/executor.ts` — NO CHANGE (single-run execution is already correct; parallelism is a queue concern)
- `shared/types.ts` — MODIFIED (`WorkerToServer.state` payload shape; `AppConfig.max_concurrent_runs` becomes `number` not `literal(1)`)

#### What Changes in the Server

`ipc.ts` `getLastWorkerState()` returns the new per-target shape. The `GET /api/worker/state` endpoint returns the same. No structural change — just the payload type widens.

**Frontend:**
- `TargetDetail`: queue display currently filters `workerQueue` by target name. With per-target state this becomes a direct lookup: `state.targets[target.name]`. Simpler, not harder.
- `Dashboard`: `loadRuns()` still calls `api.getWorkerState()` every 5s. No polling rate change needed.

#### New Constant

```typescript
// shared/constants.ts — ADD
export const MIN_SCHEDULE_INTERVAL_HOURS = 1/6   // 10 minutes
```

---

### Feature 2: Per-Target Scheduling

**Goal:** Each target can have its own `interval_hours`. A global fallback applies when no per-target schedule is set. Minimum 10min interval enforced.

#### Schema Changes

```typescript
// shared/types.ts — MODIFIED
export interface Target {
  // ... existing fields ...
  schedule?: {           // NEW: per-target override
    enabled?: boolean
    interval_hours?: number
  }
}

export interface ScheduleConfig {
  enabled: boolean
  interval_hours?: number       // global fallback
  self_repair_before: boolean
  per_target?: Record<string, { enabled?: boolean; interval_hours?: number }>  // NEW
}
```

The `per_target` map in `ScheduleConfig` is the authoritative schedule state sent over IPC. The `Target.schedule` in `targets.yaml` is the source at config-load time — copied into `ScheduleConfig.per_target` on startup or config reload.

#### What Changes in the Scheduler

**Current:** `scheduler.ts` has one `setInterval`. New model: **one timer per target**.

```typescript
// worker/scheduler.ts — MODIFIED
const schedulerTimers: Map<string, ReturnType<typeof setInterval>> = new Map()

export function startScheduler(
  config: ScheduleConfig,
  targets: Record<string, Target>,
  enqueue: (run: Run) => void
): void {
  stopAllSchedulers()
  if (!config.enabled) return

  const globalInterval = config.interval_hours
  for (const [name, target] of Object.entries(targets)) {
    const override = config.per_target?.[name] ?? target.schedule
    if (override?.enabled === false) continue  // explicitly disabled for this target
    const hours = override?.interval_hours ?? globalInterval
    if (!hours) continue

    const intervalMs = Math.max(hours, MIN_SCHEDULE_INTERVAL_HOURS) * 3_600_000
    const timer = setInterval(() => {
      enqueue({ id: randomUUID(), target: name, mode: 'production', trigger: 'interval', ... })
    }, intervalMs)
    schedulerTimers.set(name, timer)
  }
}

export function stopAllSchedulers(): void {
  for (const t of schedulerTimers.values()) clearInterval(t)
  schedulerTimers.clear()
}
```

**Worker `index.ts` startup:** After loading targets, call `startScheduler(scheduleConfig, targetsMap, enqueue)`. On IPC `schedule` message: call `startScheduler` again with updated config and current `targetsMap`.

**Targets reload:** When config is saved (via `PUT /api/config/targets`), server sends `{ type: 'schedule', config }` IPC. Worker calls `startScheduler` with refreshed targets.

#### Frontend Schedule UI (ScheduleBar + Config Page)

The top `ScheduleBar` component shows the global schedule. For per-target schedule display, the existing `TargetDetail` panel is the natural home — add a small "Schedule: every Xh" row next to the target metadata.

**Integration points:**
- `shared/types.ts` — MODIFIED (`Target.schedule`, `ScheduleConfig.per_target`)
- `worker/scheduler.ts` — MODIFIED (multi-timer model)
- `worker/index.ts` — MODIFIED (pass targets to startScheduler; on config reload restart schedulers)
- `server/routes/schedule.ts` — MODIFIED (accept `per_target` in PUT body, pass through)
- `server/routes/config.ts` — MODIFIED (on targets save, trigger schedule restart via IPC)
- `frontend/components/schedule-bar.ts` — MINOR (shows global; no per-target display here)
- `frontend/components/target-detail.ts` — MODIFIED (show per-target schedule if set)
- `frontend/pages/config.ts` (or `target-detail.ts`) — optional per-target schedule editor

---

### Feature 3: Auto PR Creation

**Goal:** When nightwatch produces code changes, auto-create a PR without human approval. The PR URL appears in `RunSummaryAction.pr_url` (field already exists in the schema).

#### Where It Lives

This happens **inside the nightwatch skill** (the claude -p subprocess), not in the app. The app does not need to create PRs — the kc-nightwatch skill already creates PRs in Phase 4. The app's role is:

1. Surface `pr_url` from the run summary (already done: `ActionCard` shows "View PR" link)
2. Provide feedback collection for merged/closed PRs (already done: `feedback-collector.ts`)
3. Trigger outcome tracking when a new PR URL appears

**What the app needs to enable this:**
- No new skill changes (nightwatch skill already creates PRs — the `--dry-run` guard just prevents it)
- The `actions` field in `RunSummaryAction` already has `pr_url?: string`
- The summary parser in `executor.ts` already reads `summary.yaml` written by the skill

**What changes:**
- **Run mode expansion:** Add `'production-auto'` mode variant or a `flags.auto_pr: boolean` to `Run` that removes any human-approval gate in the custom_prompt. Since the skill itself controls PR creation via its internal logic, the app likely passes `auto_create_pr: true` in the custom prompt injected at run start.

Actually, reviewing the executor: `custom_prompt` is passed as `--append-system-prompt`. The trigger dialog can inject `[AUTO] Create PRs without confirmation.` when auto mode is requested.

**No new app components needed.** The feature is in the skill. The app needs:
- A run mode or flag in the trigger UI that passes the auto-create instruction
- The existing `ActionCard.pr_url` display already handles it
- The `feedback-collector.ts` already polls PR status

**Integration points (minimal):**
- `shared/types.ts` — MINOR: add `'production-auto'` to `Run['mode']` union OR use existing `custom_prompt`
- `frontend/components/trigger-dialog.ts` — MODIFIED: add "Auto-create PRs" toggle that sets mode/flag
- `worker/executor.ts` — MINOR: if `run.mode === 'production-auto'`, inject auto-create system prompt

---

### Feature 4: Auto Linear Issue Creation

**Goal:** When nightwatch identifies improvement signals, auto-create Linear issues. The issue URL appears in `RunSummaryAction` (no `linear_url` field yet — needs adding).

#### Schema Addition

```typescript
// shared/types.ts — MODIFIED
export interface RunSummaryAction {
  // ... existing ...
  linear_url?: string    // NEW
}
```

#### Where It Lives

Same pattern as auto PR: the nightwatch skill creates issues, writes `linear_url` in `summary.yaml`. The app's role:

1. Surface `linear_url` in `ActionCard` (similar to `pr_url` "View PR" link)
2. Collect feedback via `checkLinearStatus()` (already implemented in `feedback-collector.ts`)

**What the app needs:**
- `ActionCard` MODIFIED: render "View Issue" link when `linear_url` is present
- `feedback-collector.ts` MODIFIED: already has `checkLinearStatus()` — wire it to `collectImplicitFeedback` alongside PR checking (today only PR URLs are collected; add linear pass)
- `summary.yaml` parsing in `executor.ts`: no change — it reads all fields from per_target.actions as-is

**Integration points:**
- `shared/types.ts` — MODIFIED: add `linear_url?` to `RunSummaryAction`
- `frontend/components/action-card.ts` — MODIFIED: show "View Issue" link when `linear_url` present
- `worker/feedback-collector.ts` — MODIFIED: include `linear_url` actions in implicit feedback loop

---

### Feature 5: Outcomes Page

**Goal:** Aggregate view of all PRs and Linear issues across all runs, filterable by target/status.

#### New Page

```
frontend/pages/outcomes.ts   ← NEW
```

**Data source:** The page calls `api.getRuns()` (existing), then for each completed run fetches the summary to extract `actions` with `pr_url` or `linear_url`. This is the same data pattern as the Runs page's detail view.

**Performance:** Fetching all run summaries on page load is expensive if there are 100 runs. Two options:

Option A: Fetch lazily — load summaries only for completed runs that have `total_actions > 0`. Use a new `GET /api/outcomes` endpoint that pre-aggregates from all summaries server-side.

Option B: Use the existing `GET /api/runs` + per-run `GET /api/runs/:id` with client-side aggregation, capped at last 20 runs.

**Recommendation: Option A** — new `GET /api/outcomes` endpoint. Server aggregates once; frontend gets a flat list.

#### New API Endpoint

```typescript
// server/routes/api.ts — ADD
apiRoutes.get('/api/outcomes', async (c) => {
  const target = c.req.query('target')
  const runs = await listRuns({ status: 'completed' })
  const outcomes: OutcomeItem[] = []
  for (const run of runs.slice(0, 50)) {  // last 50 completed runs
    const detail = await getRun(run.id)
    for (const [t, targetData] of Object.entries(detail?.summary?.per_target ?? {})) {
      if (target && t !== target) continue
      for (const action of targetData.actions ?? []) {
        if (action.pr_url || action.linear_url) {
          outcomes.push({ run_id: run.id, target: t, action, run_started: run.started_at })
        }
      }
    }
  }
  return c.json(outcomes)
})
```

**New type:**
```typescript
// shared/types.ts — ADD
export interface OutcomeItem {
  run_id: string
  target: string
  run_started?: string
  action: RunSummaryAction   // has pr_url and/or linear_url
}
```

#### Frontend Changes

- `frontend/pages/outcomes.ts` — NEW (table view: target, signal summary, type, PR link, Linear link, created date, feedback status)
- `frontend/components/bottom-nav.ts` — MODIFIED: add "Outcomes" tab (5th tab)
- `frontend/app.ts` — MODIFIED: add `#/outcomes` route branch
- `frontend/lib/api.ts` — MODIFIED: add `getOutcomes(filter?: { target? })` method

---

### Feature 6: NW-Claude Awareness of Outcomes

**Goal:** Chat can answer "what PRs were created for target X?" and "did that PR get merged?".

#### Integration

`mcp-tools.ts` already has `nw_get_proposals` and `nw_get_run`. Add two new MCP tools:

```typescript
// server/services/mcp-tools.ts — ADD tools
nw_get_outcomes: list OutcomeItems (calls the same aggregation as GET /api/outcomes)
nw_get_outcome_status: check current PR/Linear status for a specific signal_id
```

The chat manager sends the MCP server alongside the chat session — NW-Claude can query outcomes via these tools without any frontend changes.

**Integration points:**
- `server/services/mcp-tools.ts` — MODIFIED: add 2 new tools
- No frontend changes needed (NW-Claude's awareness is tool-driven)

---

### Feature 7: Implementation Outcome Tracking (Phase 0.6)

**Goal:** Track whether merged PRs actually improved the target's indicators. Requires before/after indicator measurement comparison.

#### Data Model (already partially exists)

`ImplementationOutcome` type is already defined in `shared/types.ts`:
```typescript
export interface ImplementationOutcome {
  proposal_id: string; pr_url: string; target: string
  indicator: string; before: number; after: number; delta: number; effective: boolean
}
```

The field `per_target[].implementation_outcomes` is already in `PerTargetSummary`.

#### Measurement Flow

1. At run start: Phase 0.5 measures baseline indicators and writes them to `summary.yaml`
2. A merged PR means the change is live in the target repo
3. Next run for the same target: Phase 0.6 compares new baseline to the stored before-value
4. Delta + `effective` flag written to `implementation_outcomes` in summary

**The measurement logic lives in the kc-nightwatch skill** (Phase 0.6). The app only needs to:
- Display `implementation_outcomes` in the Runs detail page (next to actions)
- Surface `implementation_outcomes` in the Outcomes page
- Pass `implementation_outcomes` to NW-Claude via an MCP tool

**Integration points:**
- `frontend/pages/runs.ts` — MODIFIED: render `implementation_outcomes` section in run detail
- `frontend/pages/outcomes.ts` — MODIFIED (part of page design): include outcome tracking column
- `server/services/mcp-tools.ts` — already has `nw_get_run` which returns full summary including `implementation_outcomes`

---

### Feature 8: UI Fix — Bottom Nav Gap

**What:** Black line between content area and bottom nav bar.

**Root cause (to verify):** Likely a `height: 100%` vs `height: 100vh` mismatch, or a missing `overflow: hidden` on the page container that allows content to overflow behind the nav.

**Integration:** `frontend/components/bottom-nav.ts` (MINOR CSS fix). No logic change.

---

## Complete Component Change Matrix

| File | Change | Feature(s) |
|------|--------|-----------|
| `shared/types.ts` | MODIFIED | `WorkerToServer.state` per-target shape; `ScheduleConfig.per_target`; `Target.schedule`; `RunSummaryAction.linear_url`; `OutcomeItem` type; `AppConfig.max_concurrent_runs` literal→number |
| `shared/constants.ts` | MODIFIED | Add `MIN_SCHEDULE_INTERVAL_HOURS` |
| `worker/index.ts` | MODIFIED | Per-target queues + activeRuns map; new enqueue/processTarget/cancel logic; pass targets to scheduler |
| `worker/scheduler.ts` | MODIFIED | Multi-timer model; per-target intervals; minimum enforcement |
| `worker/executor.ts` | MINOR | Auto-create system prompt injection for `production-auto` mode |
| `worker/feedback-collector.ts` | MODIFIED | Add `linear_url` actions to implicit feedback collection loop |
| `server/ipc.ts` | MODIFIED | `lastWorkerState` shape widens to per-target |
| `server/routes/api.ts` | MODIFIED | Add `GET /api/outcomes` endpoint |
| `server/routes/schedule.ts` | MODIFIED | Accept `per_target` in PUT body |
| `server/routes/config.ts` | MODIFIED | On targets save, re-send schedule IPC to trigger scheduler restart |
| `server/services/mcp-tools.ts` | MODIFIED | Add `nw_get_outcomes` + `nw_get_outcome_status` tools |
| `frontend/app.ts` | MODIFIED | Add `#/outcomes` route |
| `frontend/lib/api.ts` | MODIFIED | Add `getOutcomes()` method |
| `frontend/pages/outcomes.ts` | NEW | Outcomes aggregate page |
| `frontend/pages/runs.ts` | MODIFIED | Render `implementation_outcomes` section in detail view |
| `frontend/components/action-card.ts` | MODIFIED | Add "View Issue" link for `linear_url` |
| `frontend/components/target-detail.ts` | MODIFIED | Show per-target schedule if set |
| `frontend/components/trigger-dialog.ts` | MODIFIED | Add "Auto-create PRs" toggle |
| `frontend/components/bottom-nav.ts` | MODIFIED | Add Outcomes tab; fix nav gap CSS |

---

## Data Flow Changes

### Parallel Execution — State Flow

```
User triggers run for target-A
  → api.triggerRun({ target: 'target-a', ... })
  → server: appendRun, sendToWorker({ type: 'enqueue', run })
  → worker: enqueue(run)
     → targetQueues.get('target-a').push(run)   [NEW]
     → processTarget('target-a')
        ├── activeRuns.has('target-a')? NO → start run
        └── executeRun() running in background

  (meanwhile, target-b runs independently — no blocking)

  sendState() → { type: 'state', targets: {
    'target-a': { queue: [], current: runA },
    'target-b': { queue: [runB2], current: runB1 }   ← parallel
  }}
```

### Per-Target Scheduling — Startup Flow

```
Worker starts
  → readTargets() → targetsMap
  → loadOrCreateAppConfig() → scheduleConfig
  → startScheduler(scheduleConfig, targetsMap, enqueue)
     → for each target: create timer with per-target OR global interval
     → timers fire independently → enqueue({ target: specificTarget, trigger: 'interval' })
```

### Auto PR + Outcome Flow

```
executeRun() → claude -p spawned with auto_create_pr system prompt
  → NW skill Phase 4: creates PR, writes pr_url to summary.yaml
  → executor reads summary.yaml → send({ type: 'run:completed', summary })

server: handleWorkerMessage('run:completed')
  → broadcastGlobal('brief-ready', { run_id, summary })

browser: 'brief-ready' SSE event
  → api.briefChat(target, summary)  ← NW-Claude sees PR URLs
  → Outcomes page re-fetches via usePoll

feedback-collector (next run):
  → collectImplicitFeedback(actionsWithPrAndLinear)   ← checks gh + Linear API
  → appendFeedback() with pr_status / linear_status source
```

### Outcomes Page Data Flow

```
User navigates to #/outcomes
  → outcomes.ts mounts → api.getOutcomes()
  → GET /api/outcomes
     → server: listRuns({ status: 'completed' })
     → for each run.id: getRun(id) → extract per_target.actions with pr_url/linear_url
     → return OutcomeItem[]
  → render table sorted by run_started desc
  → usePoll(30_000) for background refresh (slow poll — outcomes don't change rapidly)
```

---

## Architectural Patterns

### Pattern 1: Per-Target Queue Isolation

**What:** Replace single `queue + currentRun` with `Map<target, queue> + Map<target, activeRun>`. Each target's queue drains independently via `processTarget(targetName)`.

**When to use:** Any time you need "different types queue separately, same type queues together" — the generalization of v1.1's max-1 global concurrency.

**Trade-offs:** Slightly more state to manage. `sendState()` payload is larger. Cancel must search all per-target queues. The benefit is straightforward: a slow target (30min run) no longer blocks all other targets.

**Key invariant to preserve:** `processTarget` must be idempotent — called multiple times for the same target while it's already active must be a no-op (guard: `if (activeRuns.has(targetName)) return`).

### Pattern 2: Per-Timer Scheduling

**What:** One `setInterval` per target instead of one global timer. Each timer fires independently, enqueues only its own target.

**When to use:** When execution units need different rates. Also cleaner semantics: stopping a target's schedule is `clearInterval(schedulerTimers.get(name))` — no need to restart the global timer.

**Trade-offs:** More timers in memory. For 10 targets this is negligible. The alternative (one global timer that checks per-target overrides) adds branching complexity for marginal memory savings.

### Pattern 3: Server-Side Aggregation for Outcomes

**What:** `GET /api/outcomes` aggregates across run summaries server-side. Frontend gets a flat list.

**When to use:** When the query involves joining multiple files/records and pagination or filtering is needed. Avoids the frontend doing 100 sequential `getRun()` calls.

**Trade-offs:** Server holds more logic. But the pattern is consistent with how `health-api.ts` already aggregates run history into health data.

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Global Lock for Parallel Execution

**What people do:** Add a `runningCount: number` and allow up to N concurrent runs total (semaphore).

**Why it's wrong:** The requirement is not "N runs total" — it is "1 per target, unlimited across targets." A global semaphore would still block target-B if target-A fills the N slots. Per-target isolation maps directly to the requirement.

**Do this instead:** Per-target `activeRuns` map. Guard is `activeRuns.has(targetName)` not a global counter.

### Anti-Pattern 2: Changing the IPC Transport for Parallelism

**What people do:** Switch to a shared database or event bus to coordinate parallel workers.

**Why it's wrong:** Bun native IPC works perfectly for 1 server ↔ 1 worker. Parallelism is a queue concern inside the worker, not a transport concern. Adding a second worker process would require a coordinator and break the clean two-process architecture.

**Do this instead:** Keep one worker process. Manage N concurrent `executeRun()` calls inside it via the per-target queue model. Bun handles concurrent async functions natively.

### Anti-Pattern 3: Fetching Outcomes Via Many Individual Run Fetches in the Frontend

**What people do:** Frontend calls `api.getRun(id)` for every run in the list to build the outcomes table.

**Why it's wrong:** 50 runs = 50 serial fetches. Runs are YAML-backed; each fetch reads a YAML file. Visible lag on page load.

**Do this instead:** `GET /api/outcomes` — server-side aggregation, single HTTP round trip.

### Anti-Pattern 4: Per-Target Schedule in `targets.yaml` Only

**What people do:** Read per-target schedule exclusively from `targets.yaml` each time a scheduler tick fires.

**Why it's wrong:** `targets.yaml` can change mid-session. If the scheduler reads it every tick, a malformed YAML write during a run could crash the scheduler. Also, the IPC `schedule` message is the authoritative runtime state — `targets.yaml` is the source of truth at startup/reload only.

**Do this instead:** Load per-target schedule from `targets.yaml` at startup into `ScheduleConfig.per_target`. On config save (via API), re-send `{ type: 'schedule', config }` IPC to restart all schedulers with the new per-target map. The worker's schedulers always run from in-memory `ScheduleConfig`, not disk.

---

## Suggested Build Order

Dependencies flow from schema → worker → server → frontend.

```
Step 1 — Schema (foundation, blocks all other steps)
  shared/types.ts — per-target state shape, ScheduleConfig.per_target,
                    Target.schedule, RunSummaryAction.linear_url,
                    OutcomeItem, AppConfig.max_concurrent_runs widening
  shared/constants.ts — MIN_SCHEDULE_INTERVAL_HOURS

Step 2 — Worker: parallel queue (deps: step 1)
  worker/index.ts — targetQueues + activeRuns, new enqueue/processTarget/cancel
  RATIONALE: This is the most complex change. Isolate it early to validate
             before building features that depend on correct parallelism.

Step 3 — Worker: per-target scheduler (deps: step 1, step 2 for enqueue signature)
  worker/scheduler.ts — multi-timer model, min interval enforcement

Step 4 — Server: outcomes endpoint + state shape (deps: step 1)
  server/ipc.ts       — widen lastWorkerState to per-target shape
  server/routes/api.ts — GET /api/outcomes
  server/routes/schedule.ts — accept per_target in PUT body
  server/routes/config.ts   — trigger schedule IPC on targets save

Step 5 — Server: MCP tools (deps: step 1, step 4)
  server/services/mcp-tools.ts — nw_get_outcomes + nw_get_outcome_status

Step 6 — Worker: auto PR + linear feedback wiring (deps: step 1)
  worker/executor.ts            — auto-create system prompt injection
  worker/feedback-collector.ts  — add linear_url to implicit feedback loop
  RATIONALE: Independent of parallelism changes; can be done in parallel with steps 2-3.

Step 7 — Frontend: API client + route (deps: steps 4 endpoints must exist)
  frontend/lib/api.ts  — add getOutcomes()
  frontend/app.ts      — add #/outcomes route

Step 8 — Frontend: Outcomes page (deps: step 7)
  frontend/pages/outcomes.ts (NEW) — table view of PRs + Linear issues

Step 9 — Frontend: Action card + trigger dialog updates (deps: step 1)
  frontend/components/action-card.ts  — linear_url "View Issue" link
  frontend/components/trigger-dialog.ts — Auto-create PRs toggle

Step 10 — Frontend: Run detail + target detail updates (deps: step 1, step 8)
  frontend/pages/runs.ts             — implementation_outcomes section
  frontend/components/target-detail.ts — per-target schedule display

Step 11 — Frontend: Bottom nav + UI fix (deps: step 8 page must exist)
  frontend/components/bottom-nav.ts — add Outcomes tab, fix gap CSS
```

**Parallelization opportunities:**
- Steps 2 and 6 can run in parallel (different files, no deps between them)
- Step 4 can start as soon as step 1 is done (parallel with steps 2-3)
- Steps 7-11 all depend on server endpoints (step 4) but not on each other

---

## Integration Points Summary

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Worker queue → execution | In-process `processTarget()` calls | Each target drains its own queue concurrently via async functions |
| Worker → Server | Bun native IPC `process.send()` | State message shape changes: per-target map instead of single queue |
| Server → Frontend (live state) | HTTP polling `GET /api/worker/state` (5s) | Payload widens; frontend lookup changes from filter to direct key access |
| Server → Frontend (outcomes) | HTTP `GET /api/outcomes` | New endpoint; 30s poll from Outcomes page |
| Server → NW-Claude (chat) | MCP tools via Anthropic SDK | 2 new tools expose PR/Linear outcome data |
| Skill → App (PR/Linear URLs) | `summary.yaml` written by skill, read by executor | `linear_url` field added alongside existing `pr_url` |
| Feedback loop (implicit) | `gh pr view` + Linear GraphQL API | `feedback-collector.ts` extended to process `linear_url` actions |

---

## Sources

Direct codebase inspection (2026-03-21):
- `app/worker/index.ts` — queue model (lines 61-121), __all__ expansion (lines 73-98)
- `app/worker/scheduler.ts` — single global timer, ScheduleConfig dependency
- `app/worker/executor.ts` — executeRun() signature, summary.yaml parsing, feedback wiring
- `app/worker/feedback-collector.ts` — checkPrStatus(), checkLinearStatus() implementations
- `app/server/ipc.ts` — lastWorkerState, IPC message handler
- `app/server/routes/api.ts` — existing endpoints, POST /api/runs trigger
- `app/server/services/run-store.ts` — listRuns(), getRun() signatures
- `app/server/services/mcp-tools.ts` — existing 12 tools
- `app/shared/types.ts` — Run, Target, ScheduleConfig, RunSummaryAction, ImplementationOutcome
- `app/frontend/components/action-card.ts` — pr_url display, feedback buttons
- `app/frontend/pages/runs.ts` — detail view, action card rendering
- `app/frontend/lib/api.ts` — full endpoint inventory
- `.planning/PROJECT.md` — v2.0 requirements list

---
*Architecture research for: Nightwatch Dashboard v2.0 Parallel Execution + Auto-Action*
*Researched: 2026-03-21*
