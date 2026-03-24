# Stack Research

**Domain:** Bun-native web dashboard — v4.0 Flywheel Intelligence additions
**Researched:** 2026-03-25 (v4.0 addendum)
**Confidence:** HIGH (findings based on direct codebase inspection + ESM availability verification)

---

> **Scope:** This document covers ONLY what v4.0 adds for: feedback trend visualization, auto-calibration, signal prioritization, forge results display, and per-indicator sparklines. The v1.0–v3.0 stack (Bun, Hono, Preact/HTM, Zod, yaml, MCP SDK, toast, Notification API) is validated and unchanged.

---

## v4.0 Stack Additions

**Summary: Zero new npm packages. Zero new vendor ESM files.** All five v4.0 features are implementable with the existing stack, extending what is already shipped.

| Feature | Stack Needed | Status |
|---------|-------------|--------|
| Feedback trend visualization | Enhanced `LineChart` + `AreaChart` SVG components | Extend existing `line-chart.ts` |
| Auto-calibration algorithm | `feedback-store.ts` extension (EMA + YAML persistence) | Pure TypeScript, zero deps |
| Signal prioritization scoring | New `priority-scorer.ts` utility | Pure TypeScript, zero deps |
| Forge results display | Extend `/api/config/warnings` → new `ForgeResultCard` component | Route already exists |
| Per-indicator sparklines | Enhanced `Sparkline` component (gradient, area fill) | Extend existing `sparkline.ts` |

---

## Why No Charting Library

The project has a hard no-build constraint (Preact + HTM, vendor-only ESM). The charting library options fail this constraint:

| Library | Problem | Verdict |
|---------|---------|---------|
| **Chart.js 4.x** | Depends on `@kurkle/color` bare specifier — requires two-file vendor dance + import map update; Canvas-based, doesn't compose with SVG components | Reject |
| **uPlot 1.6.32** | Canvas 2D + DOM manipulation (creates its own div container, CSS classes, legend elements) — incompatible with Preact's declarative render model; ~52KB vendored | Reject |
| **D3.js** | 500KB+ even tree-shaken; ESM submodule vendoring requires 8+ separate files; CSS class mutations incompatible with HTM | Reject |
| **Recharts / Victory** | React-native — incompatible with Preact without compat layer (introduces full React bundle) | Reject |

**The project already ships the right primitives.** `Sparkline` (80x20 SVG polyline) and `LineChart` (240x80 SVG with axes) exist in `frontend/components/`. They render inline SVG via HTM, compose with Preact signals, and need zero wiring. v4.0 extends them with area fill and gradient — browser-native SVG `<path>`, `<defs>`, `<linearGradient>` — no library required.

**Confidence:** HIGH — verified uPlot ESM (52KB, Canvas-based, incompatible); verified Chart.js bare-specifier problem in GitHub issue #11592; existing SVG components confirmed functional in health page.

---

## Feature Implementation Details

### 1. Feedback Trend Visualization

**What it needs:** Accept/reject rate over time, per-target charts.

**Existing pieces:**
- `LineChart` in `frontend/components/line-chart.ts` renders a 240x80 SVG with axes — already used in `health.ts` page
- `per_indicator_rates.history: number[]` already populated in `health-api.ts`
- `TargetHealthData.per_indicator_rates` already carries history arrays

**What to add/extend:**
- `LineChart` needs a second series (accept rate = 1 - reject rate) — add `series: Array<{ values: number[], color: string, label: string }>` prop overload
- Add `AreaChart` variant with SVG `<path>` fill (closed polygon below the line) — reuses same coordinate math, adds a `polygon` element or closes path with `L ${xMax},${yMax} L ${xMin},${yMax} Z`
- New `FeedbackTrendChart` component wrapping multi-series LineChart — calls `api.getCalibration()`, renders accept vs. reject over time per indicator

**No new dependencies.** SVG area fill is `<path d="..." fill="..." opacity="0.15" />` — fully composable with existing `html` tagged template literal approach.

### 2. Auto-Calibration Algorithm

**What exists:** `getCalibrationData()` in `feedback-store.ts` computes a one-shot threshold:
```
threshold = clamp(0.1, 0.9, 0.5 + (rejectRate - 0.5) × 0.5)
```
This is stateless — recalculated from scratch on every call.

**What v4.0 adds:**

**Exponential Moving Average (EMA) smoothing** — prevents threshold whiplash when a single rejected signal temporarily spikes the rate. Formula:
```typescript
// alpha = 0.3 is a standard EMA smoothing factor: responsive but not twitchy
const ema = (current: number, previous: number, alpha = 0.3) =>
  alpha * current + (1 - alpha) * previous
```

**Time-windowed recalibration** — use only feedback from the last 30 days for threshold calculation. Older feedback informs trend display but not threshold decisions. Implementation: filter `FeedbackEntry[]` by `submitted_at >= now - 30d` before computing rates.

