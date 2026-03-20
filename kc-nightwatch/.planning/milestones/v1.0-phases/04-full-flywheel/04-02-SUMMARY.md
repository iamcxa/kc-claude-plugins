---
phase: 04-full-flywheel
plan: 02
subsystem: ui
tags: [preact, hono, svg, typescript, bun, htm, health-api, sparkline, charts]

requires:
  - phase: 04-full-flywheel/04-01
    provides: TargetHealthData and HealthIndicatorData types in shared/types.ts; run-store and feedback-store services
  - phase: 03-flywheel-core
    provides: feedback-store getCalibrationData; run-store listRuns/getRun; shared/types.ts base types

provides:
  - GET /api/health/:target endpoint returning TargetHealthData with indicator history from last 10 runs
  - Health page (frontend) with per-target indicator sparklines, reject rate line charts, acceptance rate
  - HealthSummaryBar aggregate health display at top of Health page
  - Sparkline component (80x20px SVG polyline, color-coded by trend)
  - LineChart component (240x80px SVG line chart with axes)
  - 4-tab bottom navigation (Dashboard, Runs, Health, Config)
  - Per-target health arrows in sidebar (fetched in app.ts, passed as prop)

affects:
  - 04-03 (chat-manager — no direct dependency, but users can now navigate to Health page)

tech-stack:
  added: []
  patterns:
    - "Health API aggregation: aggregate at query time from last 10 runs per target — no materialized health store"
    - "SVG inline components: Sparkline (polyline) and LineChart (axes + data line) as pure functions returning html`` templates"
    - "healthData prop flow: app.ts fetches -> passes to Dashboard -> Dashboard passes to Sidebar (sidebar arrows are owned by app root)"
    - "TDD RED-GREEN commit pattern: failing test commit first, then implementation, then verify GREEN"

key-files:
  created:
    - app/server/routes/health-api.ts
    - app/frontend/pages/health.ts
    - app/frontend/components/sparkline.ts
    - app/frontend/components/line-chart.ts
    - app/frontend/components/health-summary.ts
    - app/tests/server/health-api.test.ts
  modified:
    - app/server/index.ts (healthApiRoutes import + registration)
    - app/frontend/lib/api.ts (getHealth method + TargetHealthData import)
    - app/frontend/components/bottom-nav.ts (4-tab nav with Health)
    - app/frontend/components/sidebar.ts (healthData prop + trend arrows)
    - app/frontend/app.ts (Health page routing + health data fetch + healthData state)
    - app/frontend/pages/dashboard.ts (accept healthData prop, pass to Sidebar)

key-decisions:
  - "Health data fetched in app.ts (root) not in sidebar — single fetch for all targets, passed as prop to Dashboard then Sidebar"
  - "Sparkline colors: last > first = success (green), last < first = error (red), equal = muted (gray) — matches visual intuition"
  - "LineChart Y-axis fixed 0-100% for reject rate — not auto-scaled, so charts are visually comparable across indicators"
  - "Overall health in HealthSummaryBar derived from majority-vote of per-target health values (not re-computed from indicators)"
  - "dashboard.ts updated to accept healthData prop — only forward, no re-fetch; app.ts is single data source"

patterns-established:
  - "Pattern: inline SVG in Preact htm — use html`` with SVG elements directly, no JSX, no build step needed"
  - "Pattern: Health prop flow — root app fetches aggregate data -> passes down as prop -> deep components render without side-effects"

requirements-completed: [HEALTH-01, HEALTH-02, HEALTH-03, HEALTH-04, HEALTH-05]

duration: 6min
completed: 2026-03-19
---

# Phase 04 Plan 02: Flywheel Health Page Summary

**Health API + SVG sparklines/charts + sidebar arrows: full flywheel health visibility from GET /api/health/:target through Preact UI**

## Performance

- **Duration:** ~6 min
- **Started:** 2026-03-19T03:12:26Z
- **Completed:** 2026-03-19T03:18:22Z
- **Tasks:** 2 code tasks + 1 auto-approved checkpoint
- **Files modified:** 12

