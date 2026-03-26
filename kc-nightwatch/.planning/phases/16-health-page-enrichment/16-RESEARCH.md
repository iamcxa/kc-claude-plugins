# Phase 16: Health Page Enrichment - Research

**Researched:** 2026-03-26
**Domain:** Preact/HTM frontend — SVG tooltips, expandable card UI, calibration table rendering
**Confidence:** HIGH

## Summary

Phase 16 is a pure frontend enrichment. All three requirements (VIZ-02, VIZ-03, FORGE-01) are satisfied by adding new Preact components and wiring to Phase 15 API endpoints that are already implemented and tested. No new API endpoints are needed.

The key technical challenges are: (1) adding SVG hit-area rectangles over sparkline data points for hover detection — the existing `Sparkline` component must be extended with a local tooltip state using `useState`, (2) building a `ForgeResultCard` with expand/collapse state using `useState` plus CSS-based toggle, (3) rendering a flat calibration table with a guarded threshold cell. Every pattern needed already exists in the codebase — `toast.ts` shows absolute-positioned floating UI, `sparkline.ts` shows SVG coordinate math, `api.ts` shows the `get<T>()` fetch helper.

The main integration point is `health-api.ts`: it already iterates `runsWithSummary` to build `indicator_baseline`, but run IDs are not extracted into the response. A parallel `run_ids` field must be added to `HealthIndicatorData` in `types.ts` and populated in `health-api.ts`.

**Primary recommendation:** Implement in 2 plans — Plan 16-01 (server-side run_ids extraction + type changes + API client method) and Plan 16-02 (frontend components: ForgeResultCard, CalibrationTable, sparkline tooltip, health.ts wiring). Each plan has a focused set of files and a clear test contract.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Page sections top-to-bottom: HealthSummaryBar → ForgeResultCard → Target Cards → Calibration Table → Reject Rate Charts. Rationale: system-level (forge) first for quick glance, then per-target detail, then cross-target summary.
- **D-02:** No tabs — keep the existing scrollable page model. Tabs add state management complexity under the no-build constraint.
- **D-03:** Expandable card pattern — collapsed shows status icon + pass/fail badge + relative time ("2h ago"). Click expands to show branch name + validation details list.
- **D-04:** Fail state uses `var(--error)` accent. Pass uses `var(--success)`. Stale data (>36h) uses `var(--muted)` color to indicate outdated.
- **D-05:** Data source: `GET /api/forge/results` (Phase 15 endpoint, always 200, `{ forge_result, run_date, stale }`). Frontend needs new `api.getForgeResults()` method.
- **D-06:** Single flat table (not per-target grouped). All indicators in one table sorted by reject rate descending.
- **D-07:** Columns: Indicator | Threshold | Reject % | Feedback Count. Rows where `total_feedback < 10` show "(N/10)" in Threshold column instead of a number.
- **D-08:** Data source: existing `api.getCalibration()` returns `CalibrationData[]` — already has all needed fields including `current_threshold`, `threshold_null_reason`, `reject_rate`, `total_feedback`.
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

### Deferred Ideas (OUT OF SCOPE)

