# Phase 16: Health Page Enrichment - Context

**Gathered:** 2026-03-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Enrich the health page with real sparkline history (backed by Phase 15 data layer), a calibration table, hover tooltips with run IDs, and a forge validation results card. All work is frontend — new components + wiring to existing Phase 15 API endpoints. No new API endpoints.

</domain>

<decisions>
## Implementation Decisions

### Page Layout
- **D-01:** Page sections top-to-bottom: HealthSummaryBar → ForgeResultCard → Target Cards → Calibration Table → Reject Rate Charts. Rationale: system-level (forge) first for quick glance, then per-target detail, then cross-target summary.
- **D-02:** No tabs — keep the existing scrollable page model. Tabs add state management complexity under the no-build constraint.

### ForgeResultCard
- **D-03:** Expandable card pattern — collapsed shows status icon + pass/fail badge + relative time ("2h ago"). Click expands to show branch name + validation details list.
- **D-04:** Fail state uses `var(--error)` accent. Pass uses `var(--success)`. Stale data (>36h) uses `var(--muted)` color to indicate outdated.
- **D-05:** Data source: `GET /api/forge/results` (Phase 15 endpoint, always 200, `{ forge_result, run_date, stale }`). Frontend needs new `api.getForgeResults()` method.

### Calibration Table
- **D-06:** Single flat table (not per-target grouped). All indicators in one table sorted by reject rate descending.
- **D-07:** Columns: Indicator | Threshold | Reject % | Feedback Count. Rows where `total_feedback < 10` show "(N/10)" in Threshold column instead of a number.
- **D-08:** Data source: existing `api.getCalibration()` returns `CalibrationData[]` — already has all needed fields including `current_threshold`, `threshold_null_reason`, `reject_rate`, `total_feedback`.

### Sparkline Tooltips
- **D-09:** Custom tooltip div (not SVG `<title>` native tooltip). Positioned absolutely relative to sparkline container. Shows two lines: value as percentage + run ID.
- **D-10:** Implementation: invisible SVG rect hit areas over each data point. Mouse enter shows tooltip, mouse leave hides. No click interaction.
- **D-11:** Data shape: parallel arrays — add `runIds?: string[]` to Sparkline Props. When absent, tooltip shows value only. LineChart component unchanged.
- **D-12:** Run ID data must flow from health API → frontend. `HealthIndicatorData.history` stays `number[]`, add `run_ids?: string[]` to HealthIndicatorData type. health-api.ts already has run data in scope — extract run IDs during history construction.

### Claude's Discretion
- Tooltip positioning logic (above/below/auto based on viewport)
- Sparkline hit area sizing (rect width per data point)
- ForgeResultCard expand/collapse animation (CSS transition or instant)
- Calibration table empty state when no feedback exists
- Whether to add section headers/dividers between page sections

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Frontend Components
- `app/frontend/pages/health.ts` — Current health page (160 lines). Target card rendering, sparkline + LineChart usage, data fetching pattern
- `app/frontend/components/sparkline.ts` — Current sparkline (34 lines). Pure SVG polyline, Props: `{values, width?, height?}`. Needs tooltip enhancement
- `app/frontend/components/line-chart.ts` — LineChart with axes (54 lines). NOT changed in this phase, but reference for SVG pattern
- `app/frontend/components/health-summary.ts` — HealthSummaryBar at top of page
- `app/frontend/components/toast.ts` — Example of absolute-positioned floating UI element (pattern for tooltip)

### API Layer
- `app/frontend/lib/api.ts` — Frontend API client. Has `getHealth()` and `getCalibration()`, needs new `getForgeResults()` and `getSignalPriority()` methods
- `app/server/routes/forge.ts` — `GET /api/forge/results` (Phase 15). Returns ForgeResultData
- `app/server/routes/signals.ts` — `GET /api/signals/priority` (Phase 15). Returns SignalPriorityItem[] (Phase 17 will use)
- `app/server/routes/health-api.ts` — `GET /api/health/:target`. Needs to include run_ids in indicator history

### Types
- `app/shared/types.ts` — CalibrationData (line 176), ForgeResultData (line 186), SignalPriorityItem (line 196), HealthIndicatorData, TargetHealthData

### Phase 15 Context
- `.planning/phases/15-data-layer-foundations/15-CONTEXT.md` — Data layer decisions (EMA, N gate, bucketing) that this phase consumes

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Sparkline` component: Pure SVG, easy to extend with hit areas + tooltip state. Already handles `values.length < 2` gracefully.
- `LineChart` component: Similar SVG pattern but with axes. NOT getting tooltips in this phase.
- `toast.ts`: Uses signal-backed absolute-positioned div — similar pattern usable for tooltip.
- `api.ts:get<T>()`: Generic fetch helper, trivial to add `getForgeResults()`.

### Established Patterns
- Preact + HTM: `html\`` template literals, `useState`/`useEffect` hooks
- CSS via inline styles (no CSS modules or classes) — all styling is `style="..."` strings
- No build step — all imports via `htm/preact`, vendor ESM files
- State management: local component state only (no global store)

### Integration Points
- `health.ts` useEffect: Currently fetches targets + health data. Needs to also fetch forge results + calibration data.
- `HealthIndicatorData.history: number[]` → needs parallel `run_ids?: string[]`
- `health-api.ts` line 30-35: Already iterates `runsWithSummary` — run IDs available in the loop for extraction

</code_context>

<specifics>
## Specific Ideas

- ForgeResultCard collapsed height should match other cards' header height for visual consistency
- Calibration table "(N/10)" display mirrors the N gate message pattern from Phase 15 (D-04)
- Tooltip should disappear immediately on mouse leave (no fade delay) — matches the tool's utilitarian aesthetic

</specifics>

<deferred>
## Deferred Ideas

- Tooltip on LineChart (Reject Rate Charts section) — separate enhancement, not in Phase 16 scope
- Calibration table sorting toggle (click column header to sort) — premature interactivity
- ForgeResultCard linking to actual PR on GitHub — requires `gh` CLI auth verification in safehouse context (noted as blocker in STATE.md)

</deferred>

---

*Phase: 16-health-page-enrichment*
*Context gathered: 2026-03-26*
