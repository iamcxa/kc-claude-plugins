---
phase: 02-core-cockpit
plan: "03"
subsystem: ui
tags: [preact, htm, hono, sse, typescript, bun, frontend, dashboard]

# Dependency graph
requires:
  - phase: 02-01
    provides: REST API endpoints (targets, runs, schedule, SSE stream)
  - phase: 02-02
    provides: Worker queue, scheduler, NW memory isolation
provides:
  - Preact+HTM frontend served at http://localhost:3200
  - Master-detail dashboard with target sidebar and detail panel
  - Trigger modal (Production/Dry-run, custom instructions, self-repair toggle)
  - SSE-connected collapsible log stream with auto-scroll and raw toggle
  - Run history list with status/target filters and run detail view
  - Schedule bar with enabled/disabled state and countdown
  - Config stub page
  - Hash-based client-side router with bottom navigation
  - Vendored Preact 10.23.1 + HTM 3.1.1 ESM builds (no CDN dependency)
affects:
  - 03-chat-interface
  - 04-mcp-health

# Tech tracking
tech-stack:
  added:
    - Preact 10.23.1 (vendored ESM build via esm.sh)
    - HTM 3.1.1 (pre-bound htm/preact ESM — exports named 'html')
    - "@preact/signals 1.3.0 (vendored ESM)"
    - hono/bun serveStatic (static file serving from Hono)
  patterns:
    - HTM tagged-template components (html`` syntax, never JSX)
    - Import maps in index.html pointing to /vendor/ — no bundler required
    - On-the-fly .ts transpilation via Bun (MIME type: application/javascript)
    - SSE EventSource client with phase-grouped collapsible log rendering
    - Hash-based routing with hashchange listener (no client router library)
    - Preact split vendor (preact core + preact/hooks separate) to avoid duplicate var V

key-files:
  created:
    - app/frontend/index.html
    - app/frontend/app.ts
    - app/frontend/lib/api.ts
    - app/frontend/vendor/preact.module.js
    - app/frontend/vendor/htm.module.js
    - app/frontend/vendor/signals.module.js
    - app/frontend/pages/dashboard.ts
    - app/frontend/pages/runs.ts
    - app/frontend/pages/config.ts
    - app/frontend/components/schedule-bar.ts
    - app/frontend/components/bottom-nav.ts
    - app/frontend/components/sidebar.ts
    - app/frontend/components/target-detail.ts
    - app/frontend/components/trigger-dialog.ts
    - app/frontend/components/log-stream.ts
    - app/frontend/components/run-timeline.ts
  modified:
    - app/server/index.ts

key-decisions:
  - "Preact vendored as split modules (preact core + preact/hooks separate file) — single-file esm.sh build contained duplicate 'var V' symbol causing ReferenceError in module scope"
  - "Bun transpiles .ts files on-the-fly via serveStatic route — Content-Type must be set to application/javascript not text/plain; resolved with a custom route wrapper"
  - "Import map in index.html maps 'preact/hooks' to the separate hooks vendor file — enables standard import { useState } from 'preact/hooks' without bundling"
  - "All components use HTM tagged-template syntax (html`...`) in plain .ts files — no JSX, no build step, consistent with no-bundler architecture"

patterns-established:
  - "Vendor split pattern: when a single-file ESM build causes symbol collision, split into separate files for core and hooks exports"
  - "Bun on-the-fly transpilation: serve .ts frontend files via explicit Content-Type override (application/javascript) so browsers accept them as ES modules"
  - "HTM component pattern: import { html } from 'htm/preact', import hooks from 'preact/hooks', write html`<div>` tagged templates — never angle-bracket JSX in .ts files"

requirements-completed:
  - DASH-01
  - DASH-02
  - DASH-03
  - DASH-04
  - DASH-05
  - EXEC-01
  - EXEC-02
  - EXEC-03
  - EXEC-06
  - EXEC-07
  - EXEC-08
  - EXEC-09
  - HIST-01
  - HIST-02
  - HIST-03
  - HIST-04

