# Feature Research

**Domain:** Dashboard UX Polish — v1.1 Nightwatch Dashboard
**Researched:** 2026-03-20
**Confidence:** HIGH (codebase read + confirmed UX patterns via web research)

---

## Context

This is a focused v1.1 research pass. v1.0 built the full cockpit (P1/P2 features). v1.1 addresses run lifecycle feedback gaps and stale UI debt identified during use:

- The user triggers a run, sees nothing until the page auto-navigates (no acknowledgement)
- Runs page goes stale after trigger until manually refreshed
- Target detail shows dead "Edit" and "Chat" menu items (vestigial from an earlier design)
- Queue depth (how many runs are waiting) is invisible
- Long runs complete while the tab is backgrounded, with no notification

The existing codebase uses Preact + HTM (no build step), Hono server, Bun worker with IPC. All new features must fit this stack — no new frameworks, no new build tools.

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features that dashboard users assume exist. Missing them degrades trust.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Toast on trigger action | Every modern UI confirms "Run queued" immediately — silence feels like the click didn't register | LOW | 1-2 line message, auto-dismisses in 3-4s. No external library needed; a single Preact component with `position:fixed` + CSS fade |
| Toast on trigger error | If worker is offline or API returns 503, users need to know; silent failure is worse than an error message | LOW | Same toast component; error variant (red color); no auto-dismiss |
| Runs page auto-refresh while active runs exist | Dashboard page already polls every 5s when active — the runs page should behave identically | LOW | Mirror the `hasActiveRun` + `setInterval(5000)` pattern from `dashboard.ts`. No new architecture |
| Queue depth display in target detail | "Queued" status badge exists but count of pending runs is invisible | LOW | Read `runs` where `status === 'queued'` from `/api/runs`; show "2 queued" label near Run button |
| `queued_at` timestamp on Run type | Users want to know how long a run waited before starting | LOW | Add optional `queued_at: string` field to `Run` interface in `types.ts`; set in `POST /api/runs` |
| Remove dead "Edit" + "Chat" buttons | Target detail's overflow menu shows disabled "Edit" and "Chat" items — confusing, implies broken features | LOW | Delete those two `aria-disabled` menu items from `target-detail.ts`. v1.0 had them as "Coming in Phase 3" placeholders; they were never wired |
| Sidebar "Add target" wiring | Sidebar has an "Add" button; it does nothing — appears broken | LOW | Open the AddTargetWizard on click. Component already exists in `add-target-wizard.ts` |

### Differentiators (Worth Doing Well)

Features where implementation quality matters beyond just shipping them.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Browser Notification API on run completion | When a 30-minute run finishes while the tab is backgrounded, no amount of in-page toasts help. A system-level notification is the only way to reclaim the user's attention. | MEDIUM | Requires permission request (user gesture), `Notification` constructor, fallback to toast if permission denied. See pattern notes below. |
| Queue display in target detail panel | Surface the full queue (all queued runs for this target) not just a count — show run IDs, modes, `queued_at` timestamp. "You have 2 runs queued: dry-run (2 min ago) + production (1 min ago)" | MEDIUM | Read from existing `/api/runs?target=X&status=queued`. Wire into `TargetDetail` component. Requires `queued_at` field first. |
| Trigger time display in run list | Show `queued_at` alongside `started_at` to expose wait time — "queued 14 min ago, started 2 min ago" — tells users whether the worker is saturated | LOW | Cosmetic addition once `queued_at` field exists on `Run` |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Service Worker for background notifications | "More reliable than tab-open Notification API" | Service Worker installation adds a build step assumption and adds complexity for a local-only tool running on localhost. The Notification API works fine when the tab is open. | Plain `Notification` constructor; document that the tab must be open for completion notifications |
| WebSocket for real-time run status push | "Polling is outdated" | The dashboard already has SSE for log streaming (the actual real-time need). Run status updates are infrequent (every few minutes); polling at 5s intervals is invisible to the user and trivially cheap on localhost. | Keep 5s polling for run list refresh; SSE already handles the high-frequency log case |
| Toast library (react-hot-toast, sonner, etc.) | "More features, better animations" | Adding a JS dependency for toasts in a zero-build-step Preact+HTM app means either a CDN script tag or a build tool. Neither is worth it for 4 toast variants. | Inline Preact component: 50-80 lines, full control, no CDN risk |
| Persistent notification center / bell icon | "GitHub has one, so should this" | The user is the only user of this tool. A notification center that stores history adds state management complexity with zero benefit for a single-user local tool. | Toast auto-dismiss is sufficient; completed runs are visible in the runs list |
| Auto-refresh countdown indicator | "Shows me when data refreshes" | Polling at 5s is already invisible. Showing a countdown adds visual noise to a developer tool and shifts focus from the actual run state. | Show "last updated Xs ago" only if data freshness becomes a concern |
| Aggressive browser notification permission request on page load | "Get it out of the way" | Browsers block permission dialogs not triggered by user gesture. More importantly, requesting permission before the user understands what notifications are about causes denials that are hard to reverse. | Gate the permission request behind a "Notify me when runs complete" button in settings or target detail. Only ask when the user explicitly opts in. |

