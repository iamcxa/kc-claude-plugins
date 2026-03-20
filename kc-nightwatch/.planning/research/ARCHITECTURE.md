# Architecture Research

**Domain:** Nightwatch Dashboard v1.1 — UX Polish integration
**Researched:** 2026-03-20
**Confidence:** HIGH (direct codebase inspection of all affected files)

## Existing System Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                          Browser (Preact + HTM)                       │
│                                                                        │
│  app.ts (root)                                                         │
│    ├─ ScheduleBar                      ← top bar, always visible      │
│    ├─ [page router via location.hash]                                  │
│    │    ├─ Dashboard (pages/dashboard.ts)                              │
│    │    │    ├─ Sidebar                ← target list + status dots     │
│    │    │    ├─ TargetDetail           ← selected target panel         │
│    │    │    ├─ TriggerDialog          ← run trigger modal             │
│    │    │    └─ ChatPanel              ← inline NW-Claude chat         │
│    │    ├─ Runs (pages/runs.ts)        ← run list + run detail         │
│    │    ├─ Health (pages/health.ts)                                     │
│    │    └─ Config (pages/config.ts)                                     │
│    └─ BottomNav                        ← tab bar                       │
│                                                                        │
│  Dead code                                                             │
│    └─ frontend/components/chat-drawer.ts  ← ORPHAN (unused)           │
└───────────────────────────┬──────────────────────────────────────────┘
                            │ HTTP + SSE
┌───────────────────────────▼──────────────────────────────────────────┐
│                         Hono Server (server/)                          │
│                                                                        │
│  routes/api.ts     GET/POST /api/targets, /api/runs, /api/webhook     │
│  routes/stream.ts  GET /api/runs/:id/stream (SSE), /api/events (SSE)  │
│  routes/chat.ts    POST /api/chat/:target/message + SSE stream         │
│  routes/feedback.ts POST /api/feedback, GET calibration               │
│  routes/health-api.ts GET /api/health/:target                          │
│  routes/config.ts  GET/PUT /api/config + target CRUD                  │
│  routes/schedule.ts GET/PUT /api/schedule                              │
│  routes/mcp.ts     MCP server (12 tools)                               │
│                                                                        │
│  server/ipc.ts     ← SSE fan-out + global broadcast + IPC handler     │
│    sseSubscribers: Map<runId, Set<SSEWriter>>                          │
│    globalSubscribers: Set<SSEWriter>                                   │
│                                                                        │
│  services/run-store.ts   ← YAML-backed run persistence                 │
│  services/yaml-store.ts  ← generic YAML r/w                            │
│  services/chat-manager.ts ← per-target Anthropic SDK sessions          │
└───────────────────────────┬──────────────────────────────────────────┘
                            │ Bun native IPC (process.send)
┌───────────────────────────▼──────────────────────────────────────────┐
│                       Bun Worker (worker/)                             │
│                                                                        │
│  worker/index.ts     ← IPC handler, queue: Run[], currentRun          │
│  worker/executor.ts  ← claude -p spawn, log stream, summary write      │
│  worker/scheduler.ts ← interval timer → enqueue()                     │
│  worker/log-parser.ts ← JSONL → ParsedLogEvent                        │
│  worker/feedback-collector.ts ← PR/Linear status polling              │
└──────────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | Location |
|-----------|----------------|----------|
| `app.ts` | Root render, global SSE listener (`/api/events`), health data loader, page router | `frontend/app.ts` |
| `Dashboard` | Target selection, run trigger coordination, polling while active (5s) | `frontend/pages/dashboard.ts` |
| `Sidebar` | Target list, status dots, health arrows, "Add Target" button (no-op today) | `frontend/components/sidebar.ts` |
| `TargetDetail` | Target metadata, Run/Dry-run buttons, last run status, menu with dead Edit/Chat buttons | `frontend/components/target-detail.ts` |
| `TriggerDialog` | Modal for run mode + custom prompt selection | `frontend/components/trigger-dialog.ts` |
| `Runs` | Run list with filters + run detail view with LogStream. No polling (gap vs Dashboard) | `frontend/pages/runs.ts` |
| `ChatPanel` | Inline NW-Claude chat (live replacement for ChatDrawer) | `frontend/components/chat-panel.ts` |
| `ChatDrawer` | Overlay chat drawer — **DEAD CODE**, not imported anywhere | `frontend/components/chat-drawer.ts` |
| `server/ipc.ts` | SSE fan-out state, global broadcast, IPC handler, heartbeat watchdog | `server/ipc.ts` |
| `run-store.ts` | YAML-backed run list (`nightwatch-runs.yaml`) + per-run summary.yaml | `server/services/run-store.ts` |
| `worker/index.ts` | Queue (`Run[]`), `currentRun`, IPC message router | `worker/index.ts` |
| `worker/executor.ts` | Spawns `claude -p`, streams logs via IPC, writes summary.yaml | `worker/executor.ts` |
| `shared/types.ts` | Central Zod schemas + TypeScript interfaces — single source of truth | `shared/types.ts` |
| `frontend/lib/api.ts` | Typed fetch wrappers — one method per endpoint | `frontend/lib/api.ts` |

