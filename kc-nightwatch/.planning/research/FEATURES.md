# Feature Research

**Domain:** Nightwatch Dashboard v4.0 — Flywheel Intelligence
**Researched:** 2026-03-25
**Confidence:** HIGH (codebase direct inspection + PROJECT.md + pattern research)

---

## Context

This is a v4.0 research pass. v3.0 shipped worktree isolation, external feedback sources (Slack reactions + PR review comments), 3-state verdict (accepted/rejected/uncertain), dashboard source labels on ActionCard, and CalibrationData per-indicator reject rates.

**What v4.0 adds:**

- **Feedback trend visualization** — reject/accept rate over time is currently a single static value per indicator; v4 makes the trend visible as a proper time series across runs
- **Auto-calibration** — `current_threshold` is computed on every `/api/feedback/calibration` call using a static formula; v4 makes this threshold actively propagate back into the nightwatch pipeline as a tuning signal
- **Signal prioritization** — signals are currently filtered by confidence (high/medium/low) with fixed thresholds; v4 ranks signals by `confidence × historical_success_rate` so the most proven signal types surface first
- **Forge results display** — `nightwatch-self-repair.yaml` already has a `forge_result` block with `status/branch/details`; this data is not currently surfaced in the dashboard at all
- **Per-indicator trend sparklines** — health page already has sparklines for indicator values (the `Sparkline` component + `HealthIndicatorData.history[]`); the ask is to enrich these or add rejection-rate sparklines alongside indicator value sparklines

**Existing data and endpoints (carry-forward — already built):**

- `FeedbackEntry` with `submitted_at`, `source`, `verdict`, `signal_id` — the raw time-series data exists in `feedback.yaml`
- `CalibrationData` with `reject_rate`, `total_feedback`, `current_threshold` per indicator — computed on demand in `feedback-store.ts`
- `GET /api/feedback/calibration` — returns `CalibrationData[]`, no time dimension yet
- `GET /api/health/:target` — returns `TargetHealthData` with `indicators[].history[]` (chronological value array across last 10 runs) and `per_indicator_rates` (static rate + stub `[0, rate]` history — currently fake)
- `Sparkline` component (80x20 SVG polyline, color-coded by direction) — exists and in use
- `LineChart` component (240x80 SVG with axes, y=0-1, renders reject rate history) — exists but fed fake `[0, rate]` stub data
- `nightwatch-self-repair.yaml` with `forge_result: { status, branch, details }` — file exists, no API endpoint reads it

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features where the system clearly has the data and the absence is a visible gap — the dashboard shows a number where a trend belongs, or reads from a file it never exposes.