---

## Feature Dependencies

```
[Browser Notification on completion]
    └──requires──> [user has granted permission] (gated by user opt-in gesture)
    └──falls back to──> [Toast on completion] (if permission denied)
    └──requires──> [completion event detection] (already exists via run status polling or SSE)

[Queue display in target detail]
    └──requires──> [queued_at field on Run] (new field, must be set at enqueue time)
    └──requires──> [GET /api/runs?target=X&status=queued] (already exists, just needs to be called)
    └──enhances──> [trigger time display in run list] (both use queued_at)

[Runs page auto-refresh]
    └──requires──> [same poll pattern as dashboard.ts] (copy/adapt existing implementation)
    └──independent of all other v1.1 features]

[Toast notification system]
    └──independent──> (no dependencies)
    └──required by──> [Browser Notification fallback] (toast is shown when Notification permission denied)
    └──required by──> [trigger error feedback] (worker offline, 503 errors)

[Stale UI cleanup]
    └──independent──> (pure deletion — remove dead code, no new dependencies)
    └──required before──> [Sidebar add button wiring] (add-target-wizard.ts already exists)
```

### Dependency Notes

- **queued_at must be added to Run type first**: Queue display and trigger time features both depend on it. It is the one schema change in v1.1. Set it in `POST /api/runs` alongside `status: 'queued'`. It is an optional field (`queued_at?: string`) — no migration needed for existing runs.
- **Toast must be built before browser notification**: The notification fallback path shows a toast. Build toast first, wire browser notification second.
- **Stale UI cleanup is zero-dependency**: Remove dead code first. It makes the subsequent additions easier to reason about (no dead branches to confuse).
- **Runs page auto-refresh is independent**: Can be done in any order. Mirrors existing dashboard pattern exactly.

---

## MVP Definition (v1.1 scope)

### Ship in v1.1

All seven items are low-medium complexity and constitute the full v1.1 scope.

- [ ] `queued_at` timestamp — schema change that unlocks two other features; do this first
- [ ] Toast notification component — success / error variants, auto-dismiss, position:fixed top-right
- [ ] Toast on run trigger — call toast after `api.triggerRun()` resolves (success) or rejects (error)
- [ ] Runs page auto-refresh — mirror dashboard polling; start poll when active runs detected, stop when idle
- [ ] Queue display in target detail — count + list of queued runs for the selected target
- [ ] Stale UI cleanup — remove "Edit" + "Chat" dead menu items; remove chat-drawer dead file
- [ ] Sidebar add target button wiring — open AddTargetWizard on click

### Add If Convenient

- [ ] Browser Notification API on completion — requires explicit user opt-in gesture; add a "Notify me" toggle in settings or target detail area; fallback to toast if denied
- [ ] Trigger time in run list — show `queued_at` relative time alongside `started_at` in the runs list row

### Defer to v2

- [ ] Notification center / bell icon — no value for single-user local tool
- [ ] Service Worker push — wrong complexity/value ratio for localhost-only app

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| `queued_at` field | MEDIUM (unlocks other features) | LOW | P1 |
| Toast component | HIGH (immediate trigger feedback) | LOW | P1 |
| Toast on trigger | HIGH | LOW | P1 |
| Runs page auto-refresh | HIGH (removes surprising staleness) | LOW | P1 |
| Stale UI cleanup | MEDIUM (reduces confusion) | LOW | P1 |
| Sidebar add button wiring | MEDIUM | LOW | P1 |
| Queue display in target detail | MEDIUM | LOW–MEDIUM | P1 |
| Browser Notification API | HIGH (long-run completion) | MEDIUM | P2 |
| Trigger time in run list | LOW | LOW | P2 |