---

## v1.1 Feature Integration Analysis

### Feature 1: Toast System

**What it is:** Lightweight overlay notification for run trigger feedback (success/error) and other one-shot messages.

**Integration points:**
- New component: `frontend/components/toast.ts` — renders a fixed-position overlay, manages a queue of `{ id, message, type, duration }` entries with auto-dismiss
- New module: `frontend/lib/use-toast.ts` — module-level callback registration so any page can call `showToast()` without prop drilling

**Mount point:** `app.ts` renders `<Toast />` alongside the page router (outside the page div, at root level). The Toast component registers its handler on mount; any module calls the exported `showToast()` function.

**Consumers:**
- `Dashboard` (`pages/dashboard.ts`): `handleTrigger()` resolves → `showToast('Run queued for {target}', 'success')`, rejects → `showToast('Worker offline', 'error')`
- `app.ts`: optionally show toast on `brief-ready` run completion event

**Data flow:**
```
Dashboard.handleTrigger()
  → api.triggerRun() resolves → showToast('Run queued', 'success')
                     rejects  → showToast('Worker offline', 'error')
  → Toast component auto-dismisses after N ms
```

**What to create:** `frontend/components/toast.ts` (new), `frontend/lib/use-toast.ts` (new)
**What to modify:** `frontend/app.ts` (mount Toast), `frontend/pages/dashboard.ts` (call showToast on trigger)

---

### Feature 2: Browser Notification API

**What it is:** `Notification.requestPermission()` at startup and `new Notification(...)` when a run completes.

**Integration points:**
- `app.ts` already has the global SSE listener for `brief-ready` events (lines 39–47). Run completion arrives there via `broadcastGlobal('brief-ready', ...)` from `server/ipc.ts`.
- Permission request: add `Notification.requestPermission()` inside the startup `useEffect` that sets up the EventSource. Wrap in `'Notification' in window` guard.
- Notification fire: in the existing `brief-ready` listener, after `api.briefChat()`, call `new Notification('Run complete', { body: targetName })`.
- No new component needed — pure logic addition in `app.ts`.

**Current `brief-ready` handler location:** `frontend/app.ts` lines 39–47

**What to modify:** `frontend/app.ts` only — add permission request at startup + notification fire in `brief-ready` handler

---

### Feature 3: Runs Page Auto-Refresh

**What it is:** The Runs page should poll `api.getRuns()` when active runs exist, matching the polling pattern Dashboard already uses.

**Current gap:** `Runs` page (lines 58–67 in `pages/runs.ts`) fetches runs once on mount and never refreshes. A run that transitions from `queued` → `running` → `completed` while the user is on the Runs page requires a manual refresh.

**Dashboard reference implementation** (in `pages/dashboard.ts`):
- `useRef<ReturnType<typeof setInterval>>` for the timer
- `loadRuns()` function: fetches, updates state, checks for active runs (`status === 'running' || status === 'queued'`), starts or clears timer accordingly
- Cleanup in unmount `useEffect`

**What to add to Runs page:**
- `useRef` for poll timer
- `loadRuns()` function wrapping the existing `api.getRuns()` call
- Active-run detection + timer start/stop
- Optional: subscribe to global SSE `brief-ready` to trigger an immediate refresh when a run completes (avoids waiting for next 5s poll)

**What to modify:** `frontend/pages/runs.ts` — add polling pattern identical to Dashboard

