# Phase 6: Frontend Wiring - Context

**Gathered:** 2026-03-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Wire Phase 5's data infrastructure (queued_at, worker state endpoint, run:failed SSE) to the Preact/HTM frontend. Add toast notifications, browser notifications, queue display, and Runs page auto-refresh. Pure frontend phase — no server changes beyond adding `getWorkerState()` to the API client.

</domain>

<decisions>
## Implementation Decisions

### Toast System
- Hand-rolled toast component (~70 lines) using @preact/signals — no library (no-build constraint)
- Placement: top-right, avoids blocking sidebar and bottom nav
- Auto-dismiss: 4s for success toasts, error toasts stay until manually dismissed (click X)
- Stacking: max 3 visible, newest on top, older slide out to make room
- Styles: success = green-tinted with check icon, error = red-tinted with X icon, matching existing CSS custom properties (--accent, --red, --bg-card)
- Trigger points: every place that calls `api.triggerRun()` or `api.triggerRunAll()` shows "Run queued for {target}"; if POST fails, red toast with error message
- Completion/failure toasts: wired from SSE events `run:completed` (brief-ready) and `run:failed` in app.ts

### Queue Display
- Run list: relative time with label prefix — "Queued 2m ago" for waiting runs, "Started 5m ago" for running/done runs
- Old runs without `queued_at`: show only `started_at`, no special handling needed (field is optional)
- Run detail page: shows both absolute timestamps (queued_at and started_at) with duration between them
- Target detail panel: header shows "N queued" badge when runs waiting for that target
- Per-run queue position: small pill/tag next to run status — "#1 in queue" / "#2 in queue"
- Position computed from `GET /api/worker/state` response queue array (index + 1)

### Browser Notifications
- Permission prompt: triggered on first manual run trigger (click = user gesture satisfying browser requirement)
- One-time prompt: "Enable desktop notifications?" before queueing; if denied, store `nw-notif-denied` in localStorage, never ask again
- Older Safari (pre-16.4): use callback-form `Notification.requestPermission(cb)` — document in code comments
- `document.visibilityState` check: only fire `new Notification()` when tab is hidden (backgrounded)
- Completion content: title "NW: {target} complete", body "{N} actions, {M} proposals"
- Failure content: title "NW: {target} failed", body "{error}" (truncated to 80 chars)
- Click handler: `notification.onclick = () => { window.focus(); }` to bring tab to front

### Polling + SSE Hybrid Refresh
- Extract `usePoll(fetchFn, intervalMs, shouldPoll)` hook from dashboard's existing setInterval pattern
- Both dashboard and Runs page use `usePoll` — 5s interval when active/queued runs exist, stops when all terminal
- SSE events (`run:failed`, `run:completed`/`brief-ready`) in app.ts trigger an immediate re-fetch via a shared @preact/signals signal (e.g., `refreshTrigger`)
- Polling catches state transitions (queued→running), SSE catches completions instantly (no 5s wait)
- `usePoll` watches `refreshTrigger` signal — SSE increment triggers immediate fetch outside the interval

### Claude's Discretion
- Exact toast animation (CSS transition vs simple show/hide)
- `usePoll` implementation details (useRef for timer vs signal-based)
- Whether `getWorkerState()` result is cached or fetched fresh per render
- Toast z-index layering relative to dialog/drawer

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 5 deliverables (data layer this phase wires to)
- `app/shared/types.ts` — Run interface with `queued_at?: string`, IPC message types
- `app/server/ipc.ts` — `getLastWorkerState()` export, `broadcastGlobal('run:failed', ...)` handler
- `app/server/routes/api.ts` — `GET /api/worker/state` endpoint (returns `{ queue, current, schedule }`)

### Frontend patterns (existing code to follow)
- `app/frontend/app.ts` — Global SSE connection pattern (`EventSource('/api/events')`), `brief-ready` handler
- `app/frontend/pages/dashboard.ts` lines 21-70 — Existing 5s polling pattern with `setInterval`, active run detection, cleanup on unmount
- `app/frontend/lib/api.ts` — API client pattern (`get<T>`, `post<T>` helpers), needs `getWorkerState()` added
- `app/frontend/components/target-detail.ts` — Target detail panel where queue badge goes
- `app/frontend/pages/runs.ts` — Runs page that needs `usePoll` wiring

### Requirements
- `.planning/REQUIREMENTS.md` — QUEUE-02 through QUEUE-04, NOTIF-01 through NOTIF-03, POLL-01, POLL-02

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `@preact/signals` available via vendor — toast store can use `signal<Toast[]>([])` for reactive state
- `api.ts` get/post helpers — just add `getWorkerState()` method
- CSS custom properties: `--accent`, `--red`, `--bg-card`, `--border`, `--font-mono` — toast styles should use these
- `EventSource` pattern in `app.ts` — add `run:failed` listener alongside existing `brief-ready`

### Established Patterns
- Polling: `setInterval` + `useRef` for timer + cleanup in `useEffect` return — extract to `usePoll`
- SSE: `EventSource` with typed event listeners + `useRef` for cleanup
- State management: `useState`/`useEffect` from preact/hooks, no global store except where signals used
- Component structure: each `.ts` file exports one Preact component using `html` tagged template from HTM

### Integration Points
- `app.ts` — add `run:failed` + `run:completed` SSE listeners, add toast container, add notification permission check
- `dashboard.ts` — replace inline polling with `usePoll` hook
- `runs.ts` — add `usePoll` hook for auto-refresh
- `target-detail.ts` — add queue badge and per-run position pills
- `trigger-dialog.ts` — add toast on trigger success/failure, add notification permission prompt on first use
- `lib/api.ts` — add `getWorkerState()` method

</code_context>

<specifics>
## Specific Ideas

No specific requirements beyond what's captured in decisions — straightforward wiring following existing patterns.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 06-frontend-wiring*
*Context gathered: 2026-03-20*
