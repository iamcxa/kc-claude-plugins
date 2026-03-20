# Pitfalls Research

**Domain:** Adding toast/notification/polling/backward-compat features to existing Bun + Hono + Preact/HTM no-bundler dashboard
**Researched:** 2026-03-20
**Confidence:** HIGH (based on direct codebase inspection + known project-specific pitfalls)

> Note: This file covers v1.1 Dashboard UX Polish pitfalls. For v1.0 infrastructure pitfalls (Claude CLI hang, socket cleanup, SSE memory leaks, IPC heartbeat, YAML concurrent writes), see the original research at commit history.

---

## Critical Pitfalls

### Pitfall 1: Toast component imported into app.ts as side effect — triggers before Preact renders

**What goes wrong:**
A toast manager created at module scope in a new `toast.ts` file (e.g., `const toastQueue = signal([])`) gets evaluated when `app.ts` imports it. If the DOM `#app` div is not yet mounted or `render()` has not been called, the first toast that fires during app boot (e.g., on startup error) targets a non-existent element. In Preact/HTM without a bundler, module-level code executes immediately on import — there is no deferred initialization pass.

**Why it happens:**
No-bundler setups rely on browser ES module evaluation order. `app.ts` is the entry point and calls `render()` at its last line. Any module imported by `app.ts` runs its top-level code before `render()` is called. A toast component that tries to attach a portal to `document.body` at module scope finds the DOM in a partially initialized state.

**How to avoid:**
- Do NOT create toast DOM elements at module scope. Render the `<ToastContainer />` component inside the `App()` function's return value — it lives in the Preact tree alongside everything else.
- Use a Preact signal (`signal<Toast[]>([])`) as the toast queue. The signal lives at module scope (fine — it holds data, not DOM), but the component rendering it is tree-mounted.
- Expose a `showToast(msg, type)` function that mutates the signal. Callers import this function; they never touch the DOM directly.
- The `<ToastContainer />` component reads the signal and renders positioned toasts using `position:fixed` inline styles (no CSS classes needed — matches existing project style).

**Warning signs:**
- Browser console shows "Cannot read properties of null (reading 'appendChild')" on page load
- Toast appears for a fraction of a second then disappears — signal updated before component mounts, then Preact re-renders correctly but initial paint is missed
- Toast container renders twice (once from side effect, once from Preact tree)

**Phase to address:** Phase 1 (Toast infrastructure). Establish the signal + component pattern before wiring any callers.

---

### Pitfall 2: Browser Notification permission requested before user gesture — request silently denied

**What goes wrong:**
`Notification.requestPermission()` is called inside a `useEffect` in the App component (e.g., on mount) rather than in response to a direct user click. Modern browsers (Chrome 84+, Firefox 72+, Safari 16.4+) silently deny permission requests not tied to a user activation event. The promise resolves with `"denied"` immediately. When the run completes and `new Notification(...)` is called, nothing appears. The user never knew a permission was needed.

**Why it happens:**
Browser vendor documentation is clear on this requirement, but it is easy to miss when prototyping. The dashboard auto-loads and it feels natural to request permission immediately. The API does not throw — it just returns `"denied"` — so there is no error to catch and the code appears to work in the browser console.

**How to avoid:**
- Request notification permission only inside an `onClick` handler — specifically, wire it to the "Enable notifications" button in the TriggerDialog or to a dedicated "Enable run notifications" button in the top bar.
- Check `Notification.permission` state on mount. If `"default"`, show a subtle prompt badge. If `"granted"`, show the run-complete notification directly. If `"denied"`, do not show any UI for it — the user declined.
- Do not treat `"denied"` as an error; fall back to the in-app toast silently.
- Permission state persists across page loads — only request once per browser origin.

**Warning signs:**
- `Notification.permission` reads as `"denied"` immediately after `requestPermission()` is called from `useEffect`
- No permission dialog ever appears in the browser
- Works in dev but not in production (different interaction pattern)

**Phase to address:** Phase 2 (Browser notifications). Must be wired to a user gesture from day one.

---

### Pitfall 3: Polling interval leaks when Runs page unmounts — multiple intervals accumulate

