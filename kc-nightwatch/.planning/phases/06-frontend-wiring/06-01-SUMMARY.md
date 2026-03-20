---
phase: 06-frontend-wiring
plan: "01"
subsystem: ui
tags: [preact, signals, toast, polling, sse, api-client]

requires:
  - phase: 05-worker-queue
    provides: "GET /api/worker/state endpoint returning { queue, current, schedule }"

provides:
  - "use-toast.ts: module-level showToast() callable from any module without prop drilling"
  - "toast.ts: Toast component with signal-backed queue, z-index:300, auto-dismiss"
  - "use-poll.ts: usePoll hook with interval start/stop and refreshTrigger signal for SSE-driven immediate re-fetch"
  - "api.ts: getWorkerState() wrapping GET /api/worker/state"

affects:
  - 06-02 (imports Toast, showToast, usePoll, refreshTrigger, api.getWorkerState)
  - 06-03 (imports usePoll, refreshTrigger)

tech-stack:
  added: []
  patterns:
    - "Module-level callback registration (registerToastHandler/showToast) — avoids prop drilling for notifications"
    - "fnRef anti-stale-closure pattern — fetchFn ref updated each render so interval always calls latest version"
    - "refreshTrigger signal — SSE consumers increment to trigger immediate fetch outside polling interval"
    - "Signal-backed component state at module scope (data only, no DOM) — safe for Preact component rendering"

key-files:
  created:
    - app/frontend/lib/use-toast.ts
    - app/frontend/components/toast.ts
    - app/frontend/lib/use-poll.ts
  modified:
    - app/frontend/lib/api.ts

key-decisions:
  - "Toast z-index:300 to appear above TriggerDialog overlay (z-index:100) — 'Run queued' toast fires while dialog is still visible"
  - "Error toasts no auto-dismiss (stay until manually closed); success toasts auto-dismiss at 4s"
  - "refreshTrigger initial value 0 — useEffect skips initial render by checking value > 0 before calling fnRef.current()"
  - "fnRef pattern instead of fetchFn in useEffect deps — prevents timer restart on every fetchFn identity change"

patterns-established:
  - "Module-level handler registration: registerToastHandler() called in useEffect, cleaned up on unmount"
  - "No module-scope DOM manipulation: signal() at module scope is data only; DOM rendering inside component tree"

requirements-completed: [NOTIF-01, POLL-02]

duration: 3min
completed: 2026-03-20
---

# Phase 06 Plan 01: Frontend Infrastructure (Toast + Poll + API) Summary

**Signal-backed toast notification system and polling hook with SSE-driven immediate re-fetch, enabling showToast() from any module and usePoll() with refreshTrigger for interval + event-triggered fetches**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-20T09:34:10Z
- **Completed:** 2026-03-20T09:37:03Z
- **Tasks:** 2
- **Files modified:** 4 (3 created, 1 modified)

## Accomplishments
- Created module-level toast system: `registerToastHandler` + `showToast` callable without prop drilling from any module
- Toast component renders at z-index:300 (above TriggerDialog z-index:100) with signal-backed queue, max 3 visible, success auto-dismiss 4s, error manual-close
- Created `usePoll` hook: manages interval start/stop with `shouldPoll` boolean + watches `refreshTrigger` signal for SSE-driven immediate re-fetch; fnRef pattern prevents stale closures
- Added `api.getWorkerState()` to api client wrapping `GET /api/worker/state`

## Task Commits

Each task was committed atomically:

1. **Task 1: Create toast system (use-toast.ts + toast.ts)** - `a9b7201` (feat)
2. **Task 2: Create usePoll hook with refreshTrigger signal and add getWorkerState to API client** - `cc543d8` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified
- `app/frontend/lib/use-toast.ts` — ToastType, ToastItem, registerToastHandler, showToast exports
- `app/frontend/components/toast.ts` — Toast component with signal-backed queue, z-index:300, auto-dismiss
- `app/frontend/lib/use-poll.ts` — usePoll hook, refreshTrigger signal (signal(0))
- `app/frontend/lib/api.ts` — getWorkerState() method added after getHealth

## Decisions Made
- Toast z-index:300 (plan specified explicitly) to ensure "Run queued" toast appears above TriggerDialog overlay (z-index:100)
- refreshTrigger initial value is 0; useEffect skips the initial render by checking `value > 0` before calling fetch — prevents spurious fetch on mount
- fnRef pattern: fetchFn ref updated every render, not in useEffect deps — avoids interval restart on every closure change

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All 3 shared infrastructure modules are ready for Plan 02 (app root + dashboard + queue display) and Plan 03 (runs page polling)
- Plan 02 imports: `Toast` (mount at root), `showToast` (trigger from handleTrigger), `usePoll` (dashboard polling), `refreshTrigger` (SSE increment), `api.getWorkerState` (queue data)
- Plan 03 imports: `usePoll`, `refreshTrigger` (runs page polling with SSE-driven refresh)

---
*Phase: 06-frontend-wiring*
*Completed: 2026-03-20*