---

### Feature 4: `queued_at` Field on Run Type

**What it is:** A timestamp recording when a run was enqueued, distinct from `started_at` (when execution began). Currently runs in `queued` status have no timestamp for when they were queued.

**This is a schema change that touches 4 layers:**

**Layer 1 — `shared/types.ts`**
- Add `queued_at?: string` to the `Run` interface (optional for backward compat with ~100 existing runs in `nightwatch-runs.yaml`)

**Layer 2 — `server/routes/api.ts`**
- `POST /api/runs` (lines 25–41): set `queued_at: new Date().toISOString()` on the `run` object before `appendRun()`
- `POST /api/webhook` (lines 66–81): same

**Layer 3 — `server/services/run-store.ts`**
- No change needed. Run objects are stored and retrieved as-is from YAML.

**Layer 4 — Worker**
- `worker/index.ts` lines 78–92 (`__all__` expansion): set `queued_at` on each `subRun` built during expansion
- `worker/scheduler.ts` lines 22–33: set `queued_at` on the `run` object built by the scheduler interval

**Display changes:**
- `frontend/pages/runs.ts` run list row: for runs with `status === 'queued'` and no `started_at`, show `timeAgo(run.queued_at)` instead of `timeAgo(run.started_at)` (the existing `timeAgo()` helper handles this)
- `frontend/components/target-detail.ts` last run panel: show "Queued X ago" when `status === 'queued'` and `queued_at` is present

**What to modify:** `shared/types.ts`, `server/routes/api.ts`, `worker/index.ts`, `worker/scheduler.ts`, `frontend/pages/runs.ts`, `frontend/components/target-detail.ts`

---

### Feature 5: Queue Visibility in TargetDetail

**What it is:** Show queue depth (how many runs are waiting) for the selected target in the TargetDetail panel.

**Where queue state lives:** `worker/index.ts` maintains `const queue: Run[]` and `let currentRun: Run | null`. It sends `{ type: 'state', queue, current }` IPC messages whenever the queue changes. `server/ipc.ts` receives these in `handleWorkerMessage` but currently only logs them (line 76 — debug log only, no fan-out to frontend).

**Two design options — Option A recommended:**

**Option A — HTTP polling endpoint (recommended):**
- `server/ipc.ts`: add `let lastWorkerState: { queue: Run[]; current?: Run } = { queue: [] }` module-level variable, updated in the `state` case of `handleWorkerMessage`
- `server/routes/api.ts`: add `GET /api/worker/state` returning `lastWorkerState`
- `frontend/lib/api.ts`: add `getWorkerState(): Promise<{ queue: Run[]; current?: Run }>`
- `frontend/pages/dashboard.ts`: call `api.getWorkerState()` in `loadRuns()` (runs every 5s when active), store as `workerQueue` state, pass to TargetDetail

**Option B — Global SSE broadcast (not recommended):**
- Would broadcast a `worker:state` SSE event on every queue change during a run
- Queue changes can happen dozens of times per minute — pollutes the SSE channel designed for infrequent lifecycle events

**TargetDetail display:**
- Accept new prop `workerQueue: Run[]`
- Filter by `run.target === target.name` to get per-target queue items
- Show "X run(s) queued" below the last-run panel when count > 0

**What to modify:** `server/ipc.ts` (store lastWorkerState), `server/routes/api.ts` (add GET /api/worker/state), `frontend/lib/api.ts` (add getWorkerState), `frontend/pages/dashboard.ts` (fetch queue, pass to TargetDetail), `frontend/components/target-detail.ts` (accept + display queue prop)

---

### Feature 6: Sidebar Add Target Button Wiring

**What it is:** The `+ Add Target` button in `Sidebar` has `onClick=${() => {}}` today — two instances of it (line 32: empty-state version; line 75: footer button). It should open the `AddTargetWizard`.

**Current state of AddTargetWizard:** The component exists at `frontend/components/add-target-wizard.ts` and handles both create and edit modes. It is already used in the Config page. Dashboard does not currently mount it.