**Threshold persistence** — calibrated thresholds must survive server restarts. Write to `nightwatch-feedback.yaml` under a `calibration_state:` key:
```yaml
calibration_state:
  last_computed: "2026-03-25T..."
  thresholds:
    pipeline-friction: 0.72
    flow-coverage: 0.85
```
Use existing `writeYamlFile` from `yaml-store.ts`. Add `getPersistedThreshold(indicator)` / `persistThreshold(indicator, value)` helpers to `feedback-store.ts`.

**New API endpoint:** `POST /api/feedback/calibrate` — triggers recalibration, writes state, returns updated `CalibrationData[]`. Called by the dashboard's "Recalibrate" button.

**No new dependencies.** Pure TypeScript arithmetic + existing `yaml` package for persistence.

### 3. Signal Prioritization

**What it needs:** Rank signals by confidence × historical success so the nightwatch pipeline acts on high-value signals first.

**Algorithm (pure TypeScript):**
```typescript
interface SignalScore {
  signal_id: string
  indicator: string
  confidence: 'high' | 'medium' | 'low'
  priority_score: number  // 0.0–1.0
}

const CONFIDENCE_WEIGHT = { high: 1.0, medium: 0.6, low: 0.3 }

function scoreSignal(
  signal: { signal_id: string; indicator: string; confidence: 'high' | 'medium' | 'low' },
  calibration: Map<string, CalibrationData>,
  recencyBonus: number  // 0.0–0.2 based on time since last action
): number {
  const cal = calibration.get(signal.indicator)
  const historicalSuccess = cal ? (1 - cal.reject_rate) : 0.5  // default 50% if no data
  const confidenceWeight = CONFIDENCE_WEIGHT[signal.confidence]
  return Math.min(1.0, confidenceWeight * historicalSuccess + recencyBonus)
}
```

**Placement:** New file `server/services/priority-scorer.ts`. The executor reads calibration at Phase 3 (after confidence filter) and re-sorts the filtered signal list by priority score descending before the per-plugin cap applies.

**Dashboard display:** `CalibrationData[]` from `api.getCalibration()` already contains `reject_rate` and `current_threshold`. A new `SignalPriorityTable` component renders indicator name, reject rate, derived success rate, and current threshold as a sortable table — no API changes needed.

**No new dependencies.** Pure TypeScript. Calibration data already fetched by health endpoint.

### 4. Forge Results Display

**What exists:**
- `nightwatch-self-repair.yaml` already has `forge_result: { status: 'pass'|'fail', branch: string|null, details: string }`
- `/api/config/warnings` route reads this YAML and returns it as `{ warnings: Record<string, unknown> }`
- Config page already calls `api.getConfigWarnings()` and processes `config_fixes`

**What v4.0 adds:**

**`ForgeResultCard` component** in `frontend/components/forge-result-card.ts`:
```typescript
// Props derived from nightwatch-self-repair.yaml forge_result field
interface ForgeResultProps {
  status: 'pass' | 'fail' | null
  branch: string | null
  details: string | null
  runDate: string | null
}
```

Renders a compact card: status badge (green PASS / red FAIL), run date, details text, and a link to the branch PR if `branch` is non-null.

**Placement:** Add to the Health page (`health.ts`) as a sidebar panel, or add a "Last Self-Repair" section to the Config page — where `config_warnings` already displays. Config page is the natural home since self-repair data comes from the same YAML.

**API: no changes.** `/api/config/warnings` already returns the full YAML. The component reads `warnings.forge_result` from the existing response.

**No new dependencies.**

### 5. Per-Indicator Sparkline Enhancement

**What exists:** `Sparkline` in `frontend/components/sparkline.ts` renders an 80x20 SVG polyline with color coding (green/red/muted based on trend direction).

**What v4.0 adds:**
- **Area fill** — close the polyline into a polygon and add a semi-transparent fill (opacity 0.1) matching the line color. Use SVG `<polygon>` with the same points plus two baseline corners, or convert to `<path>` for a proper filled area.
- **Tooltip on hover** — native SVG `<title>` element as the simplest no-JS approach (browser renders tooltip on mouse over). Example: `html\`<title>${values.join(', ')}</title>\`` inside the `<svg>`. For richer tooltips, Preact `useState` + `onMouseMove` handler + absolute-positioned div — all within existing patterns.
- **Min/max annotation** — small text labels at the peak and trough points. Optional prop `showExtremes?: boolean`.

**No new dependencies.** All SVG primitives — `<path>`, `<polygon>`, `<title>`, `<text>` — are browser-native and compose cleanly with the existing `html` tagged template literal.

---

## What NOT to Add

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| **uPlot** | Canvas-based DOM mutation — incompatible with Preact declarative render; 52KB vendor file for charts we can build in 50 lines of SVG | Extend existing `LineChart`/`Sparkline` |
| **Chart.js** | Requires `@kurkle/color` dependency (bare specifier problem in import maps); Canvas-based | Extend existing SVG components |
| **D3.js** | 500KB+ even tree-shaken; DOM mutation model fights Preact; ESM submodule vendoring is 8+ files | SVG path math is 20 lines of TypeScript |
| **date-fns / dayjs** | Full date formatting library not needed for 30-day window filter | `new Date(entry.submitted_at) > new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)` — one line |
| **Lodash / Ramda** | Not needed for EMA formula or simple sort/filter operations | Native `Array.prototype.sort`, `filter`, `reduce` |
| **React charting libraries (Recharts, Victory)** | Require React compat layer — adds full React bundle, breaks no-build constraint | — |

