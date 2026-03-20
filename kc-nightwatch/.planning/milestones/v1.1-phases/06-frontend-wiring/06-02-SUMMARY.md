---
phase: 06-frontend-wiring
plan: "02"
subsystem: ui
tags: [preact, toast, notifications, polling, sse, queue, sidebar]

requires:
  - phase: 06-01
    provides: "Toast/showToast, usePoll/refreshTrigger, api.getWorkerState"

provides:
  - "app.ts: Toast mounted at root, SSE run:failed + brief-ready fire showToast + browser Notification + refreshTrigger++"
  - "dashboard.ts: usePoll replacing inline pollTimerRef/setInterval (POLL-02 complete), queue data fetched, AddTargetWizard wired"
  - "target-detail.ts: workerQueue prop, queued count + position pills display"
  - "sidebar.ts: onAddTarget prop wired to both Add Target buttons"

affects:
  - 06-03 (runs page polling — also consumes usePoll/refreshTrigger)

tech-stack:
  added: []
  patterns:
    - "Fragment wrapper (<></>) in htm/preact for sibling root elements (Toast + main layout)"
    - "usePoll(loadRuns, 5_000, hasActiveRuns) — shouldPoll driven by hasActiveRuns state"
    - "Notification.requestPermission() on user gesture (triggerRun), never on page load"
    - "visibilityState === 'hidden' guard before firing browser Notification"
    - "nw-notif-denied localStorage key to skip re-prompting after denial"

key-files:
  modified:
    - app/frontend/app.ts
    - app/frontend/pages/dashboard.ts
    - app/frontend/components/target-detail.ts
    - app/frontend/components/sidebar.ts

key-decisions:
  - "Fragment wrapper required in htm to render Toast as sibling to main layout div without extra DOM wrapper"
  - "Notification.requestPermission() called in handleTrigger (not useEffect) — user gesture requirement for modern browsers"
  - "nw-notif-denied localStorage key prevents re-prompt when user explicitly denied"
  - "Dead phases variable removed alongside phases.length > 0 usage — RunTimeline was never rendering anyway"
  - "Disabled Edit/Chat buttons left untouched per user decision (v1.1 out of scope)"

requirements-completed: [NOTIF-02, NOTIF-03, QUEUE-03, QUEUE-04, POLL-02]

duration: 8min
completed: 2026-03-20
---

# Phase 06 Plan 02: Frontend Integration (Toast + Notifications + Queue + Polling) Summary

**Full integration of Plan 01 infrastructure: Toast mounted at app root, SSE events fire toasts and browser Notifications, refreshTrigger incremented on run events, dashboard replaces inline polling with usePoll, queue data flows to TargetDetail, and Sidebar Add Target buttons open AddTargetWizard**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-03-20T09:41:51Z
- **Completed:** 2026-03-20T09:49:45Z
- **Tasks:** 3
- **Files modified:** 4 (all modified, none created)

## Accomplishments

- Mounted `<Toast />` component at app root using Preact fragment wrapper (sibling to main layout div)
- Wired SSE `brief-ready` listener: `showToast` success, `refreshTrigger.value++`, browser `Notification` with `visibilityState === 'hidden'` + `Notification.permission === 'granted'` guards, `n.onclick = window.focus()`
- Added SSE `run:failed` listener: `showToast` error, `refreshTrigger.value++`, browser `Notification` with same guards
- Notification permission NOTE comment in app.ts — actual `requestPermission()` is in dashboard.ts on user gesture
- Dashboard: replaced `pollTimerRef`/`setInterval` with `usePoll(loadRuns, 5_000, hasActiveRuns)` (POLL-02 satisfied)
- Dashboard `loadRuns()` now also calls `api.getWorkerState()` and sets `workerQueue` state
- `handleTrigger`: added `Notification.requestPermission()` on first trigger with `nw-notif-denied` localStorage guard
- `handleTrigger`: `showToast('Run queued for {target}', 'success')` on success; `showToast(err.message, 'error')` on failure
- Passed `workerQueue` prop to `TargetDetail` and `onAddTarget` prop to `Sidebar`
- Mounted `<AddTargetWizard>` with `isOpen/onClose/onSaved` wiring
- `TargetDetail`: added `workerQueue?: Run[]` prop, queue display section with count badge and position pills
- `TargetDetail`: added `timeAgo()` helper function; removed dead `phases` variable and unused `RunTimeline` call
- `Sidebar`: added `onAddTarget: () => void` prop; both Add Target buttons now call `onAddTarget` (not `() => {}`)

## Task Commits

Each task was committed atomically:

1. **Task 1: Wire app.ts with Toast mount, SSE listeners, refreshTrigger, browser notifications** - `815c25f` (feat)
2. **Task 2: Wire dashboard with usePoll, toast, queue state, AddTargetWizard, notification permission** - `b696548` (feat)
3. **Task 3: Wire target-detail queue display and sidebar Add Target button** - `e84382a` (feat)

## Files Created/Modified

- `app/frontend/app.ts` — Toast import + mount, showToast import, refreshTrigger import, run:failed listener, brief-ready listener enhanced, browser Notification with visibilityState guard
- `app/frontend/pages/dashboard.ts` — usePoll replacing pollTimerRef/setInterval, workerQueue state, showAddWizard state, handleTrigger with toast + notification permission, AddTargetWizard mount, workerQueue/onAddTarget props passed
- `app/frontend/components/target-detail.ts` — workerQueue prop, timeAgo() function, queue display section, dead phases variable removed
- `app/frontend/components/sidebar.ts` — onAddTarget prop in interface + destructuring, both buttons wired to onAddTarget

## Decisions Made

- Fragment wrapper (`<></>`) required in htm template to render `<Toast />` as sibling to the main layout `<div>` — htm doesn't support adjacent top-level elements without a fragment
- `Notification.requestPermission()` placed in `handleTrigger` (user gesture context), not in any `useEffect` — Chrome 84+, Firefox 72+, Safari 16.4+ silently deny page-load requests
- `nw-notif-denied` localStorage key prevents annoying re-prompt when user explicitly denied permission
- Dead `phases` variable removed: `const phases = lastRun?.log_path ? [] : []` was always `[]`, so `phases.length > 0` conditional always evaluated to false — `RunTimeline` was never rendering

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 03 (Runs page polling): imports `usePoll` and `refreshTrigger` — both infrastructure items are ready
- All NOTIF-02, NOTIF-03, QUEUE-03, QUEUE-04, POLL-02 requirements are now complete

---
*Phase: 06-frontend-wiring*
*Completed: 2026-03-20*