**Integration points:**
- `Sidebar` Props: add `onAddTarget: () => void` — both `onClick=${() => {}}` instances wire to this
- `Dashboard`: add `showAddWizard: boolean` state + mount `<AddTargetWizard isOpen={showAddWizard} onClose={...} onSaved={...} />`
- Pass `onAddTarget={() => setShowAddWizard(true)}` from Dashboard to Sidebar
- On wizard `onSaved`: reload targets with `api.getTargets()` and refresh run data

**What to modify:** `frontend/components/sidebar.ts` (add onAddTarget prop, wire both buttons), `frontend/pages/dashboard.ts` (add wizard state + mount, pass callback to Sidebar)

---

### Feature 7: Cleanup

**chat-drawer.ts — DELETE:**
- File: `frontend/components/chat-drawer.ts`
- `chat-panel.ts` is the live replacement. `chat-drawer.ts` is not imported from `app.ts`, Dashboard, or any page.
- Verify before deleting: `grep -r "chat-drawer" app/frontend/` should return zero results.

**Disabled buttons in target-detail.ts (lines 83–95):**
- "Edit" button: `aria-disabled="true"`, `title="Coming in Phase 3"` — Edit functionality is implemented (AddTargetWizard handles edit mode via `editTarget` prop). Wire to `onEdit` callback. Pass `editTarget` data to the wizard from Dashboard.
- "Chat" button: `aria-disabled="true"`, `title="Coming in Phase 3"` — ChatPanel is now always visible inline on Dashboard. This menu item is vestigial. Remove it from the dropdown, or change to a no-op label noting chat is in the right panel.

**Dead code in target-detail.ts (line 46):**
- `const phases = lastRun?.log_path ? [] : []` — always evaluates to `[]` regardless of the condition. This was scaffolding never completed. Remove the variable entirely (it is only used in the `phases.length > 0` guard that is therefore always false).

**What to delete:** `frontend/components/chat-drawer.ts`
**What to modify:** `frontend/components/target-detail.ts` (fix/remove disabled buttons, remove dead phases variable)

---

## File Change Matrix

| File | Change | v1.1 Feature(s) |
|------|--------|-----------------|
| `shared/types.ts` | MODIFIED | queued_at field on Run |
| `server/ipc.ts` | MODIFIED | Store lastWorkerState for queue visibility |
| `server/routes/api.ts` | MODIFIED | queued_at on POST /api/runs + webhook; GET /api/worker/state |
| `worker/index.ts` | MODIFIED | queued_at on __all__ sub-runs |
| `worker/scheduler.ts` | MODIFIED | queued_at on scheduled runs |
| `frontend/app.ts` | MODIFIED | Mount Toast; Notification API permission + fire |
| `frontend/lib/api.ts` | MODIFIED | Add getWorkerState() |
| `frontend/lib/use-toast.ts` | NEW | Toast state management (module-level callback) |
| `frontend/components/toast.ts` | NEW | Toast overlay component |
| `frontend/pages/dashboard.ts` | MODIFIED | Toast calls; AddTargetWizard wiring; queue fetch; pass queue to TargetDetail |
| `frontend/pages/runs.ts` | MODIFIED | Polling pattern; show queued_at for queued runs |
| `frontend/components/sidebar.ts` | MODIFIED | Add onAddTarget prop; wire both Add Target buttons |
| `frontend/components/target-detail.ts` | MODIFIED | Queue display prop; fix/remove disabled buttons; remove dead phases variable |
| `frontend/components/chat-drawer.ts` | DELETE | Dead code |

---

## Data Flow Changes

### Run Trigger with Toast

```
User: clicks Run in TargetDetail
  → Dashboard.openDialog(targetName) → TriggerDialog shown
  → User confirms → handleTrigger({ mode, custom_prompt })
  → api.triggerRun({ target, mode, ... })
     ├── 202 Accepted → showToast('Run queued for {target}', 'success')
     │                → loadRuns() [existing]
     └── error        → showToast('Worker offline', 'error')
```

### Run Completion with Browser Notification

```
worker/index.ts: run completes → send({ type: 'run:completed', run_id, summary })
  → server/ipc.ts: handleWorkerMessage → broadcastGlobal('brief-ready', { run_id, summary })
  → browser app.ts: es.addEventListener('brief-ready')
     ├── api.briefChat(target, summary)               [existing]
     ├── new Notification('Run complete', { body })   [NEW]
     └── showToast('{target} run complete', 'success') [NEW, optional]
```