- Tooltip on LineChart (Reject Rate Charts section) — separate enhancement, not in Phase 16 scope
- Calibration table sorting toggle (click column header to sort) — premature interactivity
- ForgeResultCard linking to actual PR on GitHub — requires `gh` CLI auth verification in safehouse context (noted as blocker in STATE.md)
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| VIZ-02 | Health page shows calibration table with current threshold, reject rate, total feedback count, and sample size per indicator | `api.getCalibration()` already returns `CalibrationData[]` with all fields. New `CalibrationTable` component renders flat table sorted by reject rate descending. N-gate display uses `threshold_null_reason` field. |
| VIZ-03 | Sparkline and trend chart show tooltip with exact value and run ID on hover | `Sparkline` extended with `runIds?: string[]` prop + local `useState` for active tooltip index. SVG `<rect>` hit areas cover each data point. Tooltip div absolutely positioned within `position:relative` container. `run_ids` extracted from `health-api.ts` and added to `HealthIndicatorData` type. |
| FORGE-01 | Health page displays forge validation results from the most recent self-repair run (status, branch, details) | `GET /api/forge/results` already implemented in Phase 15. `api.getForgeResults()` added to api.ts. New `ForgeResultCard` component with useState expand/collapse. |
</phase_requirements>

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Preact + HTM | vendored ESM | UI components, `useState`/`useEffect` hooks | Established pattern in this codebase — no build step |
| TypeScript | 5.x (Bun native) | Types for new props and API shapes | All existing files use `.ts` with strict types |
| Bun test | 1.3.9 | Test runner for server-side unit tests | Existing test infrastructure (`bun test`) |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Hono | ^4.12.8 | Server route handler | Only if new routes added — not needed this phase |
| @preact/signals | vendored ESM | Module-level reactive state | Not needed this phase — local `useState` is sufficient |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| SVG `<rect>` hit areas | SVG `<title>` native tooltip | `<title>` tooltips are browser-styled, can't show two lines, no run ID — D-09 mandates custom div |
| Local `useState` for expand/collapse | @preact/signals | Signals are overkill for single-component local toggle state |
| Absolute-positioned div tooltip | SVG `<foreignObject>` | foreignObject is complex in HTM templates; absolute div is the existing pattern (toast.ts) |

**Installation:** No new packages needed. All dependencies are vendored or already in `package.json`.

---

## Architecture Patterns

### Recommended Project Structure
```
app/
├── frontend/
│   ├── components/
│   │   ├── sparkline.ts          # MODIFIED: add runIds prop + tooltip
│   │   ├── forge-result-card.ts  # NEW
│   │   └── calibration-table.ts  # NEW
│   ├── lib/
│   │   └── api.ts                # MODIFIED: add getForgeResults()
│   └── pages/
│       └── health.ts             # MODIFIED: fetch + wire new components
├── server/
│   └── routes/
│       └── health-api.ts         # MODIFIED: extract run_ids parallel array
├── shared/
│   └── types.ts                  # MODIFIED: HealthIndicatorData.run_ids
└── tests/
    ├── server/
    │   └── health-api.test.ts    # MODIFIED: add run_ids assertions
    └── frontend/
        ├── sparkline.test.ts     # NEW: tooltip logic tests
        ├── forge-result-card.test.ts  # NEW: pure function tests
        └── calibration-table.test.ts # NEW: row-render logic tests
```

### Pattern 1: Sparkline with SVG Hit Areas

**What:** The `Sparkline` component wraps the existing `<svg>` in a `position:relative` container div. A `<rect>` per data point acts as an invisible hit target (full-height column). `onMouseEnter`/`onMouseLeave` handlers on each rect update a local `activeIdx` state. When `activeIdx !== null` and `runIds` is provided, an absolutely-positioned tooltip div renders above the container.

**When to use:** Whenever SVG paths need hover interaction — the path itself has no width for mouse events, rects provide the hit surface.

**Key coordinate math (existing sparkline.ts pattern):**
```typescript
// Source: app/frontend/components/sparkline.ts
const x = (i / (values.length - 1)) * width
const y = height - ((v - min) / range) * height
// Hit rect: centered on x, full height, width = pointSpacing
const pointSpacing = values.length > 1 ? width / (values.length - 1) : width
const rectX = x - pointSpacing / 2
```

### Pattern 2: Expandable Card (ForgeResultCard)

**What:** A single `useState<boolean>` (`expanded`) drives the conditional render. Collapsed state: one-line row with icon, badge, and relative time. Expanded state: additional section shows branch name + details list. Click anywhere on the collapsed row toggles `expanded`.

**Relative time helper pattern** (no library — hand-rolled per project convention):
```typescript
function relativeTime(isoDate: string | null): string {
  if (!isoDate) return 'never'
  const diffMs = Date.now() - new Date(isoDate).getTime()
  const diffH = Math.floor(diffMs / 3600000)
  if (diffH < 1) return 'just now'
  if (diffH < 24) return `${diffH}h ago`
  return `${Math.floor(diffH / 24)}d ago`
}
```