**What goes wrong:**
The `Runs` component calls `setInterval` to poll `/api/runs` every 5 seconds. When the user navigates to Dashboard and back (hash change causes Preact to unmount/remount `<Runs />`), a new interval is started without the previous one being cleared. After navigating back and forth 5 times, 5 intervals fire in parallel, each updating state 5× per second. The UI flickers and the server receives 5× the expected load.

**Why it happens:**
This has already happened once in this project — the Dashboard component's polling logic (dashboard.ts:54–60) handles this correctly by using a `pollTimerRef` and checking `if (active && !pollTimerRef.current)`. But the Runs page currently has no polling at all. Adding polling by copy-pasting the pattern from the Dashboard is easy to do incorrectly if the cleanup `useEffect` is forgotten.

**How to avoid:**
- Pattern to follow: always pair `setInterval` with a matching `useEffect` cleanup that calls `clearInterval`. `pollTimerRef.current` guards against double-registration. Dashboard's `loadRuns()` + `pollTimerRef` pattern (dashboard.ts:21, 54–70) is the right model — copy it exactly.
- Verify: open Runs page, navigate away, navigate back. Open browser DevTools Network tab. Only one `/api/runs` request per 5-second window should appear.
- Do not start polling unconditionally on mount — only start if there are active runs. Stop polling when all runs are terminal.

**Warning signs:**
- Network tab shows 2× or 3× `/api/runs` requests per poll interval
- CPU % in Activity Monitor climbs on the Runs page over time
- React/Preact DevTools shows unusually frequent re-renders of the run list

**Phase to address:** Phase 3 (Runs page auto-refresh). Implement cleanup-first before adding the interval.

---

### Pitfall 4: `queued_at` field added to Run type but existing YAML entries silently read as undefined

**What goes wrong:**
`Run` interface gains a new optional `queued_at?: string` field. Existing entries in `~/.claude/kc-plugins-config/nightwatch-runs.yaml` do not have this field. When the UI tries to display `queued_at`, it renders `—` (correct, since `timeAgo(undefined)` returns `—`). However, the sort logic in `run-store.ts` (line 16: sort by `started_at`) remains untouched. If the new queue display panel sorts by `queued_at` and falls back to sorting missing entries last, the "queued" run at the top of the visible queue will appear to be a run that was queued a moment ago, while older runs (without `queued_at`) will sort to the bottom — correct behavior but only by accident, not by design.

**Why it happens:**
TypeScript marks optional fields as `field?: type`, so `undefined` is a valid value for all existing callers. The bug is invisible at compile time. The issue is that display logic assumes the field exists on new runs but not old ones, and sorting/display must explicitly handle the `undefined` case as "unknown / legacy run".

**How to avoid:**
- `queued_at` must be added to `appendRun()` in `run-store.ts` as a required field for new runs: set it to `new Date().toISOString()` at the moment `enqueue` is sent to the worker.
- For display: `queued_at ?? started_at` is the right fallback — "when did we first know about this run?" Use this composite for the queue display.
- Do NOT migrate existing YAML entries. Old runs without `queued_at` should show `—` in the trigger time column — that is accurate.
- Add a TypeScript type guard: `run.queued_at ? formatTime(run.queued_at) : '—'` to make the undefined case explicit at every display site.

**Warning signs:**
- TypeScript compiles cleanly but runtime shows `undefined` in queue display
- Sort order looks wrong when mixing old and new runs
- Queue display shows `NaN` or `Invalid Date` instead of `—` (indicates `new Date(undefined)` was called)

**Phase to address:** Phase 1 (Run type + store). Add `queued_at` to the `appendRun` call at the same time as the type definition.

---

### Pitfall 5: Removing `chat-drawer.ts` breaks nothing in TypeScript but the import still exists in a dead-code path

**What goes wrong:**
`chat-drawer.ts` is a full component (256 lines). It is not imported by `app.ts` or any page. However, if it was at any point imported as a conditional import (e.g., an old draft of `dashboard.ts` had `import { ChatDrawer }...`), TypeScript's module resolution will still flag it as "referenced" in the project graph even if the import statement was removed. The risk is the reverse: a future developer adding `ChatDrawer` back via autocomplete gets the old broken version instead of the current `ChatPanel`. The file must be deleted, not just disconnected.