### Queue State Display

```
worker/index.ts: send({ type: 'state', queue, current })  [existing, on every queue change]
  → server/ipc.ts: handleWorkerMessage
     ├── debug log                                         [existing]
     └── lastWorkerState = { queue, current }              [NEW]

Dashboard.loadRuns() [runs every 5s while active]
  → api.getWorkerState()   [NEW call added to loadRuns]
  → setWorkerQueue(queue)
  → pass workerQueue to TargetDetail prop
  → TargetDetail: filter queue by target.name → show "X queued"
```

### Runs Page Live Refresh

```
Runs page mounts
  → loadRuns() → api.getRuns() → setRuns(runs)
  → if active runs: start 5s poll timer [NEW]
  → on brief-ready SSE (optional): loadRuns() immediately [NEW]
  → on unmount: clearInterval [NEW]
```

---

## Architectural Patterns

### Pattern 1: Polling While Active

**What:** Components start a `setInterval` when active runs exist and clear it when idle.
**When to use:** Any page/component that displays live run state (list, counts, status).
**Trade-offs:** Simple, no WebSocket complexity. 5s latency is fine for this tool.

Dashboard is the reference implementation. Runs page needs the same pattern:

```typescript
const pollTimerRef = useRef<ReturnType<typeof setInterval> | null>(null)

function loadRuns() {
  api.getRuns().then(runs => {
    setRuns(runs)
    const active = runs.some(r => r.status === 'running' || r.status === 'queued')
    if (active && !pollTimerRef.current) {
      pollTimerRef.current = setInterval(loadRuns, 5_000)
    } else if (!active && pollTimerRef.current) {
      clearInterval(pollTimerRef.current)
      pollTimerRef.current = null
    }
  }).catch(console.error)
}

useEffect(() => {
  loadRuns()
  return () => { if (pollTimerRef.current) clearInterval(pollTimerRef.current) }
}, [])
```

### Pattern 2: Toast via Module-Level Callback (no Context, no prop-drilling)

**What:** A module exports `showToast()` that delegates to a callback registered by the Toast component at mount time.
**When to use:** Cross-cutting concerns where prop-drilling would be invasive (toast, global errors).
**Trade-offs:** Less "React pure" but avoids Zustand/Redux and Preact context overhead. No build step required.

```typescript
// frontend/lib/use-toast.ts
type ToastType = 'success' | 'error' | 'info'
let _handler: ((msg: string, type: ToastType) => void) | null = null

export function registerToastHandler(fn: typeof _handler) { _handler = fn }
export function showToast(message: string, type: ToastType = 'success') {
  _handler?.(message, type)
}
```

The `Toast` component calls `registerToastHandler(...)` in its `useEffect` on mount. Any module calls `showToast(...)` directly — no prop threading needed.

### Pattern 3: HTTP Polling for Frequent State, SSE for Lifecycle Events

**What:** The existing global SSE channel (`/api/events`) carries infrequent lifecycle events (`brief-ready`, `config-changed`). Frequent state updates (queue depth, run list) use HTTP polling.
**When to use:** Always in this codebase — keep the SSE channel clean.
**Trade-offs:** Two connection patterns, but clear separation of concerns. Prevents SSE flooding.

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Broadcasting Queue State Over Global SSE

**What people do:** Add `broadcastGlobal('worker:state', ...)` every time the queue changes.
**Why it's wrong:** Queue changes multiple times per minute during active runs. Global SSE is designed for infrequent lifecycle events. This conflates the two concerns and creates unnecessary event volume even for a single-user tool.
**Do this instead:** Add `GET /api/worker/state` endpoint. Clients poll it at 5s alongside the run list — one function call added to `loadRuns()`.

### Anti-Pattern 2: Making `queued_at` Required

**What people do:** Add `queued_at: string` (non-optional) to enforce timestamp hygiene.
**Why it's wrong:** ~100 existing runs in `nightwatch-runs.yaml` have no `queued_at`. Non-optional breaks backward compat; requires a data migration.
**Do this instead:** Keep `queued_at?: string` optional. Display logic falls back to `started_at` or `—` when absent. New runs set it; old runs show nothing.

### Anti-Pattern 3: Prop-Drilling Toast State