| Feature | Why Expected | Complexity | Depends On |
|---------|--------------|------------|------------|
| Feedback trend over time (accept/reject rate time series per indicator) | Health page shows a single static reject rate per indicator. The underlying `FeedbackEntry[]` records already have `submitted_at` timestamps. Showing a rate-per-run chart — not just "40% reject rate overall" — is the obvious next step for a system that explicitly tracks learning over time. | MEDIUM | `GET /api/health/:target` currently returns fake `[0, rate]` for `per_indicator_rates[].history` — replace with real per-run bucketed rates derived from `FeedbackEntry.run_id` correlation to run dates. No new schema changes needed. |
| Forge results visible in dashboard | `nightwatch-self-repair.yaml` contains `forge_result: { status: pass/fail, branch, details }` after every self-repair run. This is health-relevant data (is NW's own plugin quality degrading?) that is completely invisible in the UI. Users who trigger self-repair have no way to see the outcome without reading the raw YAML. | LOW | New `GET /api/self-repair/latest` endpoint reading `nightwatch-self-repair.yaml`; new ForgeResultCard component or section in health page. The YAML structure is already stable. |
| Per-indicator rejection rate sparkline alongside value sparkline | Health page shows a value sparkline per indicator (e.g., "test coverage: 82, 83, 85 →") but no rejection rate sparkline. A user seeing "coverage improving" next to "80% of coverage signals rejected" needs both in the same row to assess whether the trend is signal-driven or noise. Currently these are in separate sections (indicator value row vs LineChart section below). | LOW | `per_indicator_rates[indicator].history` currently contains fake data; fix the real data first (see "Feedback trend over time"), then the sparkline is a component addition — same `Sparkline` used with rate history array. |
| Auto-calibration effect visible in dashboard | `current_threshold` per indicator is computed but never written back to any config or shown adjusting the pipeline behavior. Users see "40% reject rate → threshold 0.7" but have no way to know if this threshold is actually used anywhere or is just decorative. The feature is only table stakes if the threshold is actually wired into something (auto-calibration) — without that wiring, displaying it is misleading. | HIGH | Requires: (1) propagating `current_threshold` from `CalibrationData` back to the kc-nightwatch skill via the journal context or a config file it reads; (2) surfacing in the dashboard that auto-calibration is active and showing the current threshold value per indicator |

### Differentiators (Worth Doing Well)

Features where quality of implementation matters beyond basic presence — these are what make the flywheel "visible and self-adjusting" rather than just a stats page.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Time-bucketed feedback trend (per-run rate, not rolling average) | Grouping feedback by run_id and displaying accept/reject rate per run (x-axis = run index, y-axis = rate) shows "learning over time" rather than a cumulative diluted average. A system that improved from 60% accept to 90% accept after 5 runs should show that upward slope, not just "75% overall." | MEDIUM | `getCalibrationData()` currently aggregates all-time; extend `feedback-store.ts` with a `getCalibrationHistory(runIds: string[])` function that buckets by run_id in run-date order. Feed into existing `LineChart` component (currently rendering fake data). |
| Calibration thresholds annotated on trend chart | When the auto-calibration threshold changes over time, annotating those changes on the trend line (e.g., a dotted horizontal line at y=0.7, labeled "threshold") makes the control loop visible. Users see: "rejection rate was 60%, threshold raised to 0.7, rate then dropped to 30%." | MEDIUM | SVG annotation line inside `LineChart` component; threshold history requires adding a timestamp to `current_threshold` when it changes (minor schema addition) |
| Signal prioritization display in run detail | When a run produces 12 signals but only 3 are acted on, showing them ranked by `confidence × historical_success_rate` (not arbitrary order) lets users understand why signals were selected, and builds trust in the selection mechanism. | MEDIUM | `RunSummaryAction` already has `assessment.confidence`; historical success rate must be derived from `FeedbackEntry` (accepted/total for the same indicator); ranking is computed server-side in a new endpoint or embedded in the existing run summary response |
| Forge result status badge on target card | A small pass/fail/warn badge on each target's card in the dashboard (reading from the latest self-repair result) gives users an at-a-glance plugin health signal without navigating to the health page. This is the same information as the forge results page/section, surfaced one level higher. | LOW | Requires same `GET /api/self-repair/latest` endpoint; target card must check if the target is "kc-nightwatch" (self-monitoring) or surface forge results per monitored target if those are also validated |
| Indicator sparkline tooltip on hover | The existing `Sparkline` SVG component shows a 80x20 chart but no values on hover. Adding a simple SVG `<title>` element or a positioned tooltip showing "run N: 83" on hover converts a purely directional signal into a precise one. Low implementation cost, meaningfully improves utility. | LOW | Pure SVG addition to `Sparkline` component; `<title>` in the SVG path element is the accessibility-correct approach; custom positioned div is an alternative for richer UX |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Rolling average trend smoothing | "The per-run rate is too noisy — smooth it with a 3-run moving average" | Smoothing hides the very signal the system is trying to capture: abrupt threshold changes in auto-calibration should show as step functions, not gradual curves. Smoothing makes a 3-run improvement look like a gradual 10-run improvement and obscures whether a calibration change had an effect. | Show raw per-run rates. If noise is an issue, add more runs to the x-axis rather than smoothing. |
| Global accept/reject rate aggregate chart across all targets | "Show me the overall flywheel health in one chart" | Different targets have completely different north stars and signal types. A global reject rate mixing "PR quality" (low stakes, high volume) and "test coverage" (high stakes, low volume) produces a meaningless number. The health page already aggregates health into an overall indicator — that's the right level. | Keep the existing per-target HealthSummaryBar for global health signal; per-indicator charts stay per-target. |
| Historical threshold editing (allow user to override computed thresholds) | "I want to override the computed 0.7 threshold to 0.5 for this indicator" | Manual override defeats the auto-calibration purpose. More importantly, the threshold formula (`0.5 + (rejectRate - 0.5) * 0.5`) is a deterministic function of reject rate — if the user disagrees with the threshold, the correct action is to submit more feedback to change the reject rate, not to override the formula. | Surface the formula explanation in the dashboard ("threshold = 0.5 + reject_rate × 0.5") so users understand how to influence it. |
| Feedback trend chart as interactive zoom-and-pan | "I want to scrub through 6 months of feedback history" | The nightwatch pipeline runs infrequently (daily/weekly). Even after 6 months, this is 20-180 data points — well within the range of a static SVG chart. Interactive zoom is appropriate for hundreds of data points, not dozens. The no-build constraint also makes interactive chart libraries (d3, Chart.js) expensive to add. | Show all available data points in the existing `LineChart` component. If the run count exceeds 20, show the last 20 with a count label ("showing last 20 of N"). |
| Automated signal suppression based on reject rate | "If an indicator's reject rate is above 80%, stop sending those signals automatically" | Auto-suppression creates invisible dead zones: users won't know a class of signal is being blocked, can't tell if the situation changed, and can't re-enable without knowing to look for the suppression. The `current_threshold` raising approach is safer — signals still appear but ranked lower. | Use the calibration threshold to rank signals lower (or require higher LLM confidence), not to hard-suppress them. Always show the threshold adjustment in the dashboard so the effect is visible. |
| Forge result diff viewer (show changed lines from forge fix PR) | "I want to see what forge changed in-dashboard" | Forge fix PRs are GitHub PRs with proper diffs. Rendering a diff in the dashboard adds a diff-formatting component, a `gh pr diff` subprocess, and a code display UI. The GitHub PR URL is already shown — that's the right place for the diff. | Link to the forge fix PR URL in the ForgeResultCard. The PR diff is one click away. |

---

## Feature Dependencies

```
[Feedback trend over time (real data)]
    └──requires──> [getCalibrationHistory() in feedback-store.ts]
                   (bucket FeedbackEntry[] by run_id, join to run dates for chronological order)
    └──feeds──>    [LineChart on health page] (replace fake [0, rate] stub with real history array)
    └──enables──>  [Per-indicator rejection rate sparkline] (same data, smaller component)
    └──enables──>  [Calibration threshold annotation on trend chart]

[Per-indicator rejection rate sparkline]
    └──requires──> [Feedback trend data fix] (real per-run rates, not stub)
    └──requires──> [UI layout change on health page indicator row] (add second Sparkline beside value Sparkline)
    └──note──>     Sparkline component itself already exists — no new component needed

[Auto-calibration wiring]
    └──requires──> [current_threshold already computed in getCalibrationData()]
    └──requires──> [mechanism to pass thresholds to nightwatch skill]
                   Options: (A) write to journal context file the skill reads at Phase 0,
                             (B) write to a new ~/.claude/kc-plugins-config/nightwatch-calibration.yaml,
                             (C) inject via custom_prompt when enqueueing a run
    └──requires──> [nightwatch skill updated to read and use calibration thresholds]
                   (changes kc-nightwatch skill, not just the app — cross-component concern)
    └──enables──>  [Calibration status badge in dashboard ("auto-calibration: active / N thresholds adjusted")]
    └──note──>     This is the highest-complexity v4 feature; wiring to the skill is out of app scope
                   unless option C (custom_prompt injection) is used, which requires no skill changes

[Signal prioritization]
    └──requires──> [Historical success rate per indicator] (accepted / total for indicator, from FeedbackEntry[])
    └──requires──> [Confidence numeric mapping] (high=1.0, medium=0.5, low=0.2 or similar)
    └──requires──> [Score = confidence_numeric × historical_success_rate] (computed in run summary or server-side)
    └──enables──>  [Ranked signal display in run detail] (ActionCards ordered by score descending)
    └──note──>     Historical success rate is already computable from getCalibrationData();
                   confidence numeric mapping is the only new logic needed
    └──note──>     Ranking ActionCards in UI (frontend sort) vs ranking before action execution
                   (pipeline change) are two different features — distinguish clearly in planning

[Forge results display]
    └──requires──> [GET /api/self-repair/latest endpoint] (reads nightwatch-self-repair.yaml)
    └──requires──> [ForgeResultCard component OR section in health page]
    └──note──>     nightwatch-self-repair.yaml structure is stable: forge_result.status (pass/fail/warn),
                   forge_result.branch (nullable), forge_result.details (string)
    └──enables──>  [Forge status badge on target card in dashboard] (one level higher, same data)
    └──note──>     Self-repair run_date is in the YAML — surface "last checked: N days ago"

[Indicator sparkline tooltip]
    └──requires──> [Sparkline component change] (add SVG title or hover div)
    └──note──>     Pure component enhancement; no data dependencies; fully independent
```

---

## MVP Recommendation for v4.0

### P1 — Ship (high value, manageable scope)

**Feedback trend data fix** — Replace the fake `[0, rate]` stub in `health-api.ts` with real per-run bucketed rates. This unblocks `LineChart` rendering real data and unblocks the sparkline fix. The `FeedbackEntry.run_id` field exists; the `listRuns()` function exists; this is a data join in `health-api.ts`, not a schema change.

**Forge results display** — New `GET /api/self-repair/latest` endpoint + `ForgeResultCard` component added to health page. `nightwatch-self-repair.yaml` is stable. One read endpoint + one display component. Highest value-to-complexity ratio in v4.

**Per-indicator rejection rate sparkline** — Depends on the feedback trend data fix. Once `per_indicator_rates[].history` is real, add a second `Sparkline` in the indicator row on the health page. Uses existing component, existing layout slot. Small change with clear value: users see value trend and rejection trend side-by-side.

**Indicator sparkline tooltip** — Add `<title>` SVG element to `Sparkline` component. Fully independent, low effort, meaningful improvement for accessibility and precision.

### P2 — Ship if scope allows

**Signal prioritization (display only)** — Sort `ActionCard` list in the run detail view by a `score = confidence_numeric × acceptance_rate` derived from `CalibrationData`. This is frontend-only sorting using data already available. Distinct from changing the pipeline execution order (P3).

**Calibration threshold annotation on trend chart** — Add a dotted horizontal line at `y = current_threshold` to the `LineChart`. Requires the feedback trend data fix (P1 precondition). Low complexity once data is real.

### P3 — Defer to v4.1+

**Auto-calibration wiring to nightwatch skill** — Propagating `current_threshold` back into the kc-nightwatch pipeline requires deciding on a mechanism (journal context vs config file vs custom_prompt) and potentially modifying the kc-nightwatch skill. This is a cross-component change with implications for the skill's Phase 0 behavior. Worth its own milestone sub-task.

**Signal prioritization in pipeline execution** — Changing *which* signals nightwatch acts on (not just display order in the dashboard) requires modifying the skill's Phase 3 signal ranking. Cross-component, separate from the display-only sort.

**Forge status badge on target card** — Depends on forge results display (P1). Once that endpoint exists, adding a badge to target cards is low effort — but it requires a decision about whether to show per-target forge results (each target monitored by NW has its own forge check?) or just the kc-nightwatch self-check. Defer until the forge results page clarifies scope.

---

## Implementation Pattern Notes

### Feedback Trend Data Fix

The bottleneck: `per_indicator_rates[indicator].history` in `health-api.ts` line 70-73 currently returns `[0, currentRate]` — a two-point stub. Real fix:

1. Collect `FeedbackEntry[]` for all runs in the `last10` window
2. Group by `run_id`, then by `indicator` (derived from `signal_id.split(':')[0]`)
3. For each run (chronological), compute that run's reject rate per indicator
4. Return as a properly-ordered array of length equal to runs that had feedback

The `FeedbackEntry.run_id` field is already populated. The runs are already sorted chronologically in `runsWithSummary`. This is a pure data aggregation change in `health-api.ts` — no new files, no schema changes.

### Forge Results Endpoint

`GET /api/self-repair/latest` reads `~/.claude/kc-plugins-config/nightwatch-self-repair.yaml` via the existing `readYamlFile()` helper. The relevant fields:

```typescript
interface SelfRepairResult {
  run_date: string
  mode: string
  forge_result: {
    status: 'pass' | 'fail' | 'warn'
    branch: string | null
    details: string
  }
  config_warnings: Array<{ target: string; field: string; error: string; suggestion: string }>
  config_fixes: Array<unknown>
}
```

New `ForgeResultCard` component in health page: status badge (green/red/yellow), `details` text (truncated with expand), `branch` link if non-null, `run_date` as "last checked N days ago."

### Signal Prioritization Score

Confidence numeric mapping: `high → 1.0`, `medium → 0.5`, `low → 0.2` (not linear — high is strongly preferred over medium).

Historical success rate: already available from `CalibrationData.reject_rate` per indicator. Success rate = `1 - reject_rate`.

Score: `confidence_numeric × (1 - reject_rate)`. An action with `high` confidence and 20% reject rate scores `1.0 × 0.8 = 0.8`. An action with `medium` confidence and 0% reject rate scores `0.5 × 1.0 = 0.5`. The high-confidence action ranks above the medium-confidence action even with slightly more historical rejection.

Edge case: indicators with zero feedback (`total_feedback === 0`) → `success_rate = 1.0` (benefit of doubt). This matches existing behavior where new indicators aren't penalized.

### Per-Indicator Rate Sparkline Layout

Current health page indicator row:
```
[indicator name]     [value sparkline]   [current value]   [trend arrow]
```

Target v4 layout:
```
[indicator name]     [value sparkline]   [rate sparkline]   [current value]   [trend arrow]
```

The `rate sparkline` uses the same `Sparkline` component but inverted color logic: higher reject rate is red (bad), lower is green (good). A separate `RateSparkline` wrapper component around `Sparkline` handles color inversion without modifying the base component.

### Auto-Calibration Display (display-only, threshold wire-up deferred)

The calibration endpoint already returns `current_threshold` per indicator. Add a small "Calibration" section to the health page showing:

```
Indicator          Feedback  Reject%  Threshold
coverage:test-count   12      40%      0.70 ↑
review-friction       8       25%      0.62 ↓
```

Arrow direction: threshold vs the neutral 0.5 baseline (up = more selective = tighter filter). This surfaces the auto-calibration data without requiring skill changes. The wire-up to the pipeline is a separate P3 item.

---

## Existing Component and Data Summary

| Component/Data | Current State | v4.0 Change |
|----------------|--------------|-------------|
| `Sparkline` | Used for indicator value history — exists, works | Add `<title>` tooltip (P1); no other changes |
| `LineChart` | Renders reject rate history — exists but fed fake `[0, rate]` data | Fix data source to real per-run bucketed rates (P1) |
| `HealthIndicatorData.history[]` | Real per-run indicator values — already working | No change |
| `per_indicator_rates[].history` | Fake two-point stub — currently broken | Fix in `health-api.ts` (P1 data fix) |
| `CalibrationData[]` from `/api/feedback/calibration` | All-time aggregate per indicator | Add `getCalibrationHistory()` function for time-series (P1) |
| `nightwatch-self-repair.yaml` | Exists, written by self-repair runs | New read endpoint + ForgeResultCard (P1) |
| `FeedbackEntry.submitted_at` | Exists but unused in health computation | Used in per-run bucketing (P1 data fix) |
| `ActionCard` | Renders action with feedback buttons and outcome links | Sort by priority score (P2 signal prioritization) |

---

## Feature Prioritization Matrix

| Feature | User Value | Complexity | Priority |
|---------|------------|------------|----------|
| Feedback trend data fix (real per-run rates) | HIGH — enables all trend viz features | MEDIUM | P1 — foundational |
| Forge results display | HIGH — first-time visibility of NW self-health | LOW | P1 — independent quick win |
| Per-indicator rejection rate sparkline | HIGH — value + rejection side-by-side | LOW (after data fix) | P1 — depends on data fix |
| Sparkline tooltip on hover | MEDIUM — precision over direction-only | LOW | P1 — independent quick win |
| Calibration data table (display-only) | MEDIUM — makes threshold logic visible | LOW | P1 — display only |
| Signal prioritization (display sort) | MEDIUM — improves actionability of run detail | MEDIUM | P2 |
| Calibration threshold annotation on trend chart | MEDIUM — makes control loop visible | MEDIUM | P2 — after data fix |
| Auto-calibration wire-up to NW skill | HIGH — closes the flywheel adjustment loop | HIGH | P3 — next milestone |
| Signal prioritization in pipeline execution | HIGH — changes what NW acts on | HIGH | P3 — next milestone |
| Forge status badge on target card | LOW — convenience, redundant with health page | LOW | P3 — after P1 scope settled |

---

## Sources

- Direct codebase inspection (2026-03-25): `app/server/services/feedback-store.ts`, `app/server/routes/health-api.ts`, `app/server/routes/feedback.ts`, `app/shared/types.ts`, `app/frontend/pages/health.ts`, `app/frontend/components/sparkline.ts`, `app/frontend/components/line-chart.ts`, `app/frontend/components/action-card.ts`, `~/.claude/kc-plugins-config/nightwatch-self-repair.yaml`, `~/.claude/kc-plugins-config/nightwatch-feedback.yaml` — HIGH confidence (direct read, current state confirmed)
- `.planning/PROJECT.md` v4.0 target features — HIGH confidence (authoritative)
- PatternFly Sparkline design guidelines (patternfly.org) — MEDIUM confidence (sparkline UX best practices: no axes, pair with metric, answer "where are we, direction, trend")
- Smashing Magazine — UX strategies for real-time dashboards (smashingmagazine.com/2025) — MEDIUM confidence (progressive disclosure via hover states, annotation patterns)
- RICE scoring model (productplan.com) — MEDIUM confidence (signal prioritization framework: confidence × success_rate is a RICE-inspired composite score)
- FasterCapital — Dashboard dynamics integrating sparklines (fastercapital.com) — LOW confidence (general dashboard patterns only)

---

*Feature research for: Nightwatch Dashboard v4.0 — Flywheel Intelligence*
*Researched: 2026-03-25*
