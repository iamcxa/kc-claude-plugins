# Architecture Patterns

**Domain:** Nightwatch Dashboard v4.0 — Flywheel Intelligence
**Researched:** 2026-03-25
**Milestone type:** Subsequent milestone — integration into existing server/worker/frontend

---

## Existing Architecture Map

Understanding the baseline before describing what changes.

### Server Layer (`app/server/`)

| File | Role |
|------|------|
| `index.ts` | Hono app, worker spawn, route registration |
| `ipc.ts` | Bun native IPC to worker (send/receive messages) |
| `routes/api.ts` | Targets, runs CRUD, worker state |
| `routes/feedback.ts` | POST /api/feedback, GET /api/feedback/:runId, GET /api/feedback/calibration |
| `routes/health-api.ts` | GET /api/health/:target — builds TargetHealthData from run history + calibration |
| `routes/outcomes.ts` | GET /api/outcomes, GET /api/outcomes/:id/status |
| `routes/stream.ts` | SSE /api/events (brief-ready, run:failed) |
| `services/feedback-store.ts` | Read/write nightwatch-feedback.yaml; `getCalibrationData()`, `appendFeedback()` |
| `services/run-store.ts` | Read/write per-run YAML files |
| `services/outcome-store.ts` | Read/write outcomes index |

### Worker Layer (`app/worker/`)

| File | Role |
|------|------|
| `executor.ts` | Orchestrates run lifecycle, sends IPC events |
| `feedback-collector.ts` | PR status, PR review, Linear status → FeedbackEntry |
| `scheduler.ts` | Interval-based run triggers |
| `worktree-manager.ts` | Git worktree isolation for runs |
| `policy.ts` | Signal confidence thresholds (reads calibration) |
| `auto-action.ts` | Autonomous action execution |

### Frontend Layer (`app/frontend/`)

| File | Role |
|------|------|
| `app.ts` | Router, SSE listener, healthData for sidebar |
| `pages/dashboard.ts` | Target list + run trigger |
| `pages/health.ts` | Health page — renders TargetHealthData with Sparkline + LineChart |
| `pages/runs.ts` | Run list + detail with ActionCard + BaselineCard |
| `pages/outcomes.ts` | Outcome list + detail |
| `components/sparkline.ts` | SVG inline sparkline (width=80, height=20, color by direction) |
| `components/line-chart.ts` | SVG line chart with axes (width=240, height=80, Y=0..1 reject rate scale) |
| `components/action-card.ts` | Per-signal card with feedback buttons, outcome badge |
| `components/baseline-card.ts` | Indicator baselines from run summary |
| `lib/api.ts` | Typed fetch wrappers for all routes |

### Shared Types (`app/shared/types.ts`)

Key types relevant to v4.0:
- `FeedbackEntry` — signal_id, target, run_id, verdict, source, submitted_at
- `CalibrationData` — indicator, total_feedback, reject_count, reject_rate, current_threshold
- `IndicatorBaseline` — value, measurement, previous_value, trend
- `TargetHealthData` — target, health, indicators (Record<string, HealthIndicatorData>), reject_rate, per_indicator_rates, acceptance_rate, runs_analyzed
- `HealthIndicatorData` — current, trend, history (number[])

### Data Files (runtime, not in repo)

| Path | Contents |
|------|----------|
| `~/.claude/kc-plugins-config/nightwatch-feedback.yaml` | FeedbackStore (explicit_feedback, pr_feedback, linear_feedback, slack_feedback, pr_review_feedback) |
| `~/.claude/kc-plugins-config/nightwatch-targets.yaml` | Target definitions with indicators |
| `app/runs/` | Per-run YAML with summary + log |

---

## v4.0 Feature Set and Integration Points

The milestone adds five feature areas. Each is analyzed below: what exists, what's missing, where it plugs in.

### Feature 1: Feedback Trend Visualization

**What exists:**
- `GET /api/feedback/calibration` returns `CalibrationData[]` — per-indicator reject rate, but no time series
- `health-api.ts` builds `per_indicator_rates` with history arrays, but only `[0, current_rate]` (two-point fake history, not real time series)
- `LineChart` component is already wired in `pages/health.ts` rendering reject rate over "runs"
- The YAML store is append-only; timestamps are in `FeedbackEntry.submitted_at`