---

## Integration Points with Existing Vendor ESM Pattern

The existing `index.html` import map:
```json
{
  "imports": {
    "preact": "/vendor/preact.module.js",
    "preact/hooks": "/vendor/preact-hooks.module.js",
    "htm/preact": "/vendor/htm.module.js",
    "@preact/signals": "/vendor/signals.module.js"
  }
}
```

**v4.0 adds nothing to this import map.** No new vendor files needed. All new components follow the same pattern:

```typescript
// New component — same import pattern as all existing components
import { html } from 'htm/preact'
import { useState } from 'preact/hooks'
import type { CalibrationData } from '../../shared/types.ts'
```

SVG inline rendering in HTM works natively — Preact passes SVG attributes as-written per official Preact docs. The `<linearGradient>`, `<defs>`, `<polygon>`, `<path>` elements are all in scope without any import.

---

## New Types Needed in `shared/types.ts`

```typescript
// v4.0 additions

// Calibration persistence (written to nightwatch-feedback.yaml)
export interface CalibrationState {
  last_computed: string  // ISO timestamp
  thresholds: Record<string, number>  // indicator → adjusted threshold
}

// Forge result from nightwatch-self-repair.yaml
export interface ForgeResult {
  status: 'pass' | 'fail'
  branch: string | null
  details: string
}

// Extended self-repair YAML shape (superset of existing config_warnings return)
export interface SelfRepairData {
  run_date?: string
  forge_result?: ForgeResult
  config_warnings?: Array<{ target: string; field: string; error: string; suggestion: string }>
  config_fixes?: Array<{ message: string }>
}

// Signal priority score (computed, not persisted)
export interface SignalPriorityScore {
  indicator: string
  confidence_weight: number
  historical_success_rate: number
  priority_score: number
}
```

---

## New Files (No New Dependencies)

| File | Purpose |
|------|---------|
| `frontend/components/forge-result-card.ts` | Compact forge status display — reads from existing `/api/config/warnings` |
| `frontend/components/feedback-trend-chart.ts` | Multi-series accept/reject chart — extends `LineChart` pattern |
| `frontend/components/area-chart.ts` | SVG area chart with gradient fill — standalone component |
| `server/services/priority-scorer.ts` | Signal priority scoring function |
| New export `frontend/components/sparkline.ts` | Extend existing: area fill + tooltip (backward compatible via optional props) |

---

## Backend API Additions (Minimal Surface)

| Endpoint | Method | Purpose | Source Data |
|----------|--------|---------|-------------|
| `/api/feedback/calibrate` | POST | Trigger EMA recalibration + persist thresholds | `feedback-store.ts` + `nightwatch-feedback.yaml` |
| `/api/feedback/calibration` | GET (exists) | Now returns `current_threshold` from persisted state (not recomputed) | `nightwatch-feedback.yaml` calibration_state |
| `/api/config/warnings` | GET (exists) | Already returns `forge_result` field — no change needed | `nightwatch-self-repair.yaml` |

The only new endpoint is `POST /api/feedback/calibrate`. Everything else extends existing routes.

---

## Calibration Algorithm: Confidence

The EMA-based threshold calibration is a well-understood adaptive control technique:
- EMA with α=0.3 is standard for moderate responsiveness (roughly 10-run lag before new patterns dominate)
- 30-day rolling window matches the project's signal cooldown period — signals expire from feedback consideration at the same cadence they expire from the improvement log
- Clamping to [0.1, 0.9] prevents degenerate states (always-reject or always-accept)

The current formula (`0.5 + (rejectRate - 0.5) × 0.5`) is correct but needs the EMA layer for stability. Adding EMA is a one-function change to `feedback-store.ts` — no schema changes to `CalibrationData`.

**Confidence:** HIGH — algorithm is pure arithmetic, no external verification needed.

---

## Sources

- Direct codebase inspection: `frontend/components/sparkline.ts`, `frontend/components/line-chart.ts`, `frontend/pages/health.ts`, `server/services/feedback-store.ts`, `server/routes/health-api.ts`, `frontend/lib/api.ts`, `shared/types.ts`
- uPlot ESM verification: `https://esm.sh/uplot@1.6.32` — confirmed Canvas-based, ~52KB, incompatible with SVG approach
- Chart.js bare specifier issue: [GitHub issue #11592](https://github.com/chartjs/Chart.js/issues/11592) — confirmed `@kurkle/color` import map problem
- Preact SVG handling: [Preact docs](https://preactjs.com/guide/v10/differences-to-react/) — confirmed passes SVG attributes as-written, no special handling needed
- Existing vendor files: `preact@10.23.1`, `@preact/signals@1.3.0`, `htm@3.1.1` — no version updates needed

---
*Stack research for: Nightwatch Dashboard v4.0 Flywheel Intelligence*
*Researched: 2026-03-25*