# Metrics
duration: ~90min
completed: 2026-03-18
---

# Phase 2 Plan 03: Core Cockpit Frontend Summary

**Preact+HTM dashboard cockpit with vendored ESM modules, SSE log stream, trigger modal, run history, and Bun on-the-fly .ts transpilation — no bundler required**

## Performance

- **Duration:** ~90 min (includes two post-task fix rounds)
- **Started:** 2026-03-18
- **Completed:** 2026-03-18
- **Tasks:** 3 (2 auto + 1 checkpoint:human-verify — approved)
- **Files modified:** 17 (16 frontend files created + server/index.ts modified)

## Accomplishments

- Built complete Preact+HTM frontend cockpit with 16 files (no bundler, no CDN — all vendor files local)
- Dashboard master-detail layout: sidebar target list, detail panel with north star and action buttons, trigger modal
- SSE log stream with collapsible phase groups, raw/parsed toggle, auto-scroll, and reconnect button
- Runs page with history list (status/target filter), run detail view with RunTimeline and LogStream
- Schedule bar countdown (10s tick), config stub page, hash-based router, bottom navigation
- Human visually verified at checkpoint: all UI elements render, nav works, modal opens/closes, schedule bar shows state
- Resolved two post-Task-2 issues (MIME type error + duplicate var V) before checkpoint approval

## Task Commits

Each task was committed atomically:

1. **Task 1: Vendor files + import map + api client + static serving** - `971c663` (feat)
2. **Task 2: App router + all page and component files** - `f875dfe` (feat)
3. **Fix: transpile .ts frontend files on-the-fly** - `4cad92d` (fix — deviation, Rule 1)
4. **Fix: split preact vendor** - `c7bd879` (fix — deviation, Rule 1)
5. **Task 3: Visual verification checkpoint** — approved by human (no commit)

## Files Created/Modified

