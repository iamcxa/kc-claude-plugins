# Project Research Summary

**Project:** Nightwatch Dashboard v1.1 — UX Polish
**Domain:** Bun-native web dashboard (Preact + HTM + Hono + Bun worker + IPC)
**Researched:** 2026-03-20
**Confidence:** HIGH

## Executive Summary

The Nightwatch Dashboard v1.1 is a targeted UX polish pass on a complete v1.0 cockpit. The system is a no-bundler Preact/HTM frontend served by Hono on Bun, communicating with a Bun background worker via native IPC, with SSE for real-time log streaming and HTTP polling for run state. The v1.1 scope addresses five gaps identified during use: the trigger action produces no feedback, the Runs page goes stale after a trigger, queue depth is invisible, the target detail panel has dead UI elements, and long-running completions are invisible when the tab is backgrounded. All five are addressable with the existing stack — no new npm packages are required.

The recommended approach is a sequential 4-phase build that respects data dependencies: schema first (`queued_at` field), then server infrastructure (queue endpoint + IPC state capture), then frontend wiring (toast + notification + polling + queue display), then cleanup (dead code removal). This order avoids the two worst failure modes: frontend code consuming a schema field that does not exist yet, and dead code removal that leaves dangling imports. The single highest-risk implementation decision is the toast rendering strategy — if the toast queue is created as a DOM side effect at module scope rather than inside the Preact tree via a signal, it silently breaks on page load with no error in the console.

The architecture patterns established in v1.0 (SSE for lifecycle events, HTTP polling for frequent state, module-level callbacks for cross-cutting concerns) are the correct model for all v1.1 additions. Specifically: browser notifications must be gated on a user gesture (not on-mount), Runs page polling must be conditional on active runs (not unconditional), and queue state must surface via a new REST endpoint rather than SSE broadcasts (which would pollute the lifecycle event channel). All three deviations are documented in PITFALLS.md as critical anti-patterns that produce silent failures — the kind that pass happy-path testing but break immediately in real use.

## Key Findings

### Recommended Stack

No new npm packages are needed for v1.1. All features are implementable with the existing Bun + Hono + Preact/HTM + @preact/signals stack. The existing codebase provides a reference implementation for every pattern needed: the Dashboard's `pollTimerRef + setInterval(5000)` pattern is the exact model for Runs page polling; the Dashboard's `handleTrigger` click handler is the correct user-gesture context for `Notification.requestPermission()`; the `@preact/signals` import map is already wired and ready for a toast signal.

**Core technologies (unchanged from v1.0):**
- **Bun 1.2.x**: Runtime, test runner, TypeScript-native — no new config needed
- **Hono 4.12.x**: HTTP server — add one `GET /api/worker/state` endpoint
- **Preact + HTM**: Frontend UI — add two new files (toast hook + toast component)
- **@preact/signals**: State management — use for toast queue (already in importmap)
- **yaml + zod**: YAML persistence + schema validation — `queued_at` is optional, no migration needed

**v1.1 additions (zero new packages):**
- Custom `useToast` hook (~70 lines): module-level callback pattern, no prop drilling, no CDN dependency
- Raw `Notification` Web API: desktop-only, localhost = secure context by spec, no HTTPS needed
- `useInterval` custom hook: extracted from existing Dashboard polling logic

### Expected Features

**Must have (table stakes — ship in v1.1):**
- `queued_at` timestamp on Run type — schema change that unlocks two other features; do this first
- Toast notification component — success/error variants, auto-dismiss, `position:fixed` top-right
- Toast on run trigger success/error — immediate acknowledgement after `api.triggerRun()` resolves or rejects
- Runs page auto-refresh — mirror Dashboard's polling pattern; poll when active runs exist, stop when idle
- Queue depth display in TargetDetail — count + list of queued runs for selected target
- Stale UI cleanup — remove dead "Edit"/"Chat" menu items and `chat-drawer.ts` orphan file
- Sidebar "Add Target" button wiring — open existing `AddTargetWizard` on click (already exists)

**Should have (add if time allows):**
- Browser Notification API on completion — requires explicit user opt-in gesture; fallback to toast if permission denied
- Trigger time in run list — show `queued_at` relative time alongside `started_at`

**Defer to v2+:**
- Notification center / bell icon — no value for single-user local tool
- Service Worker push — wrong complexity/value ratio for localhost-only dashboard
- WebSocket for run status — SSE + 5s polling is already sufficient at this scale

### Architecture Approach

The system has a clean 3-tier architecture (Preact frontend → Hono server → Bun worker) with IPC as the worker-to-server channel and SSE as the server-to-browser channel for lifecycle events. All v1.1 changes are additive: two new files, twelve modified files, one file deletion. The architecture research provides a precise 10-step build order and a file change matrix covering 14 files. The key architectural decision is surfacing worker queue state via a new polling endpoint (`GET /api/worker/state`) rather than global SSE, preserving the invariant that the global SSE channel carries only infrequent lifecycle events.