## Accomplishments
- Created `GET /api/health/:target` aggregation endpoint — derives health from last 10 runs, builds indicator history, computes reject/acceptance rate from feedback calibration data
- Built 5 new frontend components: Sparkline (SVG polyline), LineChart (SVG with axes), HealthSummaryBar, Health page, updated BottomNav and Sidebar
- Wired health data fetch in app.ts root — fetches per-target health on mount, passes to Dashboard→Sidebar for trend arrows
- 13 new TDD tests for health API, all passing

## Task Commits

1. **TDD RED: Health API failing tests** - `d06b2d3` (test)
2. **Task 1: Health API route + aggregation logic** - `193ce7e` (feat)
3. **Task 2: Health page frontend + components** - `ec9b9dc` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified
- `app/server/routes/health-api.ts` — GET /api/health/:target aggregation (last 10 runs, indicator history, calibration-based reject/acceptance rate)
- `app/tests/server/health-api.test.ts` — 13 TDD tests covering shape, history order, health derivation, empty state, rate calculations
- `app/frontend/components/sparkline.ts` — 80x20px SVG polyline, color by last>first trend
- `app/frontend/components/line-chart.ts` — 240x80px SVG with Y-axis (0-100%), X-axis (run index), polyline in accent color
- `app/frontend/components/health-summary.ts` — HealthSummaryBar with Overall: Improving/Stable/Degrading text + arrows
- `app/frontend/pages/health.ts` — Full Health page: summary bar, per-target sections with sparklines, reject rate charts, acceptance rate, "Gathering data" empty state
- `app/frontend/lib/api.ts` — Added getHealth(target) method + TargetHealthData import
- `app/frontend/components/bottom-nav.ts` — 4 tabs: Dashboard, Runs, Health, Config
- `app/frontend/components/sidebar.ts` — Added healthData prop, renders trend arrows with aria-label next to target names
- `app/frontend/app.ts` — Health page routing (#/health), health data fetch useEffect, healthData state + prop to Dashboard
- `app/frontend/pages/dashboard.ts` — Accept healthData prop, pass to Sidebar
- `app/server/index.ts` — Added healthApiRoutes import and registration

## Decisions Made
- Health data fetch lives in `app.ts` (root), not in Dashboard or Sidebar — single network call, prop-drilling down. Avoids duplicate fetches when navigating.
- Sparkline color scheme: last > first = success, last < first = error, equal = muted. Matches intuitive "up is good".
- LineChart Y-axis is fixed 0.0–1.0 (reject rate fraction, shown as 0%–100%). Not auto-scaled — charts are visually comparable across indicators.
- HealthSummaryBar derives `overallHealth` from majority-vote of per-target health values (improving/stable/degrading counts), not re-aggregated from indicators.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Dashboard updated to accept healthData prop**
- **Found during:** Task 2 (frontend wiring)
- **Issue:** app.ts passes `healthData` to `<${Dashboard}>` but `Dashboard` component didn't accept any props — prop would be silently ignored, sidebar arrows would never render
- **Fix:** Added `DashboardProps` interface with `healthData?: Record<string, ...>` and forwarded to `<${Sidebar}>`
- **Files modified:** app/frontend/pages/dashboard.ts
- **Verification:** healthData prop reaches Sidebar component
- **Committed in:** ec9b9dc (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 missing critical prop forwarding)
**Impact on plan:** Essential for sidebar arrows to render. Without this fix, the healthData state would be fetched but never displayed.

## Issues Encountered
- Pre-existing test failures (3): `writeFeedbackTrends` not exported, `appendFeedback`/`appendRun` module mock issues — confirmed pre-existing before this plan. Out of scope.

## Next Phase Readiness
- Health API endpoint live at GET /api/health/:target — Phase 4 Plan 3 (chat MCP) can call it if needed
- All 5 HEALTH requirements completed (HEALTH-01 through HEALTH-05)
- Bottom nav is now 4 tabs — consistent with UI-SPEC

---
*Phase: 04-full-flywheel*
*Completed: 2026-03-19*
