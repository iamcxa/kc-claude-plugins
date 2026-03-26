---
phase: 16-health-page-enrichment
plan: "02"
subsystem: frontend
tags: [component, preact, htm, sparkline, calibration, forge, health-page]
dependency_graph:
  requires: [16-01]
  provides: [forge-result-card, calibration-table, sparkline-tooltip, health-page-wiring]
  affects: [app/frontend/pages/health.ts, app/frontend/components/sparkline.ts]
tech_stack:
  added: []
  patterns:
    - Preact+HTM inline-style components
    - Pure helper functions re-implemented in test files (no DOM)
    - TDD with bun:test
key_files:
  created:
    - app/frontend/components/forge-result-card.ts
    - app/frontend/components/calibration-table.ts
    - app/tests/frontend/forge-result-card.test.ts
    - app/tests/frontend/calibration-table.test.ts
    - app/tests/frontend/sparkline.test.ts
  modified:
    - app/frontend/components/sparkline.ts
    - app/frontend/pages/health.ts
decisions:
  - ForgeResultCard renders Unavailable (not crash) when data===null (fetch error pattern from RESEARCH Pitfall 5)
  - CalibrationTable isLast detection uses sorted array length (calibration.length) for last-row no-border
  - Sparkline tooltip positioned as sibling to SVG (not inside SVG) per RESEARCH Pitfall 1
  - Font-size 12px standardized to 11px on "runs analyzed" text per UI-SPEC typography contract
metrics:
  duration: 31min
  completed: "2026-03-26"
  tasks_completed: 3
  tasks_total: 4
  files_created: 5
  files_modified: 2
---

# Phase 16 Plan 02: Health Page Enrichment (Components + Wiring) Summary

ForgeResultCard expand/collapse + CalibrationTable sorted rows + Sparkline tooltips wired into health page in D-01 section order.

## What Was Built

Three tasks completed: two new components with TDD tests, one existing component enhanced, and the health page wired to use all three.

### Task 1: ForgeResultCard and CalibrationTable components (TDD)

**ForgeResultCard** (`app/frontend/components/forge-result-card.ts`):
- Four states: normal (pass/fail/stale), null (no forge run), fetch error (Unavailable), expanded
- Exported pure helpers: `relativeTime()`, `statusColor()`, `statusIcon()`
- Accessibility: `role="button"`, `tabIndex={0}`, `aria-expanded`, Enter/Space keyboard handlers
- Colors: `var(--success)` for pass, `var(--error)` for fail, `var(--muted)` for stale/null
- Stale text: entire card text color shifts to `var(--muted)` when `data.stale === true`
- Expanded section: branch in `var(--font-mono)`, details as `<ul>` list

**CalibrationTable** (`app/frontend/components/calibration-table.ts`):
- Exported pure helpers: `sortByRejectRate()` (never mutates), `formatThreshold()`
- Loading state: single "Loading..." row spanning 4 columns
- Empty state: "No feedback collected yet — run the pipeline to generate data."
- N-gate threshold: renders `threshold_null_reason` in italic+muted when `current_threshold === null`
- Sort: descending by reject_rate using `[...data].sort((a, b) => b.reject_rate - a.reject_rate)`
- 4 columns: Indicator, Threshold, Reject %, Feedback
- Last row: no bottom border

**Tests** (24 tests total):
- `forge-result-card.test.ts`: 10 tests — relativeTime (6 cases), statusColor (6 cases)
- `calibration-table.test.ts`: 14 tests — sortByRejectRate (5 cases), formatThreshold (7 cases)

### Task 2: Sparkline tooltip enhancement (TDD)

**Enhanced Sparkline** (`app/frontend/components/sparkline.ts`):
- New `runIds?: string[]` prop parallel to `values`
- Exported helpers: `tooltipStyle()`, `formatTooltipValue()`
- Transparent `<rect>` hit areas per data point (edge-guarded: first rect starts at x=0, last ends at x=width)
- `pointer-events:none` on `<polyline>` so rects capture all events
- Tooltip div as sibling to SVG (not inside SVG) at `position:absolute;top:-36px`
- Edge guards: first point left-anchored (`left:0;transform:none`), last point right-anchored (`right:0;left:auto;transform:none`), middle centered (`transform:translateX(-50%)`)
- Run ID line in `var(--muted)` when `runIds?.[activeIdx]` present

**Tests** (`sparkline.test.ts`, 17 tests):
- tooltipStyle: 7 edge cases (first, last, middle, 2-point extremes)
- formatTooltipValue: 6 rounding cases
- pointSpacing: 4 calculation verifications

### Task 3: Health page wiring

**Updated health.ts**:
- Imports: ForgeResultCard, CalibrationTable, ForgeResultData, CalibrationData
- New state: `forgeData`, `calibration`, `calibrationLoading`
- New `useEffect`: parallel fetch of forge results and calibration data
- Section order matches D-01: HealthSummaryBar → ForgeResultCard → loading/error/sparse → Target Cards → CalibrationTable → Reject Rate Charts
- Sparkline now passes `runIds=${indicator.run_ids}` for tooltip
- Fixed font-size 12px → 11px on "runs analyzed" text per UI-SPEC

## Test Results

- Frontend tests: 59 pass (42 pre-existing + 17 sparkline)
- Full suite: 436 pass, 0 fail

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Typography] Standardized font-size 12px to 11px on "runs analyzed" text**
- **Found during:** Task 3 (health.ts wiring)
- **Issue:** Existing health.ts had `font-size:12px` on the "runs analyzed" label; UI-SPEC mandates 11px for micro/caption tier to keep the scale at 3 sizes
- **Fix:** Changed to `font-size:11px` per UI-SPEC typography contract
- **Files modified:** `app/frontend/pages/health.ts` (line 108)
- **Commit:** b008f58

None of the other plan steps required deviations — executed exactly as specified.

## Known Stubs

None — all data flows are wired through real API calls (`api.getForgeResults()`, `api.getCalibration()`). The `forgeData` state initializes to `null` (shows "Unavailable" until fetch completes), which is intentional fallback behavior per RESEARCH Pitfall 5.

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| Task 1 | e1dfdb2 | feat(16-02): ForgeResultCard + CalibrationTable components with tests |
| Task 2 | 9879041 | feat(16-02): enhance Sparkline with tooltip hit areas + sparkline tests |
| Task 3 | b008f58 | feat(16-02): wire ForgeResultCard, CalibrationTable, and tooltipped Sparklines into health page |