**Priority key:**
- P1: Must ship in v1.1 — all are low cost, high value
- P2: Ship in v1.1 if time allows, otherwise v1.2

---

## Implementation Pattern Notes

### Toast Component

Pattern: single `Toast` component in `frontend/components/toast.ts`, rendered at root level in `app.ts`. Uses a `useToast()` context hook (or simple module-level array + Preact signal). Each toast has: `type` (success|error|info|warn), `message`, `duration` (default 3500ms, 0 = no auto-dismiss).

Key behaviors:
- **Success** (run queued): auto-dismiss after 3.5s
- **Error** (worker offline, 503): no auto-dismiss — user must close
- Stack multiple toasts vertically (rare but possible if user spam-triggers)
- Position: top-right, fixed, z-index above dialog (existing dialog is z-index:100 → use 200)

No external library. ~70 lines of Preact + CSS.

### Browser Notification API

Pattern: permission is `denied | granted | default`. Only request permission in response to explicit user gesture (a "Notify me when runs complete" toggle). Never request on page load.

Flow:
1. User clicks "Notify me" toggle in target detail or settings
2. If `Notification.permission === 'granted'` → enable immediately
3. If `Notification.permission === 'default'` → call `Notification.requestPermission()` → enable if granted
4. If `Notification.permission === 'denied'` → show message explaining how to re-enable in browser settings
5. Store preference in `localStorage` so the toggle state persists

On run completion detected (via polling): `new Notification('Nightwatch run completed', { body: 'target-name: completed in Xm Ys', icon: '/favicon.ico' })`

Fallback: if permission is not granted, show toast instead. This ensures completion feedback exists regardless of notification state.

### Runs Page Auto-Refresh

Copy the `hasActiveRun` + `pollTimerRef` + `setInterval(5000)` pattern verbatim from `dashboard.ts`. The runs page already fetches `api.getRuns()` on mount. Add:

1. After `setRuns(runs)`, compute `hasActive = runs.some(r => r.status === 'running' || r.status === 'queued')`
2. If `hasActive && !pollTimerRef.current` → start 5s interval calling `loadRuns()`
3. If `!hasActive && pollTimerRef.current` → clear interval
4. Clean up on unmount

### Queue Display in Target Detail

Call `api.getRuns({ target: target.name, status: 'queued' })` in the `TargetDetail` component (or pass queued runs as a prop from parent). Show a "Queue" section below the "Last run" section: list each queued run with its mode, `queued_at` relative time, and run ID (truncated). If queue is empty, hide the section entirely.

---

## Sources

- Codebase analysis: `app/frontend/pages/dashboard.ts`, `app/frontend/components/target-detail.ts`, `app/frontend/pages/runs.ts`, `app/server/routes/api.ts`, `app/shared/types.ts` — HIGH confidence
- PROJECT.md v1.1 requirements: `.planning/PROJECT.md` — HIGH confidence (authoritative)
- Toast UX patterns: [LogRocket — Toast Notifications Best Practices](https://blog.logrocket.com/ux-design/toast-notifications/), [Carbon Design System — Notification Pattern](https://carbondesignsystem.com/patterns/notification-pattern/) — MEDIUM confidence
- Browser Notification API: [MDN — Using the Notifications API](https://developer.mozilla.org/en-US/docs/Web/API/Notifications_API/Using_the_Notifications_API), [web.dev — Permission UX](https://web.dev/articles/push-notifications-permissions-ux) — HIGH confidence (MDN is authoritative)
- Dashboard auto-refresh patterns: [Smashing Magazine — UX Strategies for Real-Time Dashboards](https://www.smashingmagazine.com/2025/09/ux-strategies-real-time-dashboards/), [InfluxData UI auto-refresh issue](https://github.com/influxdata/ui/issues/1413) — MEDIUM confidence

---

*Feature research for: Nightwatch Dashboard v1.1 — UX Polish*
*Researched: 2026-03-20*