**Why it happens:**
Files left in the codebase act as noise. Autocomplete systems (including Claude Code's own context loading) will surface dead files in suggestions. In a no-bundler project, dead files are not tree-shaken. They add to the cognitive load of anyone reading the `components/` directory.

**How to avoid:**
- Before removing `chat-drawer.ts`: verify it is not imported anywhere with a grep. The check: `grep -r "chat-drawer" app/` should return zero results.
- Delete the file with `git rm` so the deletion is tracked. Do not just empty the file.
- Same for any other dead component files found during cleanup (`add-target-wizard.ts` uses state logic that may or may not still be live — verify before touching).
- After deletion: run `bun typecheck` to confirm no remaining imports break.

**Warning signs:**
- `bun typecheck` passes after removing an import but the file still exists — file is now orphaned
- `grep -r "ChatDrawer" app/` still returns hits in component files after the "cleanup"
- Browser DevTools Network tab shows the old file being fetched (if it was referenced in a dynamic import somewhere)

**Phase to address:** Phase 4 (Stale UI cleanup). Always grep before delete, delete via `git rm`, typecheck after.

---

### Pitfall 6: Toast renders inside a `position:fixed` z-index below the TriggerDialog overlay

**What goes wrong:**
The TriggerDialog uses `z-index:100` (trigger-dialog.ts:47). The ChatDrawer uses `z-index:200`. If the ToastContainer is rendered with `z-index:50` (a common default), toasts triggered while the TriggerDialog is open will appear behind the dialog overlay and be invisible to the user. This is especially bad for the "run triggered" toast which fires when the user clicks "Start Run" in the dialog — exactly the moment the dialog is still visible.

**Why it happens:**
The existing project has established z-index layers but they are not documented centrally. `z-index:100` (TriggerDialog), `z-index:200` (ChatDrawer), and `z-index:10` (TargetDetail dropdown menu) are scattered across files. Adding a toast container at any z-index below 100 creates the invisible-toast bug.

**How to avoid:**
- Toast container must use `z-index:300` — above all existing overlays.
- `index.html` has no CSS custom property for z-index layers. Add them as CSS variables:
  ```
  --z-dropdown: 10;
  --z-dialog: 100;
  --z-drawer: 200;
  --z-toast: 300;
  ```
- Use these variables in all overlay components, not literal numbers.
- Test by triggering a toast while the TriggerDialog is open.

**Warning signs:**
- Toast fires (visible in browser DevTools: element exists in DOM) but user cannot see it
- Toast becomes visible only after closing the dialog
- `getComputedStyle(toastContainer).zIndex` reads lower than 100

**Phase to address:** Phase 1 (Toast infrastructure). Z-index layer must be set correctly before any testing.

---

### Pitfall 7: Browser Notification `onclick` navigates to a URL but the dashboard is not focused — notification fires silently

**What goes wrong:**
`new Notification("Run completed", { body: "..." })` is created. `notification.onclick` sets `window.focus()` and `location.hash = '#/runs/' + runId`. When the dashboard is in a background tab and the user is in another app (not another tab), `window.focus()` has no effect — browsers block cross-app focus for security reasons. The notification appears in the OS notification center, but clicking it does nothing because the tab never comes to front.

**Why it happens:**
`window.focus()` works in some browsers when clicking a notification that is from a same-session foreground tab, but is blocked for background sessions in macOS and most browser/OS combinations. The expected pattern is to use the `clients.openWindow()` API in a Service Worker, but that requires registering a Service Worker — which this no-bundler project does not have and should not add.

**How to avoid:**
- Accept the limitation: set `notification.onclick` to `window.focus()` and `location.hash = '#/runs/' + runId`. In the browser-tab scenario this works. In the cross-app scenario the user must manually switch to the tab.
- Do not add a Service Worker for this feature. The complexity is not justified for a local dashboard.
- The notification body should contain enough context (target name, status, duration) so the user can understand the result without needing to click through.
- This is a known acceptable limitation — document it in the feature implementation.

**Warning signs:**
- Clicking a notification in macOS Notification Center does nothing
- No errors appear in console (the failure is silent — the browser blocks focus)
- Works when the tab is already in foreground but not when the tab is backgrounded and user is in a different app

**Phase to address:** Phase 2 (Browser notifications). Accept the limitation; do not gold-plate.

---

### Pitfall 8: Polling on Runs page polls ALL runs but only needs to re-fetch when runs are active

**What goes wrong:**
The Runs page loads `api.getRuns()` and shows a list. Adding polling that calls `api.getRuns()` every 5 seconds is wasteful when no runs are active. The `/api/runs` endpoint reads `nightwatch-runs.yaml` on each call. At idle (no active runs), this is 12 file reads per minute for information that does not change. The Dashboard already implements conditional polling (only when `hasActiveRun` is true) — the Runs page must do the same.

**Why it happens:**
Simpler to start polling unconditionally. The cost is not obvious until you look at the YAML read frequency.

**How to avoid:**
- Same pattern as Dashboard: only poll while `runs.some(r => r.status === 'running' || r.status === 'queued')`.
- When a poll returns with all terminal statuses, clear the interval.
- On initial load (before first fetch), do not start polling — fetch once, then decide.
- The global SSE (`/api/events`) already emits `run:completed` events. Consider subscribing to it on the Runs page to trigger a re-fetch on completion rather than polling blindly. This eliminates polling entirely for the runs-list-refresh case.

**Warning signs:**
- `app/server/routes/api.ts` logs show a high `/api/runs` call rate even when no runs are active
- Adding `console.time/timeEnd` around YAML reads shows 200ms+ latency spikes every 5 seconds

**Phase to address:** Phase 3 (Runs page auto-refresh). Use the existing global SSE or conditional polling — not unconditional polling.

---

### Pitfall 9: Removing disabled Edit/Chat buttons without verifying the menu click handler logic

**What goes wrong:**
`target-detail.ts` has two `aria-disabled="true"` buttons for Edit and Chat (lines 83–93) in the dropdown menu. The cleanup task removes them. However, the dropdown `<div>` uses `onMouseLeave=${() => setShowMenu(false)}` to close. If any remaining code in the menu's click handler references a now-deleted variable or import (e.g., if a future edit touched the dropdown and added a reference), removing the buttons leaves the handler in an inconsistent state.

**Why it happens:**
The buttons are visually disabled but their surrounding container has live event handlers. Copy-pasting the removal without reading the full container context misses live code above and below the removed section.

**How to avoid:**
- When removing code inside a conditional block, read the entire parent container first — not just the targeted lines.
- After removal: check that no remaining event handler references a now-deleted variable.
- Run `bun typecheck` to catch any dangling references.
- Do a visual inspection of the rendered dropdown after removal to confirm the remaining items (Run, Dry run, separator, Remove target) all still work.

**Warning signs:**
- `bun typecheck` error after removal: "cannot find name X"
- Dropdown menu closes immediately on hover or does not open after edit
- `console.error` in browser shows "undefined is not a function" on dropdown interaction

**Phase to address:** Phase 4 (Stale UI cleanup). Read the full container before removing pieces.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Toast with `setTimeout` auto-dismiss at hardcoded 3000ms | Simpler — no configuration | Cannot dismiss urgent errors (failed trigger) manually; 3s may be too fast for non-technical messages | Acceptable for success toasts; errors should require manual dismiss |
| Store toast queue in a plain `useState` array at App level | No extra dependency | Toast state is prop-drilled to every component that might need to show a toast | Never — use a module-level signal so any module can call `showToast()` without prop threading |
| Poll `/api/runs` every 5s unconditionally | Always shows current state | 12 YAML reads/minute at idle; multiply by tabs open | Never — always gate polling on active-run check |
| Skip `queued_at` on scheduler-triggered runs (only add for manual) | Less diff | Queue display shows `—` for scheduled runs even though they were freshly queued | Never — all run enqueue paths must set `queued_at` |
| Use `window.addEventListener('focus', reload)` instead of polling | Event-driven; no interval | Does not refresh while tab is already focused (active run updates invisible until blur+focus) | Complement to polling, not replacement |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Preact signals in no-bundler setup | Importing `@preact/signals` but not adding it to the importmap in `index.html` | The importmap already includes `"@preact/signals": "/vendor/signals.module.js"`. Signals work. BUT: importing signals in a file that also does `html` tagged template calls causes silent issues if HTM's Preact reference diverges from the signals' Preact reference — they must resolve to the same module object |
| Browser Notification API | Calling `Notification.requestPermission()` as a Promise on older Safari (< 15) | Use the callback form: `Notification.requestPermission(status => ...)` as the safe fallback. Modern Safari supports Promise form. Since this dashboard is local/single-user, targeting modern browsers is fine — but if Safari is in scope, test explicitly |
| Global SSE `/api/events` reconnect | `EventSource` auto-reconnects after server restart. On reconnect, the `open` event fires again. If the handler assumes `open` = first connection and resets state, a server restart will clear in-flight run state in the UI | Check `es.readyState` before resetting: only reset state on the first open (track with a `let connected = false` flag, as already done in `chat-drawer.ts:41`) |
| `Bun.file().text()` stale handle | Reading `nightwatch-runs.yaml` via a stored `Bun.file(path)` handle after a write to the same path | Always create a new `Bun.file(path)` handle for each read. This is already done correctly in `yaml-store.ts:35`. Do not cache the `BunFile` object — only cache the parsed result |
| `setInterval` timer ID type in TypeScript | `ReturnType<typeof setInterval>` in Node vs browser returns different types. Bun's `setInterval` returns a `Timer` type, not `number` | The project already uses `useRef<ReturnType<typeof setInterval> | null>` (dashboard.ts:21) — match this pattern exactly |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Toast renders a new DOM node for each notification without a max-cap | Long-running dashboard accumulates 100+ toast nodes if run completions fire rapidly | Cap at 5 visible toasts; oldest auto-dismissed when cap exceeded | After ~20 runs in quick succession (e.g., dry-run testing) |
| Polling interval survives page navigations (not cleaned up) | `api.getRuns()` called N× per poll period where N = number of times user navigated to Runs | Cleanup effect removes the interval; verified by checking Network tab after navigation | From the second navigation cycle onwards |
| `timeAgo()` function called on every render without memoization | `timeAgo(run.started_at)` re-evaluated on every Preact re-render, including unrelated state changes | Since `timeAgo` is a pure function and runs list is short (<100), this is acceptable. If list grows, use `useMemo` | Not a concern at current scale (<100 runs) |
| Global SSE connection (`/api/events`) held open for 1 hour with 60s keepalive ping | 60 pings/hour × always-open = constant low-level traffic even at idle | 60s keepalive is already in `stream.ts:31`. This is the correct tradeoff for a local always-on tool | Not a concern for localhost single-user use |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Showing notification body content that includes run `custom_prompt` verbatim | Custom prompt may contain sensitive instructions; visible in OS notification center | Only include `target`, `status`, and `duration` in notification body. Never include `custom_prompt` |
| Storing notification permission state in `localStorage` and always granting silently | Bypasses browser permission model on re-load | Never store/replay permissions. Always check `Notification.permission` live; never cache the result |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Toast that says "Run triggered" with no target name | Ambiguous when running multiple targets in sequence | Include target name: "Run triggered for e2e-pipeline (dry-run)" |
| Notification fires even when dashboard tab is active and user can already see the run status | Notification for something already visible is noise | Only fire `new Notification()` when `document.visibilityState === 'hidden'`. If tab is visible, the in-app toast is sufficient |
| Polling refresh causes the selected run to deselect (state reset on new runs load) | User is reading a run detail; new run appears; list re-renders; selection clears | Keep `selectedId` state independent of the runs list. Re-fetch does not change `selectedId`. Only the hash-change handler changes selection |
| `queued_at` displayed as "just now" even for a run queued 2 minutes ago that has not started | Scheduler queues a run but the worker is busy; the queue timestamp looks like it was just created | `queued_at` is set at enqueue time, not at display time. `timeAgo(run.queued_at)` will correctly show "2m ago" for a stale queue entry |

---

## "Looks Done But Isn't" Checklist

- [ ] **Toast z-index**: Toast appears in all states — check: trigger toast while TriggerDialog is open, while ChatPanel is visible. Toast must be on top of both.
- [ ] **Notification permission flow**: "Enable notifications" button triggers the browser permission dialog. Check in a fresh browser profile with no prior permission grant. Check that `"denied"` state shows no error — just silent fallback to toast.
- [ ] **Polling cleanup**: Navigate to Runs page → navigate to Dashboard → navigate back to Runs. Exactly one `/api/runs` request per poll interval. Open Network tab to verify.
- [ ] **`queued_at` on all triggers**: Trigger a manual run (dashboard), trigger an interval-scheduled run (enable schedule, wait for it). Both should have `queued_at` in `nightwatch-runs.yaml`.
- [ ] **Dead code removal verification**: `grep -r "ChatDrawer\|chat-drawer" app/` returns zero results after cleanup. `grep -r "aria-disabled" app/frontend/components/target-detail.ts` returns zero results after removing disabled buttons. `bun typecheck` exits 0.
- [ ] **Notification on background tab**: Open dashboard, switch to another app, trigger a run manually (from Terminal via curl or by keeping the trigger dialog sent). Wait for run to complete. Browser notification should appear in macOS Notification Center.
- [ ] **Runs page shows queued runs**: Trigger a run when one is already running. Second run should appear in Runs page list as `queued` with a `queued_at` time display.

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Interval leak accumulated | LOW | Refresh the page — all intervals are destroyed on page unload. Add the cleanup `useEffect` to prevent recurrence |
| Toast not visible (z-index below dialog) | LOW | Add `z-index:300` to ToastContainer inline style; test immediately |
| `queued_at` missing from existing runs | LOW | Field is optional; display `—` for runs without it. No migration needed — existing behavior degrades gracefully |
| Notification permission permanently denied | LOW | Cannot be reset programmatically. User must go to `chrome://settings/content/notifications` or Safari Preferences. Show a help tooltip when `Notification.permission === "denied"` |
| Dead file not fully removed (still imported somewhere) | LOW | `bun typecheck` will catch the dangling import. Fix the import, then delete the file |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Toast side-effect at module scope | Phase 1 (toast.ts + ToastContainer) | Browser console has zero errors on page load before user interaction |
| Notification permission not user-gesture-gated | Phase 2 (notification wiring in TriggerDialog) | Open fresh browser profile; permission dialog appears only on button click |
| Polling interval leak on unmount | Phase 3 (Runs page polling) | Network tab: exactly 1 request per 5s after 3 navigations to/from Runs page |
| `queued_at` undefined in display | Phase 1 (Run type + appendRun) | `nightwatch-runs.yaml` shows `queued_at` field on all new run entries |
| Toast invisible behind dialog overlay | Phase 1 (toast z-index) | Toast visible while TriggerDialog is open |
| Dead code removal breaks imports | Phase 4 (cleanup) | `bun typecheck` exits 0 after each file deletion |
| Notification fires when tab is active | Phase 2 (visibility check) | Trigger run while tab is focused: no OS notification, only in-app toast |
| Uncapped toast accumulation | Phase 1 (toast queue design) | Trigger 10 runs rapidly: never more than 5 toast nodes in DOM |

---

## Sources

- Direct inspection: `app/frontend/app.ts`, `app/frontend/components/trigger-dialog.ts`, `app/frontend/components/target-detail.ts`, `app/frontend/components/chat-drawer.ts`, `app/frontend/pages/runs.ts`, `app/frontend/pages/dashboard.ts`, `app/server/services/run-store.ts`, `app/server/services/yaml-store.ts`, `app/server/routes/stream.ts`, `app/shared/types.ts`, `app/frontend/index.html`
- Known project pitfalls from MEMORY.md: esm.sh preact+hooks var V collision, .ts MIME type, Bun.file stale handle, import side-effect trap, Hono route ordering
- Browser Notification API permission model: MDN Web Docs — HIGH confidence (stable spec)
- Preact signals module resolution requirement (same module object): Preact signals GitHub README — HIGH confidence
- `document.visibilityState` for notification gating: W3C Page Visibility API spec — HIGH confidence

---
*Pitfalls research for: Nightwatch Dashboard v1.1 UX Polish (toast / browser notifications / auto-refresh / queued_at backward compat / dead code cleanup)*
*Researched: 2026-03-20*