**Major components affected by v1.1:**
1. `shared/types.ts` — adds `queued_at?: string` to Run interface (backward-compatible)
2. `server/ipc.ts` + `server/routes/api.ts` — captures `lastWorkerState` from IPC; exposes via `GET /api/worker/state`
3. `frontend/lib/use-toast.ts` + `frontend/components/toast.ts` — new module-level signal-backed toast system
4. `frontend/app.ts` — mounts Toast; adds Notification permission request + fires on `brief-ready`
5. `frontend/pages/dashboard.ts` — showToast on trigger; AddTargetWizard wiring; queue fetch; pass queue to TargetDetail
6. `frontend/pages/runs.ts` — adds conditional polling pattern identical to Dashboard
7. `frontend/components/target-detail.ts` + `sidebar.ts` — queue display, dead button removal, Add Target wiring
8. `worker/index.ts` + `worker/scheduler.ts` — set `queued_at` at enqueue time on all code paths

### Critical Pitfalls

1. **Toast DOM side effect at module scope** — Do not create toast DOM elements at module scope. Render `<ToastContainer />` inside the Preact tree. Use a `signal<Toast[]>([])` at module scope (data, not DOM). Symptom of failure: "Cannot read properties of null" on page load.

2. **Toast z-index below TriggerDialog overlay** — TriggerDialog uses `z-index:100`. Toast must use `z-index:300`. "Run queued" toast fires while the dialog is still visible — invisible toast is the failure mode. Establish CSS variables (`--z-toast: 300`) to document the layer hierarchy.

3. **Browser Notification permission requested on page load** — Chrome 84+, Firefox 72+, Safari 16.4+ silently deny `Notification.requestPermission()` not tied to a user gesture. Symptom: promise resolves `"denied"` immediately, no dialog appears, no error in console.

4. **Polling interval leak on Runs page unmount** — `setInterval` not cleared in `useEffect` cleanup accumulates N intervals after N page navigations. Follow Dashboard's exact pattern: `pollTimerRef.current` guard + `clearInterval` in unmount cleanup.

5. **`queued_at` missing from all 4 enqueue paths** — Paths: `POST /api/runs`, `POST /api/webhook`, `worker/index.ts` `__all__` expansion, `worker/scheduler.ts` interval trigger. Missing any one produces runs with `—` in queue display even though freshly queued.

## Implications for Roadmap

Based on research, the dependency order is clear and maps directly to 4 phases. Each phase builds on the previous one's deliverables.

### Phase 1: Schema + Toast Infrastructure

**Rationale:** Two prerequisites that unlock everything else. The `queued_at` schema must exist before any display code can reference it. Toast infrastructure must be built with the correct pattern (signal + component, not module-scope DOM) before any caller can use it. Both are zero-dependency additions with no external consumers yet.

**Delivers:** `shared/types.ts` with `queued_at`; all 4 enqueue paths setting it; `use-toast.ts` + `toast.ts` new files; `app.ts` mounting Toast; z-index 300 CSS variable established

**Addresses:** FEATURES.md P1 items: `queued_at` field, Toast component

**Avoids:** Pitfall 1 (toast DOM side effect), Pitfall 2 (z-index below dialog), Pitfall 5 (`queued_at` missing from scheduler/webhook paths)

### Phase 2: Server Layer + Notification Wiring

**Rationale:** The server-side queue endpoint must exist before the frontend can display queue depth. Browser notification wiring extends the existing `brief-ready` SSE handler in `app.ts` — it belongs here because it is a server behavior change (`run-failed` global broadcast) plus a `app.ts` change (fire Notification in `brief-ready` handler). The user-gesture gating must be wired from day one.

**Delivers:** `server/ipc.ts` storing `lastWorkerState`; `GET /api/worker/state` endpoint; `run-failed` global SSE broadcast; notification permission flow wired to user gesture in `app.ts`

**Uses:** STACK.md patterns: HTTP polling for frequent state (not SSE), raw Notification API (no Service Worker)

**Avoids:** Pitfall 3 (permission on page load), ARCHITECTURE.md Anti-pattern 1 (queue state over SSE)

### Phase 3: Frontend Wiring

**Rationale:** All backend dependencies now exist (schema, endpoints, SSE events). Wire the full frontend: toast on trigger, Runs page polling, queue display in TargetDetail, Add Target button, API client update. The Dashboard is the reference implementation for every pattern here — no new patterns are introduced.

**Delivers:** `api.ts` `getWorkerState()`; `dashboard.ts` toast calls + AddTargetWizard + queue fetch; `runs.ts` conditional polling; `target-detail.ts` queue prop + display; `sidebar.ts` Add Target wiring

**Implements:** All P1 FEATURES.md items except cleanup