- `app/frontend/index.html` — Import map pointing to /vendor/, CSS variables, root mount point
- `app/frontend/app.ts` — Hash-based router, App component, ScheduleBar + BottomNav + page routing
- `app/frontend/lib/api.ts` — Typed fetch wrapper for all API endpoints (getTargets, getRuns, triggerRun, etc.)
- `app/frontend/vendor/preact.module.js` — Vendored Preact 10.23.1 ESM (core + render)
- `app/frontend/vendor/htm.module.js` — Vendored HTM 3.1.1 pre-bound to Preact (exports named 'html')
- `app/frontend/vendor/signals.module.js` — Vendored @preact/signals 1.3.0 ESM
- `app/frontend/pages/dashboard.ts` — Master-detail layout, target selection, polling for active runs
- `app/frontend/pages/runs.ts` — Run history list with filters, run detail with LogStream + RunTimeline
- `app/frontend/pages/config.ts` — Config stub ("Phase 3" locked message)
- `app/frontend/components/schedule-bar.ts` — Scheduler state bar with 10s countdown tick
- `app/frontend/components/bottom-nav.ts` — 3-tab bottom navigation, accent highlight on active
- `app/frontend/components/sidebar.ts` — Target list with type badge, last-run status dot, Add Target button
- `app/frontend/components/target-detail.ts` — Target detail panel with north star, action buttons, ellipsis menu
- `app/frontend/components/trigger-dialog.ts` — Run modal with Production/Dry-run toggle, textarea, self-repair
- `app/frontend/components/log-stream.ts` — SSE EventSource client, phase-grouped collapsible log, auto-scroll
- `app/frontend/components/run-timeline.ts` — Phase progress bar (6 phases, color-coded by completion state)
- `app/server/index.ts` — Added serveStatic routes for /vendor/*, /pages/*, /components/*, /lib/*, /app.ts; on-the-fly .ts transpilation with correct Content-Type; root SPA route

## Decisions Made

- **Preact vendor split:** Vendored single-file esm.sh build contained duplicate `var V` symbol (both preact core and hooks export it). Fix: split into two vendor files — `preact.module.js` for core+render, `preact/hooks` mapped separately.
- **On-the-fly .ts transpilation:** Bun's `serveStatic` serves `.ts` files with `text/plain` MIME type, causing browser to refuse them as ES modules. Fix: custom route that reads file via `Bun.file`, transpiles with `Bun.Transpiler`, and responds with `Content-Type: application/javascript`.
- **No bundler architecture validated:** Import maps + vendored ESM + Bun transpilation = full Preact app with zero build tooling. This is the correct approach for the Phase 2 cockpit scope.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] MIME type error: .ts files rejected as ES modules**
- **Found during:** Post-Task-2 verification (browser console error)
- **Issue:** Bun's `serveStatic` serves `.ts` files with `Content-Type: text/plain`. Browsers refuse to import `text/plain` as an ES module, blocking the entire frontend from loading.
- **Fix:** Replaced generic `serveStatic` for `.ts` routes with a custom Hono handler that reads the file via `Bun.file`, transpiles with `new Bun.Transpiler({ loader: 'ts' }).transformSync()`, and returns `Content-Type: application/javascript`.
- **Files modified:** `app/server/index.ts`
- **Verification:** Browser DevTools showed no MIME errors; frontend loaded successfully.
- **Committed in:** `4cad92d`

**2. [Rule 1 - Bug] Duplicate `var V` in preact vendor — ReferenceError on module load**
- **Found during:** Post-Task-2 verification (browser console ReferenceError)
- **Issue:** Single-file esm.sh build of Preact bundled both core and hooks, both of which declared `var V` at module scope. ES module strict mode treats this as a redeclaration error.
- **Fix:** Split vendor into two files: `preact.module.js` (core + render only, from esm.sh/preact@10.23.1/src) and a separate hooks export. Updated import map in `index.html` to map `preact/hooks` to the dedicated hooks file.
- **Files modified:** `app/frontend/vendor/preact.module.js`, `app/frontend/index.html`, `app/server/index.ts`
- **Verification:** Browser console clean; Preact components mounted and rendered correctly.
- **Committed in:** `c7bd879`

---

**Total deviations:** 2 auto-fixed (2 Rule 1 — bugs)
**Impact on plan:** Both fixes were required to make the frontend load at all. No scope creep — fixes address runtime errors from vendor/server behavior not visible during code authoring.

## Issues Encountered

- HTM tagged-template syntax required careful attention: `html\`<div>\`` angle-bracket style does NOT work — must use `html\`div\`` or `html\`div class="x"\`` form. Several components needed review to ensure no angle-bracket leakage.
- `preact/hooks` import map entry initially pointed to the full preact bundle — after vendor split, the hooks file is a re-export wrapper that imports from the core file. This required coordination between the two vendor files.

## User Setup Required

None — no external service configuration required. Server starts with `bun run server/index.ts` and frontend loads at `http://localhost:3200`.

## Next Phase Readiness

- All API endpoints wired to frontend components; trigger modal sends POST /api/runs; log stream connects SSE
- Phase 3 (Chat Interface) can build on top of this cockpit — the dashboard layout and bottom nav are in place
- Config page is a stub awaiting Phase 3 implementation
- The no-bundler architecture (import maps + vendor files + Bun transpile) is validated and documented — Phase 3 can add new .ts files without any tooling changes

## Self-Check: PASSED

- FOUND: `.planning/phases/02-core-cockpit/02-03-SUMMARY.md`
- FOUND: `971c663` feat(02-03): vendor files + import map + api client + static serving
- FOUND: `f875dfe` feat(02-03): complete Preact+HTM frontend — router, dashboard, runs, config, components
- FOUND: `4cad92d` fix(02-03): transpile .ts frontend files on-the-fly — fix MIME type error
- FOUND: `c7bd879` fix(02-03): split preact vendor — separate core + hooks to fix duplicate var V

---
*Phase: 02-core-cockpit*
*Completed: 2026-03-18*