**What people do:** Add `showToast: (msg: string) => void` to Dashboard, then thread it through to TargetDetail and deeper children.
**Why it's wrong:** Toast is a cross-cutting concern. Prop-drilling invades 4+ components for what is logically a global utility.
**Do this instead:** Module-level callback pattern (Pattern 2 above).

### Anti-Pattern 4: Wiring Add Target via Config Page's Wizard

**What people do:** Navigate to `#/config` when user clicks "+ Add Target" in Sidebar, since the wizard is already there.
**Why it's wrong:** Context switch disrupts the user's flow in the Dashboard. The wizard already supports a standalone `isOpen` prop — it was designed for embedding anywhere.
**Do this instead:** Mount `AddTargetWizard` directly in Dashboard with its own `showAddWizard` state. Dashboard and Config page each manage their own wizard instance independently.

---

## Recommended Build Order

This order respects dependencies. Each step can be done independently of steps at the same level.

```
Step 1 — Schema (foundation, no deps)
  shared/types.ts — add queued_at?: string to Run

Step 2 — Server: set queued_at + queue state endpoint (deps: step 1)
  server/routes/api.ts — queued_at on POST /api/runs and webhook
  server/ipc.ts        — store lastWorkerState on 'state' IPC messages
  server/routes/api.ts — GET /api/worker/state returning lastWorkerState

Step 3 — Worker: set queued_at (deps: step 1, parallel with step 2)
  worker/index.ts   — queued_at on __all__ sub-runs
  worker/scheduler.ts — queued_at on scheduled interval runs

Step 4 — Toast infrastructure (no deps, pure new code)
  frontend/lib/use-toast.ts   — module-level callback + showToast()
  frontend/components/toast.ts — overlay component + registerToastHandler

Step 5 — App root updates (deps: step 4)
  frontend/app.ts — mount <Toast />, add Notification.requestPermission(),
                    fire Notification in brief-ready handler

Step 6 — API client update (deps: step 2 endpoint must exist)
  frontend/lib/api.ts — add getWorkerState()

Step 7 — Dashboard updates (deps: steps 4, 6)
  frontend/pages/dashboard.ts — showToast on trigger, getWorkerState in loadRuns,
                                 AddTargetWizard mount, pass workerQueue to TargetDetail

Step 8 — Component updates (deps: step 7 for prop additions)
  frontend/components/target-detail.ts — workerQueue prop, fix disabled buttons,
                                          remove dead phases variable
  frontend/components/sidebar.ts       — onAddTarget prop, wire both buttons

Step 9 — Runs page refresh (deps: step 1 for queued_at display)
  frontend/pages/runs.ts — polling pattern, show queued_at for queued runs

Step 10 — Cleanup (last, after confirming nothing references removed code)
  DELETE frontend/components/chat-drawer.ts
```

---

## Sources

- Direct codebase inspection (2026-03-20):
  - `app/shared/types.ts` — Run interface, IPC message types
  - `app/server/ipc.ts` — SSE fan-out, global broadcast, handleWorkerMessage (lines 69–96)
  - `app/server/routes/api.ts` — POST /api/runs (lines 25–41), POST /api/webhook (lines 66–81)
  - `app/server/services/run-store.ts` — YAML-backed run persistence
  - `app/worker/index.ts` — queue: Run[], currentRun, IPC handler, __all__ expansion (lines 61–121)
  - `app/worker/scheduler.ts` — interval timer, Run construction (lines 22–33)
  - `app/frontend/app.ts` — root component, global SSE, brief-ready handler (lines 39–47)
  - `app/frontend/pages/dashboard.ts` — polling reference (lines 33–63)
  - `app/frontend/pages/runs.ts` — current no-polling gap (lines 58–67)
  - `app/frontend/components/sidebar.ts` — unconnected Add Target buttons (lines 32, 75)
  - `app/frontend/components/target-detail.ts` — disabled buttons (lines 83–95), dead phases (line 46)
  - `app/frontend/components/chat-drawer.ts` — confirmed orphan (no imports in app.ts or pages)
  - `app/frontend/lib/api.ts` — full endpoint inventory
- `.planning/PROJECT.md` — v1.1 requirements list

---
*Architecture research for: Nightwatch Dashboard v1.1 UX Polish*
*Researched: 2026-03-20*