**CSS color mapping** (D-04):
```typescript
function statusColor(data: ForgeResultData): string {
  if (data.stale) return 'var(--muted)'
  if (!data.forge_result) return 'var(--muted)'
  return data.forge_result.status === 'pass' ? 'var(--success)' : 'var(--error)'
}
```

### Pattern 3: Calibration Table

**What:** A `<table>` rendered from `CalibrationData[]` sorted by `reject_rate` descending. Threshold cell: when `current_threshold === null`, render `threshold_null_reason` (e.g., "(5/10)"). Otherwise render threshold formatted as percentage.

**Empty state:** When `api.getCalibration()` returns empty array, show a single-row "No feedback collected yet" message.

**Sort pattern:**
```typescript
const sorted = [...calibration].sort((a, b) => b.reject_rate - a.reject_rate)
```

### Pattern 4: Tooltip Absolute Positioning

**What:** Tooltip div with `position:absolute;top:-36px;left:${x}px;transform:translateX(-50%)`. Container div has `position:relative`. This is the same positioning model as `toast.ts` (which uses `position:fixed`), but scoped to the sparkline container.

**Viewport edge handling** (Claude's Discretion): Use `left:0;transform:none` for the first data point, `right:0;transform:none` for the last. Simple — avoids needing `getBoundingClientRect()` in a no-DOM-access Preact context.

### Pattern 5: Run IDs Extraction in health-api.ts

**What:** The `runsWithSummary` loop in `health-api.ts` (lines 24–35) already iterates runs in chronological order. A parallel `indicatorRunIds: Record<string, string[]>` map mirrors `indicatorHistory`. At each iteration, `runData.id` is pushed to `indicatorRunIds[name]`.

**Current code location:** `app/server/routes/health-api.ts` lines 21–35

**Change required:** Add `run_ids` field extraction alongside the existing `indicatorHistory` build:
```typescript
const indicatorRunIds: Record<string, string[]> = {}
// ... inside the existing loop:
if (!indicatorRunIds[name]) indicatorRunIds[name] = []
indicatorRunIds[name].push(runData.id)
// ... in the indicators build:
indicators[name] = {
  current: history[history.length - 1] ?? 0,
  trend,
  history,
  run_ids: indicatorRunIds[name] ?? [],
}
```

### Anti-Patterns to Avoid

- **Mutating CalibrationData[] before sorting:** Use spread `[...calibration].sort(...)` — the original array reference must not be mutated (shared state).
- **Storing tooltip content in a signal:** Local `useState<number | null>` is sufficient; module-level signals would cause cross-instance bleed between multiple sparklines on the same page.
- **Adding `onMouseMove` to the polyline:** The polyline stroke has 1.5px width — not a reliable hit target. Always use `<rect>` hit areas.
- **Hardcoding "N/10" in the frontend:** The `threshold_null_reason` field already carries this string from the backend. Don't duplicate the logic.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Relative time display | Custom date library or moment.js | Inline `relativeTime()` helper (< 10 lines) | No library needed; only 3 display states (just now / Xh ago / Xd ago) |
| Tooltip positioning | Third-party tooltip library (Popper.js, Floating UI) | `position:absolute` with edge guard | No-build constraint; tooltip has < 3 positioning states |
| Table sorting | External sort library | `Array.prototype.sort` with spread copy | Single sort key (reject_rate desc), trivial implementation |
| SVG hit areas | SVG-specific mouse tracking libraries | Native SVG `<rect>` with `onMouseEnter`/`onMouseLeave` | Already in DOM, consistent with existing SVG patterns |

**Key insight:** This phase adds UI polish to existing SVG components. The no-build, no-library constraint means every visual feature must be achievable with Preact hooks + inline SVG. All needed patterns are already demonstrated in the codebase.

---

## Common Pitfalls

### Pitfall 1: SVG `onMouseLeave` fires on child elements

**What goes wrong:** When the tooltip div appears inside the SVG container, mouse movement from the `<rect>` to the tooltip div triggers `mouseleave` on the rect, causing the tooltip to flicker or disappear before the user can read it.

**Why it happens:** The tooltip div is a sibling in the DOM, not a child of the hit rect. `mouseleave` fires when the pointer exits the rect element's bounding box.

**How to avoid:** Place the tooltip div OUTSIDE the SVG element, as an absolutely-positioned sibling in the container div. The tooltip is never a mouse target itself (`pointer-events:none` on tooltip div). The `<rect>` covers the full column width — the pointer stays within a rect as long as the user moves horizontally.

**Warning signs:** Tooltip flickers on hover; tooltip disappears immediately when displayed.

---

### Pitfall 2: `HealthIndicatorData.run_ids` array shorter than `history`

**What goes wrong:** If a run has no `per_target` summary for the target, `indicatorHistory[name]` gets a value pushed but the run ID is not pushed to `indicatorRunIds[name]`. The two arrays become misaligned — tooltip shows wrong run ID for a data point.

**Why it happens:** The existing loop in `health-api.ts` has two nested `continue` conditions. Both must be mirrored for the run_ids push.

**How to avoid:** Push to `indicatorRunIds` in the exact same place as the push to `indicatorHistory`. They must be in the same branch, same loop iteration. Add a test that verifies `run_ids.length === history.length`.

**Warning signs:** Tooltip shows a run ID that doesn't match the value shown.

---

### Pitfall 3: ForgeResultCard null-state renders blank card

**What goes wrong:** `forge_result: null` (no self-repair run ever executed) renders a card with just a status icon but no meaningful text — looks broken.

**Why it happens:** The component checks `data.forge_result.status` without guarding for `forge_result === null`.

**How to avoid:** Explicit null state: when `forge_result === null`, render "No forge run recorded" text in the collapsed state. Keep the card visible so users know the feature exists.

**Warning signs:** Health page shows an empty card when first launched.

---

### Pitfall 4: Calibration table renders before data loads

**What goes wrong:** `CalibrationTable` renders an empty table with headers but no rows during the async fetch, giving the impression of missing data rather than loading state.

**Why it happens:** `calibration` state initializes to `[]` and the table renders immediately.

**How to avoid:** Pass a `loading` boolean prop (or use `null` as the unloaded sentinel). Show a "Loading..." row when `calibration === null`. Show "No feedback collected yet" only when `calibration` is an empty array after fetch completes.

**Warning signs:** Table flashes empty rows then populates.

---

### Pitfall 5: Multiple `useEffect` fetches are independent — error in one blocks nothing

**What goes wrong:** If `api.getForgeResults()` rejects, it could cause an unhandled rejection that interferes with the health data loading.

**Why it happens:** Forgetting to add a `.catch()` on the forge fetch. The existing `health.ts` uses individual `.catch(() => null)` on each target's health fetch.

**How to avoid:** Follow the existing pattern — wrap all secondary fetches in `.catch(() => fallbackValue)`. ForgeResultCard must render gracefully when `forgeData` is null (e.g., show "Unavailable").

---

## Code Examples

Verified patterns from existing codebase:

### Adding a state-driven expandable section (toast.ts signal pattern adapted)
```typescript
// Source: app/frontend/components/sparkline.ts (existing structure)
// + app/frontend/components/toast.ts (floating div pattern)
export function ForgeResultCard({ data }: { data: ForgeResultData | null }) {
  const [expanded, setExpanded] = useState(false)
  // collapsed: one line; expanded: + branch + details
  return html`
    <div style="position:relative;background:var(--panel);border:1px solid var(--border);border-radius:6px;padding:12px;margin:0 16px 16px;cursor:pointer;"
         onClick=${() => setExpanded(e => !e)}>
      ...collapsed content...
      ${expanded && html`...expanded content...`}
    </div>
  `
}
```

### SVG rect hit area with tooltip state
```typescript
// Source: coordinate math from app/frontend/components/sparkline.ts
const [activeIdx, setActiveIdx] = useState<number | null>(null)
const pointSpacing = values.length > 1 ? width / (values.length - 1) : width

// Inside SVG, after polyline:
${values.map((v, i) => {
  const x = (i / (values.length - 1)) * width
  const rectX = Math.max(0, x - pointSpacing / 2)
  const rectW = i === 0 || i === values.length - 1 ? pointSpacing / 2 : pointSpacing
  return html`
    <rect
      key=${i}
      x=${rectX} y=${0} width=${rectW} height=${height}
      fill="transparent"
      onMouseEnter=${() => setActiveIdx(i)}
      onMouseLeave=${() => setActiveIdx(null)}
    />
  `
})}

// Tooltip div OUTSIDE the SVG (sibling in container div):
${activeIdx !== null && html`
  <div style="position:absolute;top:-36px;left:${(activeIdx / (values.length - 1)) * width}px;
              transform:translateX(-50%);background:var(--panel);border:1px solid var(--border);
              border-radius:4px;padding:4px 8px;font-size:11px;color:var(--text);
              white-space:nowrap;pointer-events:none;z-index:10;">
    <div>${Math.round(values[activeIdx]! * 100)}%</div>
    ${runIds?.[activeIdx] && html`<div style="color:var(--muted);">${runIds[activeIdx]}</div>`}
  </div>
`}
```

### Calibration table row rendering with N-gate display
```typescript
// Source: CalibrationData type — app/shared/types.ts line 176
${sorted.map(row => html`
  <tr key=${row.indicator}>
    <td>${row.indicator}</td>
    <td>${row.current_threshold === null
      ? html`<span style="color:var(--muted);font-style:italic;">${row.threshold_null_reason ?? 'Accumulating data'}</span>`
      : `${Math.round(row.current_threshold * 100)}%`
    }</td>
    <td>${Math.round(row.reject_rate * 100)}%</td>
    <td>${row.total_feedback}</td>
  </tr>
`)}
```

### Adding getForgeResults() to api.ts
```typescript
// Source: api.ts existing get<T>() pattern
import type { ..., ForgeResultData } from '../../shared/types.ts'

// Inside api object:
getForgeResults(): Promise<ForgeResultData> {
  return get<ForgeResultData>('/api/forge/results')
},
```

### health-api.ts run_ids extraction
```typescript
// Source: app/server/routes/health-api.ts lines 21–35 (existing loop)
const indicatorRunIds: Record<string, string[]> = {}

// Inside the existing loop (same branch as indicatorHistory push):
if (!indicatorRunIds[name]) indicatorRunIds[name] = []
indicatorRunIds[name].push(runData.id)

// In the indicators build:
indicators[name] = {
  current: history[history.length - 1] ?? 0,
  trend,
  history,
  run_ids: indicatorRunIds[name] ?? [],
}
```

---

## Environment Availability

Step 2.6: SKIPPED — this phase is purely frontend code + one server-side data enrichment. No external tools, services, or CLIs beyond the already-running Bun+Hono server.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Bun test 1.3.9 |
| Config file | `app/bunfig.toml` (or none — `bun test` auto-discovers) |
| Quick run command | `cd app && bun test tests/server/health-api.test.ts` |
| Full suite command | `cd app && bun test` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| VIZ-03 (server side) | `GET /api/health/:target` response includes `run_ids` parallel to `history` on each indicator | unit | `bun test tests/server/health-api.test.ts` | ✅ (extend existing) |
| VIZ-03 (run_ids length) | `run_ids.length === history.length` for each indicator | unit | `bun test tests/server/health-api.test.ts` | ✅ (extend existing) |
| VIZ-02 (calibration table logic) | Rows with `total_feedback < 10` show threshold_null_reason; rows with >= 10 show formatted threshold | unit | `bun test tests/frontend/calibration-table.test.ts` | ❌ Wave 0 |
| VIZ-03 (sparkline tooltip logic) | Tooltip state activates at correct index; tooltip absent when runIds not provided | unit | `bun test tests/frontend/sparkline.test.ts` | ❌ Wave 0 |
| FORGE-01 (forge card logic) | relativeTime helper; statusColor returns correct CSS var for pass/fail/stale/null | unit | `bun test tests/frontend/forge-result-card.test.ts` | ❌ Wave 0 |

**Note on frontend tests:** The project's frontend testing pattern (as shown in `tests/frontend/action-card.test.ts`) is to extract pure helper functions and test them without a DOM. Preact render testing (jsdom/happy-dom) is NOT used — this is deliberate under the no-build constraint. Test files test the pure logic functions that components delegate to.

### Sampling Rate
- **Per task commit:** `cd app && bun test tests/server/health-api.test.ts`
- **Per wave merge:** `cd app && bun test`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `app/tests/frontend/sparkline.test.ts` — covers VIZ-03 tooltip logic (activeIdx computation, runId display guard)
- [ ] `app/tests/frontend/forge-result-card.test.ts` — covers FORGE-01 pure helpers (relativeTime, statusColor, null guard)
- [ ] `app/tests/frontend/calibration-table.test.ts` — covers VIZ-02 threshold cell logic (N-gate display, sort order, empty state)

*(Existing `tests/server/health-api.test.ts` only needs new test cases added — the file and infrastructure already exist.)*

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Fake 2-point sparkline history | Real per-run bucketed history (Phase 15) | Phase 15 (prior) | Sparklines now show meaningful curves — tooltip makes sense |
| No forge visibility | `GET /api/forge/results` endpoint (Phase 15) | Phase 15 (prior) | ForgeResultCard has real data to consume |
| Static sparkline (no interaction) | Hit-area rects + tooltip | This phase | First interactive SVG element in the codebase |

**Nothing deprecated in this phase.** LineChart component intentionally unchanged (deferred per CONTEXT.md).

---

## Open Questions

1. **Tooltip position for edge data points**
   - What we know: First and last data points are at x=0 and x=width — a centered tooltip would clip
   - What's unclear: How aggressive the clipping is at the 80px default sparkline width
   - Recommendation: Use simple edge guard (first point: tooltip anchored left; last point: anchored right). This is Claude's Discretion per CONTEXT.md.

2. **ForgeResultCard expand animation**
   - What we know: D-03 specifies click-to-expand behavior; animation is Claude's Discretion
   - What's unclear: Whether CSS `max-height` transition or instant toggle is preferred aesthetically
   - Recommendation: Use instant toggle (no animation) — consistent with the project's utilitarian aesthetic (no fade delays per CONTEXT.md specifics)

3. **Calibration table empty state wording**
   - What we know: Claude's Discretion per CONTEXT.md
   - Recommendation: "No feedback collected yet — run the pipeline to generate data." Single-row message spanning all columns.

---

## Sources

### Primary (HIGH confidence)
- Direct source code inspection: `app/frontend/components/sparkline.ts`, `app/frontend/components/toast.ts`, `app/frontend/pages/health.ts`, `app/frontend/lib/api.ts`
- Direct source code inspection: `app/server/routes/health-api.ts`, `app/server/routes/forge.ts`
- Direct source code inspection: `app/shared/types.ts` — CalibrationData (line 176), ForgeResultData (line 186), HealthIndicatorData (line 218)
- Direct source code inspection: `app/tests/frontend/action-card.test.ts` — establishes frontend test pattern (pure helper extraction, no DOM)
- Direct source code inspection: `app/tests/server/health-api.test.ts`, `app/tests/server/forge.test.ts` — establishes server test patterns

### Secondary (MEDIUM confidence)
- N/A — all findings are from direct codebase inspection, no external sources needed

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all existing libraries confirmed from `package.json` and vendor files
- Architecture: HIGH — patterns extracted directly from existing components, not inferred
- Pitfalls: HIGH — derived from reading the actual code paths that will be modified
- Test infrastructure: HIGH — `bun test` confirmed running (v1.3.9), existing test files read

**Research date:** 2026-03-26
**Valid until:** 2026-04-26 (stable codebase, no external dependencies)