**Avoids:** Pitfall 4 (unconditional polling), ARCHITECTURE.md Anti-pattern 3 (prop-drilling toast), Anti-pattern 4 (navigating to Config for Add Target)

### Phase 4: Stale UI Cleanup

**Rationale:** Delete last. Verify no imports exist before removing any file. Run `bun typecheck` after each deletion. Removing dead code after all new code is wired ensures there are no unexpected references from new code to deleted files. The Edit button situation (currently disabled, but AddTargetWizard already supports edit mode) is a decision point: wire it as working or remove it — both are valid.

**Delivers:** `chat-drawer.ts` deleted (confirmed orphan); disabled Edit/Chat buttons removed from `target-detail.ts`; dead `phases` variable removed; `bun typecheck` exits 0

**Avoids:** PITFALLS.md Pitfall 9 (removing buttons without reading full container context), Pitfall 5 (dangling imports post-deletion)

### Phase Ordering Rationale

- Schema before server: TypeScript types must exist when writing the server-side `POST /api/runs` changes
- Server before frontend: `GET /api/worker/state` endpoint must exist before `api.ts` can wrap it
- Toast infrastructure before notification wiring: fallback path (toast when permission denied) must already work when the Notification path is added
- Cleanup last: prevents new code from accidentally referencing files about to be deleted

### Research Flags

All phases have standard, well-documented patterns. No additional `/gsd:research-phase` is needed.

- **Phase 1:** `queued_at` schema + toast signal — exact implementation specified in ARCHITECTURE.md with line-level file references
- **Phase 2:** Server queue endpoint + notification — trivial route addition; notification pattern verified against MDN spec
- **Phase 3:** Frontend wiring — `dashboard.ts` reference implementation is the model for every pattern
- **Phase 4:** Dead code removal — verification steps fully specified (grep + typecheck checklist in PITFALLS.md)

One optional decision to surface during Phase 4 planning: wire the Edit button (AddTargetWizard already supports it) vs. just removing it. Either direction is low-effort — document the choice.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All v1.1 features confirmed implementable with existing stack; no new packages; verified via MDN, Bun docs, Preact docs, and direct codebase inspection |
| Features | HIGH | Derived from direct codebase analysis + PROJECT.md v1.1 requirements list; clear P1/P2 distinction with dependency graph |
| Architecture | HIGH | Based on direct inspection of all 14 affected files with line-level specificity; file change matrix + 10-step build order provided |
| Pitfalls | HIGH | Mix of project-specific pitfalls (from MEMORY.md + codebase inspection) and verified browser spec behavior (MDN); all 9 pitfalls include warning signs and recovery strategies |

**Overall confidence:** HIGH

### Gaps to Address

- **Browser Notification on older Safari**: Research confirms Promise-based `requestPermission()` works on Safari 16.4+. For older Safari, use callback form. Not a blocker — document as implementation note in Phase 2.
- **`document.visibilityState` gating**: Research recommends only firing `new Notification()` when tab is hidden. Easy to forget — add to Phase 2 acceptance checklist explicitly.
- **Edit button decision**: `target-detail.ts` has a disabled Edit button. `AddTargetWizard` supports edit mode via `editTarget` prop. The roadmap should decide: wire it (free improvement at the same touch point) or remove it (cleaner cleanup). Either is valid — needs a decision, not more research.

## Sources

### Primary (HIGH confidence)
- Direct codebase inspection (2026-03-20): `app/shared/types.ts`, `app/server/ipc.ts`, `app/server/routes/api.ts`, `app/worker/index.ts`, `app/worker/scheduler.ts`, `app/frontend/app.ts`, `app/frontend/pages/dashboard.ts`, `app/frontend/pages/runs.ts`, `app/frontend/components/sidebar.ts`, `app/frontend/components/target-detail.ts`, `app/frontend/components/chat-drawer.ts`, `app/frontend/lib/api.ts`, `app/frontend/index.html`
- `.planning/PROJECT.md` — v1.1 requirements list (authoritative)
- MDN Web Docs — Notifications API, requestPermission(), secure context definition, Page Visibility API
- Chrome Lighthouse — notification-on-start best practice (do not request on page load)
- Bun official docs — spawn, IPC, YAML, 1.2 release notes
- Hono official docs — Bun getting started, SSE streaming
- Preact no-build workflows guide — HTM + import maps, custom hooks

### Secondary (MEDIUM confidence)
- LogRocket — Toast Notifications Best Practices (auto-dismiss timing, error persistence norms)
- Smashing Magazine — UX Strategies for Real-Time Dashboards (polling vs push tradeoffs)
- overreacted.io — Making setInterval Declarative with React Hooks (useInterval canonical pattern, applies identically to Preact)
- Carbon Design System — Notification Pattern (toast positioning, stacking behavior)

---
*Research completed: 2026-03-20*
*Ready for roadmap: yes*