**What's missing:**
- Real time-series reject rates: need to bucket feedback entries by run or by week
- The current `getCalibrationData()` aggregates all-time totals — no per-period windowing
- No API endpoint that returns reject rate time series

**Integration plan:**

Server: Add `GET /api/feedback/trends` to `routes/feedback.ts`. Query `nightwatch-feedback.yaml`, bucket `FeedbackEntry[]` by `run_id` (using run order from run-store), compute cumulative reject rate at each run boundary. Returns `Array<{ run_id: string; reject_rate: number; accepted: number; rejected: number }>` per indicator.

Service: Add `getFeedbackTrends(indicatorFilter?: string)` to `feedback-store.ts`. Group by signal_id prefix (the indicator namespace already present in `signal_id.split(':')[0]`). Sorts by `submitted_at` ascending for chronological ordering.

Frontend: The existing `LineChart` component needs no changes — it accepts `values: number[]` and labels. `pages/health.ts` currently calls `api.getCalibration()` indirectly through `GET /api/health/:target`. Add `api.getFeedbackTrends()` call in `health.ts` to populate real history arrays instead of the `[0, current_rate]` stub.

**New additions:**
- `routes/feedback.ts`: one new GET route (`/api/feedback/trends`)
- `services/feedback-store.ts`: one new function (`getFeedbackTrends`)
- `lib/api.ts`: one new method (`getFeedbackTrends`)
- `pages/health.ts`: replace stub history with real trend data

**No new components or routes files required.**

---

### Feature 2: Auto-Calibration Display

**What exists:**
- `getCalibrationData()` already computes `current_threshold` per indicator using the formula: `0.5 + (rejectRate - 0.5) * 0.5`, clamped 0.1..0.9
- `GET /api/feedback/calibration` returns this data
- `api.getCalibration()` is defined but not rendered anywhere in the frontend
- `pages/health.ts` never calls `api.getCalibration()` directly — it reads `per_indicator_rates` from the health endpoint, which itself calls `getCalibrationData()`

**What's missing:**
- No UI rendering calibration thresholds per indicator
- No indication of whether a threshold was auto-adjusted or is at baseline (0.5)
- `policy.ts` in the worker reads thresholds at run time — the connection between calibration data and actual pipeline behavior is invisible to users

**Integration plan:**

Frontend only — no new server routes needed (data already available at `/api/feedback/calibration`).

Add a `CalibrationTable` component: renders `CalibrationData[]` as a table with columns: Indicator, Feedback Count, Reject Rate (%), Threshold (%), Status (raised/lowered/baseline). "Baseline" = threshold at 0.5; "raised" = threshold > 0.5 (high reject rate → stricter); "lowered" = threshold < 0.5.

Wire into `pages/health.ts`: call `api.getCalibration()` alongside the health endpoint calls. Render `CalibrationTable` below the reject rate charts.

**New additions:**
- `components/calibration-table.ts`: new component
- `pages/health.ts`: add `getCalibration()` fetch + render `CalibrationTable`

**No server changes required.**

---

### Feature 3: Signal Prioritization Display

**What exists:**
- `RunSummaryAction` has `assessment.confidence` (high/medium/low), `assessment.closer_to_north_star` (yes/no/uncertain), and `indicator`
- `ActionCard` already shows confidence as a colored badge
- No sorting of actions by confidence + north-star alignment in the UI
- No aggregate view of "which signals are highest priority across runs"

**What's missing:**
- Actions in `pages/runs.ts` render in document order from the summary — no priority sort
- No cross-run signal prioritization dashboard

**Integration plan — two sub-features:**

**3a. Sort actions within a run by priority.**
Modify `pages/runs.ts` only. Before rendering action cards, sort `targetData.actions` by: (1) `closer_to_north_star === 'yes'` first, (2) `confidence === 'high'` > `'medium'` > `'low'`. This is pure frontend change, no API touch.

**3b. Cross-run signal priority view.**
New route: `GET /api/signals/priority` in a new `routes/signals.ts`. Aggregates the last N runs' actions (from run-store), deduplicated by `signal_id`, ranked by: high-confidence + north-star-aligned actions that appear in multiple runs (recurring unresolved signals). Returns `Array<{ signal_id: string; indicator: string; summary: string; runs: number; confidence: string; north_star: string }>`.

New frontend component: `SignalPriorityList` — renders the ranked list with indicator, confidence badge, "seen N times" count, run links. Wire into `pages/health.ts` as a new section "Top Unresolved Signals" or add as a new tab/section within the runs page.

**New additions:**
- `routes/signals.ts`: new route file (`GET /api/signals/priority`)
- `server/index.ts`: register `signalsRoutes`
- `components/signal-priority-list.ts`: new component
- `lib/api.ts`: `getSignalPriority()` method
- `pages/runs.ts`: sort actions before render (no new file)
- `pages/health.ts` or new page: render `SignalPriorityList`

---

### Feature 4: Forge Results Display

**What exists:**
- Run summaries in `RunSummary.per_target` contain `actions` (including forge-fix actions in nightwatch's self-repair mode)
- `ActionCard` shows action type as a badge — forge-fix PRs already appear if the run was self-repair mode
- No dedicated forge results section — forge fixes are mixed with regular signals

**What's missing:**
- No filtering of actions by type in the run detail view
- No forge-specific result aggregation (how many forge fixes this week, pass rate)
- Forge check output (structural PASS/FAIL per skill/agent) is in the log, not in a structured summary field

**Integration plan:**

**4a. Forge results in run detail.**
`pages/runs.ts`: add a filter button or tab inside the run detail view to show only `action.type === 'quick-fix'` actions from self-repair runs. The `mode === 'self-repair'` is already in the `Run` type — use it to show a "Self-Repair Run" label and group forge actions separately.

No new routes needed. Filter is pure frontend.

**4b. Forge summary in health page.**
`services/run-store.ts` or `routes/health-api.ts`: when computing `TargetHealthData`, add `forge_pass_rate?: number` — proportion of self-repair runs where forge completed without FAIL items. Requires reading run summaries for runs where `mode === 'self-repair'`.

**Recommendation:** Keep forge results display lightweight in v4.0 — filter in `pages/runs.ts` (action type filter) + add a summary stat in `TargetHealthData`. Full forge analytics is v5.0+ territory.

**New additions:**
- `pages/runs.ts`: type filter (self-repair mode label + quick-fix filter)
- `shared/types.ts`: optional `forge_pass_count?: number; forge_fail_count?: number` on `TargetHealthData`
- `routes/health-api.ts`: compute forge pass/fail counts from self-repair runs

---

### Feature 5: Indicator Sparklines (Enhanced)

**What exists:**
- `Sparkline` component: accepts `values: number[]`, SVG 80x20, color by direction (up=green, down=red, flat=muted)
- Currently used in `pages/health.ts` for each `HealthIndicatorData.history`
- History comes from `health-api.ts` which collects `indicator_baseline.value` across last 10 runs

**What's missing:**
- Sparklines are already implemented and working. The gap is data richness: only 10 runs of history
- No target value line on sparkline (indicator target from `Target.indicators[].target`)
- No hover tooltip showing run date + value

**Integration plan:**

**5a. Show target line on sparkline.**
`Sparkline` component: add optional `target?: number` prop. If provided, render a horizontal dashed line at the normalized Y position corresponding to the target value. This gives visual context — "this is where we want to be."

The target value comes from `Target.indicators[].target` (already in the type). Pass from `pages/health.ts` which already has `Target[]` in state.

**5b. Extend history window.**
`health-api.ts`: change `const last10 = allRuns.slice(0, 10)` to `slice(0, 20)`. No type changes needed; `HealthIndicatorData.history` is already `number[]`.

**5c. Tooltip on sparkline (optional, scope risk).**
HTML `title` attribute on the SVG element for simple hover: `title="Run N: value X"`. Avoids custom tooltip component complexity. Sufficient for v4.0.

**New additions:**
- `components/sparkline.ts`: add optional `target?: number` prop + horizontal target line
- `routes/health-api.ts`: bump history window from 10 to 20 runs
- `pages/health.ts`: pass `target` prop from `Target.indicators` to each `Sparkline`

---

## Component Boundaries (Post-v4.0)

```
Server
├── routes/
│   ├── feedback.ts          MODIFIED: add /api/feedback/trends
│   ├── health-api.ts        MODIFIED: add forge stats, extend history to 20
│   ├── signals.ts           NEW: /api/signals/priority
│   └── ... (unchanged: api, outcomes, stream, config, mcp, schedule, chat)
├── services/
│   └── feedback-store.ts    MODIFIED: add getFeedbackTrends()
└── index.ts                 MODIFIED: register signalsRoutes

Worker
└── ... (unchanged — no new worker features in v4.0)

Frontend
├── pages/
│   ├── health.ts            MODIFIED: getFeedbackTrends(), getCalibration(), SignalPriorityList, CalibrationTable
│   └── runs.ts              MODIFIED: sort actions by priority, self-repair run label
├── components/
│   ├── sparkline.ts         MODIFIED: target prop + horizontal target line
│   ├── calibration-table.ts NEW
│   └── signal-priority-list.ts NEW
└── lib/
    └── api.ts               MODIFIED: getFeedbackTrends(), getSignalPriority()

Shared
└── types.ts                 MODIFIED: forge stats on TargetHealthData (optional fields)
```

---

## Data Flow Changes

### Feedback Trend Flow (new)

```
nightwatch-feedback.yaml
    → getFeedbackTrends() (feedback-store.ts)
    → GET /api/feedback/trends
    → api.getFeedbackTrends() (frontend api.ts)
    → pages/health.ts (replace [0, current_rate] stub)
    → LineChart (existing component, no change)
```

### Calibration Display Flow (new)

```
nightwatch-feedback.yaml
    → getCalibrationData() (existing, already in feedback-store.ts)
    → GET /api/feedback/calibration (existing route)
    → api.getCalibration() (existing in api.ts, not yet called from health page)
    → CalibrationTable (new component)
    → pages/health.ts
```

### Signal Priority Flow (new)

```
app/runs/*.yaml (run history)
    → run-store.ts (existing listRuns + getRun)
    → GET /api/signals/priority (new route in signals.ts)
    → api.getSignalPriority() (new in api.ts)
    → SignalPriorityList (new component)
    → pages/health.ts
```

### Sparkline Target Line Flow (modified)

```
nightwatch-targets.yaml
    → GET /api/targets (existing)
    → pages/health.ts (already has targets in state)
    → Sparkline target prop (prop added to existing component)
```

---

## Suggested Build Order

Build order follows data dependencies — server must exist before frontend calls it, simpler changes before complex ones.

### Step 1: Extend History Window (30 min)
**Files:** `routes/health-api.ts` (last10 → last20)
**Why first:** Zero risk change. Immediately improves existing sparklines with more data. No new types, no frontend changes.

### Step 2: Sparkline Target Line (45 min)
**Files:** `components/sparkline.ts`, `pages/health.ts`
**Why second:** Self-contained component enhancement. Existing target data is already in `Target.indicators[].target`. No new API calls.

### Step 3: Feedback Trend Server Work (60 min)
**Files:** `services/feedback-store.ts` (add `getFeedbackTrends`), `routes/feedback.ts` (add GET /api/feedback/trends), `lib/api.ts` (add `getFeedbackTrends`)
**Why third:** Server-side before frontend. `getFeedbackTrends` can be tested independently with curl before wiring frontend.

### Step 4: Feedback Trend Frontend (45 min)
**Files:** `pages/health.ts` (replace stub history arrays with real trend data, call `api.getFeedbackTrends`)
**Why fourth:** Depends on Step 3 server work. Replaces fake `[0, current_rate]` two-point history with real time series.

### Step 5: Calibration Table (45 min)
**Files:** `components/calibration-table.ts` (new), `pages/health.ts` (add `api.getCalibration()` call + render)
**Why fifth:** Pure frontend, no new server routes. `api.getCalibration()` already exists. Low risk.

### Step 6: Signal Priority Server Work (60 min)
**Files:** `routes/signals.ts` (new), `server/index.ts` (register route), `lib/api.ts` (add `getSignalPriority`)
**Why sixth:** New route file, moderately complex aggregation logic. Complete server side before wiring UI.

### Step 7: Signal Priority Frontend (45 min)
**Files:** `components/signal-priority-list.ts` (new), `pages/health.ts` (add section)
**Why seventh:** Depends on Step 6 server. Straightforward list rendering.

### Step 8: Forge Results Display (45 min)
**Files:** `shared/types.ts` (optional forge stats on TargetHealthData), `routes/health-api.ts` (compute forge pass/fail), `pages/runs.ts` (sort by priority, self-repair label)
**Why last:** Touches the most files but changes are additive (optional fields, frontend sort). Runs page sort is independent of all above.

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: New Page for Each Feature
**What:** Creating a new "Flywheel" or "Analytics" page
**Why bad:** The Health page already fetches targets + health data. Adding a second page that fetches the same data wastes API calls and fragments UX. Users would need to navigate between pages to compare calibration vs indicator trends.
**Instead:** Extend `pages/health.ts` with new sections. If the page gets too long, add a section toggle (expand/collapse) rather than a new page.

### Anti-Pattern 2: Polling /api/signals/priority on 5-second interval
**What:** Using `usePoll` with a short interval for the signal priority list
**Why bad:** Signal priority is derived from historical run data — it doesn't change during a run. Polling wastes requests.
**Instead:** Load once on mount (like the outcomes page's one-time load), re-fetch only after `brief-ready` SSE event (which signals a new run completed). Wire `refreshTrigger` from `use-poll.ts` as a dependency.

### Anti-Pattern 3: Moving CalibrationData computation to the worker
**What:** Having the worker compute and write calibration results to a new YAML file
**Why bad:** Calibration is a read-time aggregation over feedback entries. Making it a write-time artifact creates staleness and duplicates logic. The worker already writes enough YAML.
**Instead:** Keep `getCalibrationData()` as an on-demand aggregation in `feedback-store.ts`. It's fast (single file read + in-memory grouping). Cache in server memory if performance becomes an issue (not expected at current scale).

### Anti-Pattern 4: Breaking Sparkline's existing API
**What:** Changing `Sparkline`'s `values` prop contract or making `target` required
**Why bad:** `Sparkline` is used in multiple places. Breaking changes require updating all call sites.
**Instead:** Make `target` optional (`target?: number`). Default behavior (no target line) is identical to current.

### Anti-Pattern 5: Fetching all runs for signal priority on every health page load
**What:** `GET /api/signals/priority` scanning all historical runs on every request
**Why bad:** Run history grows unboundedly. At 500+ runs this becomes slow.
**Instead:** Limit to last 30 runs in `routes/signals.ts`. Document this limit explicitly. If deeper history is needed later, add pagination or a `?window=N` query param.

---

## Scalability Considerations

| Concern | Current state | v4.0 change | Risk |
|---------|--------------|-------------|------|
| nightwatch-feedback.yaml growth | One file, append-only, YAML parse on every request | getFeedbackTrends adds one more full-file parse | LOW — file stays small (hundreds of entries) |
| Run store reads for signal priority | Not done currently | New: reads last 30 run YAMLs | LOW — 30 small YAML files, reads are parallel |
| Health page render complexity | 1 API call per target + calibration | 2 additional API calls (trends, priority) | LOW — calls are parallel with Promise.all |
| Sparkline SVG DOM | 80x20 SVG per indicator | Adding one `<line>` element for target | Negligible |

---

## Sources

- Direct code inspection of `app/server/`, `app/worker/`, `app/frontend/`, `app/shared/` (2026-03-25)
- `shared/types.ts`: FeedbackEntry, CalibrationData, TargetHealthData, IndicatorBaseline shapes
- `services/feedback-store.ts`: existing aggregation logic and YAML schema
- `routes/health-api.ts`: existing history construction (10-run window, fake two-point reject rate history)
- `pages/health.ts`: existing render logic for sparklines and line charts
- `reference/ROADMAP.md`: v0.5 feature intentions (improvement-log analytics, reject ratio trends) — confirms this milestone aligns with planned direction
