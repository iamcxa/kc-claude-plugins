# Phase 15: Data Layer Foundations - Research

**Researched:** 2026-03-25
**Domain:** Bun + Hono + TypeScript server-side data layer — EMA calibration, run-id bucketing, new API endpoints
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Trend Bucketing**
- D-01: Per-run-id bucketing with 30-run window cap. Each run produces one data point in the history array. Cap at 30 to prevent unbounded array growth.
- D-02: History arrays populate from feedback.yaml entries grouped by run_id, with reject rate computed per-run per-indicator.

**EMA Calibration**
- D-03: Replace raw all-time average (feedback-store.ts:83) with EMA smoothing, α=0.3. Formula: `threshold_new = α * current_rate + (1 - α) * threshold_old`.
- D-04: Minimum N gate: indicators with fewer than 10 feedback entries return `threshold: null` with a message "Accumulating data (N/10)". This prevents volatile thresholds from misleading users.
- D-05: α is hardcoded at 0.3 — not user-configurable. Premature configurability adds complexity with no user benefit at this stage.
- D-06: Threshold clamping range stays at [0.1, 0.9] (same as current formula).

**API Surface**
- D-07: Trends data is added to the existing `GET /api/feedback/calibration` endpoint response (extend CalibrationData type with `history: number[]`). Same data source (feedback.yaml), natural co-location.
- D-08: New `GET /api/forge/results` endpoint — reads nightwatch-self-repair.yaml, returns forge_result block. Separate from /api/config/warnings because semantics differ (quality check ≠ config warning).
- D-09: New `GET /api/signals/priority` endpoint — aggregates last 30 runs' actions ranked by `confidence_weight × (1 - reject_rate)`. Returns sorted indicator list with scores.

**Forge Data Source**
- D-10: Forge results read from `~/.claude/kc-plugins-config/nightwatch-self-repair.yaml` (same file as /api/config/warnings but different field). Always returns 200 — empty/missing file returns `{ forge_result: null, stale: true }`.

### Claude's Discretion
- Internal data structures for run-id bucketing (Map vs array approach)
- Error handling strategy for malformed feedback.yaml entries
- Confidence weight mapping (high=1.0, medium=0.6, low=0.3 or similar)

### Deferred Ideas (OUT OF SCOPE)
- Auto-calibration skill wire-up (propagating thresholds back to kc-nightwatch skill) — v4.1+
- Configurable EMA α via safety.yaml — premature until system has enough feedback data to evaluate responsiveness
- Historical trend export/download — no current need
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| VIZ-01 | Health page shows per-indicator reject rate trend as a sparkline with real historical data (not fake 2-point stub) | Per-run bucketing in `getCalibrationData()` + `history: number[]` field on CalibrationData interface; health-api.ts line 71 is the fake stub to replace |
| SIG-02 | Calibration data is hidden for indicators with fewer than 10 feedback entries (minimum sample gate) | D-04 decision — `threshold: null` + message when `total_feedback < 10`; requires CalibrationData interface update |
| SIG-03 | Calibration threshold uses EMA smoothing (α=0.3) instead of raw all-time average | Replace formula at feedback-store.ts:83; EMA is stateless-computable from history array (no persistence needed) |
</phase_requirements>

## Summary

Phase 15 is a pure server-side data layer sprint with no frontend changes. All three requirements (VIZ-01, SIG-02, SIG-03) are served by modifications to `feedback-store.ts` and `shared/types.ts` plus two new route files. The existing codebase has all the data needed — `FeedbackEntry` objects already carry `run_id` and `submitted_at`, and `nightwatch-self-repair.yaml` already contains a `forge_result` block. The work is wiring, not infrastructure.

The most important insight is that EMA (D-03) and the minimum N gate (D-04) interact cleanly: when `total_feedback < 10`, return `threshold: null` — no EMA computation. When N >= 10, apply EMA across the per-run rate sequence and return the smoothed threshold. This means EMA can be computed statelessly from the history array (current rate at each run step) without persisting a separate "previous threshold" value. No new YAML files needed.

The CalibrationData interface needs two additions: `history: number[]` (per-run reject rates in chronological order, capped at 30) and `threshold_null_reason?: string` (explanation when threshold is null due to N gate). The existing `/api/feedback/calibration` endpoint response shape changes — Phase 16 frontend consumers must be aware.

**Primary recommendation:** Modify `getCalibrationData()` in `feedback-store.ts` to produce bucketed history + EMA threshold in one pass, add `history` and `threshold_null_reason` to `CalibrationData` in `shared/types.ts`, add two new route files (`routes/forge.ts`, `routes/signals.ts`), register them in `server/index.ts`.

## Standard Stack

### Core (unchanged — no new packages)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Bun | runtime | TypeScript execution, test runner | Already deployed; no decision needed |
| Hono | existing | HTTP routes | New routes follow `routes/*.ts` pattern |
| yaml (js-yaml) | existing | Read nightwatch-self-repair.yaml | `readYamlFile()` helper already covers this |
| bun:test | built-in | Unit tests | All 373 existing tests use `describe/it/expect` from bun:test |

**Installation:** No new packages required.

### New Types in `shared/types.ts`

```typescript
// Extend CalibrationData (existing interface, lines 176-182)
export interface CalibrationData {
  indicator: string
  total_feedback: number
  reject_count: number
  reject_rate: number
  current_threshold: number | null  // null when N < 10 (D-04)
  threshold_null_reason?: string    // "Accumulating data (N/10)" message
  history: number[]                 // per-run reject rates, chronological, capped at 30 (D-01)
}

// New types for new endpoints
export interface ForgeResultData {
  forge_result: {
    status: 'pass' | 'fail'
    branch: string | null
    details: string
  } | null
  run_date: string | null
  stale: boolean
}

export interface SignalPriorityItem {
  indicator: string
  score: number              // confidence_weight × (1 - reject_rate)
  confidence_weight: number
  reject_rate: number
  total_feedback: number
}
```

## Architecture Patterns

### Recommended Project Structure (no new directories)

```
app/server/routes/
├── feedback.ts         MODIFIED — /api/feedback/calibration returns extended CalibrationData
├── forge.ts            NEW      — GET /api/forge/results
├── signals.ts          NEW      — GET /api/signals/priority
└── (all other routes unchanged)

app/server/services/
└── feedback-store.ts   MODIFIED — getCalibrationData() with bucketing + EMA

app/shared/
└── types.ts            MODIFIED — CalibrationData, ForgeResultData, SignalPriorityItem
```

### Pattern 1: Run-ID Bucketing (for getCalibrationData)

**What:** Group all FeedbackEntry objects by run_id first, then by indicator within each run. Compute per-run reject rate per indicator. Sort by earliest submitted_at within the run. Return history arrays capped at 30.

**When to use:** D-01 and D-02 are locked. Run-id bucketing is the only approach.

**Internal data structure choice (Claude's discretion):** Use a `Map<string, Map<string, {total: number, rejected: number}>>` where outer key is `run_id`, inner key is `indicator`. Simpler than two nested loops over arrays.

**Example (feedback-store.ts modification):**
```typescript
// Source: direct codebase inspection — extends existing getCalibrationData() at line 55-94

export async function getCalibrationData(): Promise<CalibrationData[]> {
  const data = await readYamlFile<FeedbackStore>(FEEDBACK_YAML_PATH) ?? {}
  const all = [
    ...(data.explicit_feedback ?? []),
    ...(data.pr_feedback ?? []),
    ...(data.linear_feedback ?? []),
    ...(data.slack_feedback ?? []),
    ...(data.pr_review_feedback ?? []),
  ]

  // Step 1: Collect all run_ids in chronological order
  // (submitted_at is ISO string — lexicographic sort works)
  const runTimestamps = new Map<string, string>()
  for (const entry of all) {
    const existing = runTimestamps.get(entry.run_id)
    if (!existing || entry.submitted_at < existing) {
      runTimestamps.set(entry.run_id, entry.submitted_at)
    }
  }
  const sortedRunIds = [...runTimestamps.entries()]
    .sort(([, a], [, b]) => a.localeCompare(b))
    .map(([id]) => id)
    .slice(-30)  // D-01: cap at 30 runs

  // Step 2: Per-run per-indicator counts
  const runByIndicator = new Map<string, Map<string, { total: number; rejected: number }>>()
  for (const runId of sortedRunIds) {
    runByIndicator.set(runId, new Map())
  }
  for (const entry of all) {
    if (!runByIndicator.has(entry.run_id)) continue  // outside 30-run window
    const indicator = entry.signal_id.split(':')[0] ?? entry.target
    const runMap = runByIndicator.get(entry.run_id)!
    const current = runMap.get(indicator) ?? { total: 0, rejected: 0 }
    current.total++
    if (entry.verdict === 'rejected') current.rejected++
    runMap.set(indicator, current)
  }

  // Step 3: Build per-indicator history + EMA threshold
  const indicatorAllTime = new Map<string, { total: number; rejected: number }>()
  for (const entry of all) {
    const indicator = entry.signal_id.split(':')[0] ?? entry.target
    const current = indicatorAllTime.get(indicator) ?? { total: 0, rejected: 0 }
    current.total++
    if (entry.verdict === 'rejected') current.rejected++
    indicatorAllTime.set(indicator, current)
  }

  const results: CalibrationData[] = []
  for (const [indicator, { total, rejected }] of indicatorAllTime) {
    const rejectRate = total > 0 ? rejected / total : 0

    // D-04: Minimum N gate
    if (total < 10) {
      results.push({
        indicator,
        total_feedback: total,
        reject_count: rejected,
        reject_rate: Math.round(rejectRate * 100) / 100,
        current_threshold: null,
        threshold_null_reason: `Accumulating data (${total}/10)`,
        history: buildHistory(sortedRunIds, runByIndicator, indicator),
      })
      continue
    }

    // D-03: EMA α=0.3 over per-run rate sequence (D-05: α hardcoded)
    const history = buildHistory(sortedRunIds, runByIndicator, indicator)
    let emaThreshold = 0.5  // start value
    for (const rate of history) {
      emaThreshold = 0.3 * rate + 0.7 * emaThreshold
    }
    // D-06: Clamp to [0.1, 0.9]
    const currentThreshold = Math.min(0.9, Math.max(0.1, emaThreshold))

    results.push({
      indicator,
      total_feedback: total,
      reject_count: rejected,
      reject_rate: Math.round(rejectRate * 100) / 100,
      current_threshold: Math.round(currentThreshold * 100) / 100,
      history,
    })
  }
  return results
}

function buildHistory(
  sortedRunIds: string[],
  runByIndicator: Map<string, Map<string, { total: number; rejected: number }>>,
  indicator: string
): number[] {
  const history: number[] = []
  for (const runId of sortedRunIds) {
    const runMap = runByIndicator.get(runId)
    const counts = runMap?.get(indicator)
    if (counts && counts.total > 0) {
      history.push(Math.round((counts.rejected / counts.total) * 100) / 100)
    }
    // If indicator had no feedback in this run: skip (don't add 0 — misleading gap)
  }
  return history
}
```

**EMA design note:** The EMA is computed statelessly by iterating the history array. No "previous threshold" persistence is needed. Each call to `getCalibrationData()` recomputes EMA from scratch. This is correct for the current scale (feedback.yaml is small) and avoids the feedback.yaml write-back race (PITFALL-9).

### Pattern 2: Forge Results Endpoint (new routes/forge.ts)

**What:** Read `nightwatch-self-repair.yaml` via existing `readYamlFile()`, extract `forge_result` block, add staleness check from `run_date`, return 200 always.

**Example:**
```typescript
// Source: config.ts pattern at line 22-25 — same YAML file, different field
// SELF_REPAIR_YAML_PATH is already defined in config.ts; import or redefine

import path from 'node:path'
import os from 'node:os'
import { Hono } from 'hono'
import { readYamlFile } from '../services/yaml-store.ts'
import type { ForgeResultData } from '../../shared/types.ts'

export const forgeRoutes = new Hono()

const SELF_REPAIR_YAML_PATH = path.join(os.homedir(), '.claude/kc-plugins-config/nightwatch-self-repair.yaml')
const STALE_THRESHOLD_MS = 36 * 60 * 60 * 1000  // 36 hours (D-10)

forgeRoutes.get('/api/forge/results', async (c) => {
  const data = await readYamlFile<Record<string, unknown>>(SELF_REPAIR_YAML_PATH)

  if (!data) {
    return c.json({ forge_result: null, run_date: null, stale: true } satisfies ForgeResultData)
  }

  const runDate = data.run_date as string | undefined ?? null
  const stale = runDate
    ? (Date.now() - new Date(runDate).getTime()) > STALE_THRESHOLD_MS
    : true

  const forgeResult = data.forge_result as ForgeResultData['forge_result'] | undefined ?? null

  return c.json({ forge_result: forgeResult, run_date: runDate, stale } satisfies ForgeResultData)
})
```

### Pattern 3: Signal Priority Endpoint (new routes/signals.ts)

**What:** Aggregate last 30 runs' actions from `listRuns()` + `getRun()`, compute `confidence_weight × (1 - reject_rate)` per indicator, return sorted list.

**Confidence weight mapping (Claude's discretion):** `high=1.0, medium=0.6, low=0.3`. These values give a 3:2:1 ratio that meaningfully differentiates high-confidence signals while keeping low-confidence signals visible (not zero).

**Example:**
```typescript
// Source: health-api.ts pattern — same listRuns/getRun pattern
import { Hono } from 'hono'
import { listRuns, getRun } from '../services/run-store.ts'
import { getCalibrationData } from '../services/feedback-store.ts'
import type { SignalPriorityItem } from '../../shared/types.ts'

export const signalsRoutes = new Hono()

const CONFIDENCE_WEIGHT: Record<string, number> = {
  high: 1.0,
  medium: 0.6,
  low: 0.3,
}

signalsRoutes.get('/api/signals/priority', async (c) => {
  // Cap at 30 runs (D-09)
  const allRuns = await listRuns({})
  const last30 = allRuns.slice(0, 30)

  // Collect all actions from the last 30 runs
  const indicatorCounts = new Map<string, { weightSum: number; count: number; confidence: string }>()

  for (const run of last30) {
    const detail = await getRun(run.id)
    if (!detail?.summary?.per_target) continue
    for (const targetSummary of Object.values(detail.summary.per_target)) {
      for (const action of targetSummary.actions ?? []) {
        const indicator = action.indicator
        const weight = CONFIDENCE_WEIGHT[action.assessment.confidence] ?? 0.3
        const current = indicatorCounts.get(indicator) ?? { weightSum: 0, count: 0, confidence: action.assessment.confidence }
        current.weightSum += weight
        current.count++
        indicatorCounts.set(indicator, current)
      }
    }
  }

  // Get calibration data for reject rates
  const calibration = await getCalibrationData()
  const rejectRateByIndicator = new Map(calibration.map(c => [c.indicator, c.reject_rate]))

  // Compute priority scores
  const items: SignalPriorityItem[] = []
  for (const [indicator, { weightSum, count, confidence }] of indicatorCounts) {
    const avgWeight = count > 0 ? weightSum / count : 0
    const rejectRate = rejectRateByIndicator.get(indicator) ?? 0
    const score = Math.round(avgWeight * (1 - rejectRate) * 100) / 100
    items.push({
      indicator,
      score,
      confidence_weight: Math.round(avgWeight * 100) / 100,
      reject_rate: rejectRate,
      total_feedback: calibration.find(c => c.indicator === indicator)?.total_feedback ?? 0,
    })
  }

  // Sort descending by score
  items.sort((a, b) => b.score - a.score)

  return c.json(items)
})
```

### Pattern 4: Route Registration (server/index.ts)

**What:** Add two new import + `app.route()` calls — same pattern as all 10 existing routes.

```typescript
// Source: server/index.ts lines 18-164 — established pattern
import { forgeRoutes } from './routes/forge.ts'
import { signalsRoutes } from './routes/signals.ts'

// After existing registrations:
app.route('/', forgeRoutes)
app.route('/', signalsRoutes)
```

### Anti-Patterns to Avoid

- **Writing calibration thresholds back to feedback.yaml:** `feedback.yaml` is append-only. `writeYamlFile(FEEDBACK_YAML_PATH, ...)` outside `appendFeedback` causes race conditions. EMA is computed on-demand — no write-back needed.
- **Re-using `SELF_REPAIR_YAML_PATH` from config.ts via import:** `config.ts` does not export the constant. Define it locally in `forge.ts` (same value: `path.join(os.homedir(), '.claude/kc-plugins-config/nightwatch-self-repair.yaml')`).
- **Returning 404 when self-repair YAML is missing:** D-10 mandates always-200 with `{ forge_result: null, stale: true }`. Never 404.
- **Returning 0 in history for runs where indicator had no feedback:** This creates false flat lines. Skip runs with no feedback for that indicator — the history array may be shorter than 30 elements.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| YAML reading | Custom file parser | `readYamlFile()` from `yaml-store.ts` | Already handles missing file (returns null), already used by config.ts |
| ISO date comparison for staleness | Custom date math | `Date.now() - new Date(runDate).getTime()` | Standard JS, no library needed |
| Run history access | Custom file scanner | `listRuns()` + `getRun()` from `run-store.ts` | Already tested, handles edge cases |
| HTTP routing | Custom request handler | Hono `routes/*.ts` pattern | Consistent with all 10 existing route files |

**Key insight:** The YAML store, run store, and feedback store already provide everything Phase 15 needs. This phase is composition, not construction.

## Common Pitfalls

### Pitfall 1: CalibrationData.current_threshold type change breaks existing tests

**What goes wrong:** `current_threshold` changes from `number` to `number | null` (D-04). The existing `calibration.test.ts` and `feedback.test.ts` tests assert `threshold` is always a number. The health-api.ts line 69 (`perIndicatorRates`) uses `cal.current_threshold` without null check.

**Why it happens:** SIG-02 requires null threshold below N=10. The type system change propagates to every consumer.

**How to avoid:** Update `shared/types.ts` first, then fix TypeScript errors. `health-api.ts` already guards with `if (cal.total_feedback > 0)` — add `&& cal.current_threshold !== null` or handle null explicitly. Update the test assertions that assume numeric threshold.

**Warning signs:** TypeScript compile errors after types.ts change. Tests like "CalibrationData computes reject rate correctly" that hardcode numeric threshold assertions.

### Pitfall 2: Fake history stub test still passes after real implementation

**What goes wrong:** `health-api.test.ts` line 335-342 asserts `history.length >= 2`. This passes with the fake `[0, rate]` two-point stub AND would pass with real bucketed history. The test does not verify that history contains more than 2 points or that the values come from real runs.

**Why it happens:** The test was written to assert minimum shape, not data source authenticity.

**How to avoid:** The `health-api.ts` fake history stub (line 71: `history: [0, Math.round(cal.reject_rate * 100) / 100]`) needs to be replaced with real data from `getCalibrationData()` (which now returns `history`). Since `getCalibrationData()` already returns history in CalibrationData, health-api.ts should use `cal.history` directly instead of hardcoding. The test for VIZ-01 should verify that the history array contains values that match what bucketed runs would produce.

**Warning signs:** After the implementation, health-api.ts still has the literal `[0, ...]` line at line 71.

### Pitfall 3: EMA starting value affects first-run threshold significantly

**What goes wrong:** EMA formula `threshold_new = 0.3 * rate + 0.7 * threshold_old`. If `threshold_old` starts at 0.5 and the first few runs have 100% reject rate, the threshold climbs from 0.5 → 0.65 → 0.755 → ... quickly. Starting at 0.5 is arbitrary.

**Why it happens:** EMA has no cold-start mitigation. The first data points have the same weight as later ones relative to the starting value.

**How to avoid:** The minimum N gate (D-04) mitigates this naturally — EMA is only computed when N >= 10, by which point the history sequence is long enough that the starting value's influence has decayed (0.7^10 ≈ 0.028, meaning the starting value contributes less than 3% after 10 runs). This is acceptable. Document the starting value as 0.5 in a comment.

**Warning signs:** Threshold values that seem too high/low for the observed reject rate history — check that the N gate is being applied correctly.

### Pitfall 4: signals/priority endpoint scans all runs (no cap applied)

**What goes wrong:** D-09 says cap at 30 runs. `listRuns({})` returns all runs sorted desc. If `.slice(0, 30)` is forgotten or applied to the wrong variable, the endpoint scans unbounded history.

**Why it happens:** Easy to forget the cap when copy-pasting from health-api.ts which uses `slice(0, 10)`.

**How to avoid:** The cap is `slice(0, 30)` applied to the result of `listRuns({})` before the `getRun()` loop. Add a comment: `// D-09: cap at 30 runs`.

**Warning signs:** Response time > 500ms on a machine with many runs (each `getRun()` is a file read).

### Pitfall 5: forge.ts re-importing SELF_REPAIR_YAML_PATH from config.ts

**What goes wrong:** `config.ts` defines `const SELF_REPAIR_YAML_PATH = ...` but does NOT export it. Trying to `import { SELF_REPAIR_YAML_PATH } from '../routes/config.ts'` will fail with "not exported" or cause accidental side-effect import of the entire config route registration.

**Why it happens:** The path constant was not designed to be shared.

**How to avoid:** Redefine the path constant locally in `forge.ts`. Both files point to the same path string. If the path needs changing later, update both.

**Warning signs:** TypeScript error "does not provide an export named 'SELF_REPAIR_YAML_PATH'".

### Pitfall 6: Existing calibration.test.ts tests compute the old formula inline

**What goes wrong:** `calibration.test.ts` (line 5-6) inlines the old formula `0.5 + (rejectRate - 0.5) * 0.5` directly in a `computeThreshold` helper. After replacing the formula in `feedback-store.ts`, these tests still pass because they test an inline copy — not the real implementation.

**Why it happens:** The tests were written as unit tests of the formula, not integration tests of the function.

**How to avoid:** Update or replace `calibration.test.ts` with tests that call `getCalibrationData()` (via spy/mock) and verify the EMA formula output. The old formula tests can be archived as comments showing what changed.

**Warning signs:** All calibration tests pass after the change even though the formula is completely different.

## Code Examples

### EMA Formula (verified against D-03)

```typescript
// Source: CONTEXT.md D-03 (locked decision)
// Formula: threshold_new = α * current_rate + (1 - α) * threshold_old
// α = 0.3 (D-05: hardcoded)
const ALPHA = 0.3
let emaThreshold = 0.5  // starting value
for (const rate of history) {
  emaThreshold = ALPHA * rate + (1 - ALPHA) * emaThreshold
}
// D-06: Clamp to [0.1, 0.9]
const currentThreshold = Math.min(0.9, Math.max(0.1, emaThreshold))
```

### Old vs New Threshold Formula

```typescript
// OLD (feedback-store.ts line 83) — stateless linear formula:
const currentThreshold = Math.min(0.9, Math.max(0.1, 0.5 + (rejectRate - 0.5) * 0.5))

// NEW — EMA over per-run history:
// (see Pattern 1 above for full implementation)
```

### Forge YAML Schema (verified from actual file)

```yaml
# ~/.claude/kc-plugins-config/nightwatch-self-repair.yaml
run_date: "2026-03-17T21:30:00+08:00"
mode: dry-run
config_fixes: []
config_warnings:
  - target: kc-team-ops
    field: path
    error: "..."
forge_result:
  status: pass      # 'pass' | 'fail'
  branch: null      # string | null
  details: "0 FAIL, 4 WARN — ..."
feedback_collected:
  prs_scanned: 4
  ...
```

The `forge_result` block is what `/api/forge/results` returns. The `config_warnings` block is what `/api/config/warnings` already returns. They are co-located in the same file but represent different concerns (D-08).

### bun:test Spy Pattern (from health-api.test.ts)

```typescript
// Source: app/tests/server/health-api.test.ts lines 126-161
// This is the established pattern for testing routes with mocked services

import { spyOn } from 'bun:test'
import * as feedbackStore from '../../server/services/feedback-store.ts'

let getCalibrationDataSpy: ReturnType<typeof spyOn>

// In beforeEach:
getCalibrationDataSpy = spyOn(feedbackStore, 'getCalibrationData')
  .mockImplementation(async () => mockCalibration)

// In afterEach:
getCalibrationDataSpy.mockRestore()
```

## Environment Availability

Step 2.6: SKIPPED (no external dependencies — Phase 15 is server-only code changes with no new external tools, CLIs, or services).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | bun:test (built-in) |
| Config file | none — `bun test` auto-discovers `tests/**/*.test.ts` |
| Quick run command | `bun test --testPathPattern="calibration\|feedback\|forge\|signals" 2>/dev/null` |
| Full suite command | `bun test 2>/dev/null \| tail -5` |

Run from: `/Users/kent/Project/kc-claude-workspace/kc-claude-plugins/kc-nightwatch/app`

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| VIZ-01 | `per_indicator_rates[].history` contains real bucketed data (not fake `[0, rate]`) | unit | `bun test tests/server/health-api.test.ts` | ✅ — extend existing |
| VIZ-01 | `getCalibrationData()` returns `history: number[]` with per-run rates | unit | `bun test tests/server/feedback.test.ts` | ✅ — extend existing |
| SIG-02 | `current_threshold` is `null` when `total_feedback < 10` | unit | `bun test tests/server/calibration.test.ts` | ✅ — update existing |
| SIG-02 | `threshold_null_reason` contains "Accumulating data (N/10)" message | unit | `bun test tests/server/calibration.test.ts` | ✅ — update existing |
| SIG-03 | EMA threshold equals expected value for known history sequence | unit | `bun test tests/server/calibration.test.ts` | ✅ — update existing |
| D-08 | `GET /api/forge/results` returns 200 when file missing | unit | `bun test tests/server/forge.test.ts` | ❌ Wave 0 |
| D-08 | `GET /api/forge/results` returns `stale: true` when run_date > 36h | unit | `bun test tests/server/forge.test.ts` | ❌ Wave 0 |
| D-09 | `GET /api/signals/priority` returns sorted items with score field | unit | `bun test tests/server/signals.test.ts` | ❌ Wave 0 |
| D-09 | signals endpoint caps at 30 runs | unit | `bun test tests/server/signals.test.ts` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `bun test --testPathPattern="calibration\|feedback\|health-api" 2>/dev/null | tail -5`
- **Per wave merge:** `bun test 2>/dev/null | tail -5` (full suite, must stay 373+ pass, 0 fail)
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/server/forge.test.ts` — covers D-08 (forge results endpoint): missing file → 200+null, stale check, forge_result extraction
- [ ] `tests/server/signals.test.ts` — covers D-09 (signal priority endpoint): score formula, sorted order, 30-run cap

*(Existing test files for calibration, feedback, and health-api cover VIZ-01/SIG-02/SIG-03 — they need updates not new files.)*

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Linear formula: `0.5 + (rejectRate - 0.5) * 0.5` | EMA α=0.3 over per-run history | Phase 15 (D-03) | Threshold is now temporally-smoothed, not just all-time-average |
| Fake 2-point history: `[0, currentRate]` | Real per-run bucketed rates from feedback.yaml | Phase 15 (D-01, D-02) | VIZ-01: LineChart gets real trend data |
| Always-numeric threshold | Null threshold below N=10 | Phase 15 (D-04) | SIG-02: UI can show "accumulating" state |

**Deprecated after Phase 15:**
- The `[0, Math.round(cal.reject_rate * 100) / 100]` fake history at health-api.ts:71 — replaced by `cal.history` from CalibrationData

## Open Questions

1. **Does `health-api.ts` need to be updated to use `cal.history` from CalibrationData?**
   - What we know: `health-api.ts` currently builds `per_indicator_rates[].history` as a fake 2-point array at line 71. After Phase 15, `CalibrationData.history` will contain real data.
   - What's clear: `health-api.ts` should use `cal.history` directly instead of the fake stub — this is how VIZ-01 gets satisfied.
   - Recommendation: Yes, update health-api.ts line 71 to `history: cal.history` as part of the Phase 15 plan. This is strictly correct since `getCalibrationData()` is already called at line 59.

2. **What if `FeedbackEntry.run_id` is empty string or undefined in malformed entries?**
   - What we know: `FeedbackEntry.run_id` is typed as `string` (not optional). In practice it could be empty if a feedback entry was created without a run context.
   - Recommendation (Claude's discretion per CONTEXT.md): Skip entries with empty/null `run_id` in the bucketing step. Log a warning via `log.warn()`. This is defensive and matches the pattern in `getFeedbackForRun()` which would simply never match.

3. **How does the test for `calibration.test.ts` need to change?**
   - What we know: `calibration.test.ts` tests the old inline formula. After Phase 15 the formula changes to EMA and the test will test a stale copy.
   - Recommendation: Replace the `computeThreshold` inline helper in `calibration.test.ts` with the EMA formula. Keep the boundary/clamping tests but update the expected values to match EMA output.

## Sources

### Primary (HIGH confidence)

- Direct codebase inspection: `app/server/services/feedback-store.ts` (all 117 lines)
- Direct codebase inspection: `app/shared/types.ts` (all 243 lines)
- Direct codebase inspection: `app/server/routes/health-api.ts` (all 94 lines)
- Direct codebase inspection: `app/server/routes/config.ts` (all 162 lines)
- Direct codebase inspection: `app/server/routes/feedback.ts` (all 53 lines)
- Direct codebase inspection: `app/server/index.ts` (all 187 lines) — route registration pattern
- Direct codebase inspection: `app/tests/server/calibration.test.ts` — existing test baseline
- Direct codebase inspection: `app/tests/server/feedback.test.ts` — existing test baseline
- Direct codebase inspection: `app/tests/server/health-api.test.ts` — spy pattern reference
- Direct file inspection: `~/.claude/kc-plugins-config/nightwatch-self-repair.yaml` — actual forge_result schema
- Test suite run: 373 pass, 0 fail — confirmed baseline before Phase 15 changes
- `.planning/phases/15-data-layer-foundations/15-CONTEXT.md` — locked decisions (D-01 through D-10)
- `.planning/REQUIREMENTS.md` — VIZ-01, SIG-02, SIG-03 definitions

### Secondary (MEDIUM confidence)

- `.planning/research/SUMMARY.md` — milestone-level architecture overview (2026-03-25)
- `.planning/research/PITFALLS.md` — 12 pitfalls with file locations (2026-03-25)
- `.planning/research/ARCHITECTURE.md` — v2.0 build order patterns (2026-03-21, prior milestone)
- MEMORY.md (kc-claude-workspace): calibration persistence decision, fake history location, feedback.yaml append-only constraint

### Tertiary (LOW confidence)

- General EMA dampening properties (cold-start behavior, α=0.3 convergence rate) — well-understood mathematics, no external citation needed

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — confirmed zero new packages; all patterns directly inspected in codebase
- Architecture patterns: HIGH — direct code inspection of all affected files; patterns are extensions of existing code
- Pitfalls: HIGH — most pitfalls derived from direct code reading (fake stub line 71, formula line 83, type change propagation) plus test inspection
- Test mapping: HIGH — all test files verified to exist; Wave 0 gaps identified precisely

**Research date:** 2026-03-25
**Valid until:** 2026-04-25 (stable domain — no external dependencies to become stale)

## Project Constraints (from CLAUDE.md)

Directives from `/Users/kent/Project/kc-claude-workspace/kc-claude-plugins/kc-nightwatch/CLAUDE.md` relevant to this phase:

| Directive | Impact on Phase 15 |
|-----------|-------------------|
| Safety values in `config/safety.yaml` only — never hardcode limits | Phase 15 adds `const ALPHA = 0.3` (D-05: hardcoded by decision, not a safety limit — OK) and `30-run window cap` (D-01: also a product decision — OK). Neither belongs in safety.yaml. |
| Commit convention: standard semantic prefixes (`feat`, `fix`) for human development | Phase 15 commits use `feat:` prefix |
| After skill/agent/config changes: dry-run before push | Phase 15 is app code changes only (not skill/agent/config) — dry-run rule does not apply |
| File ownership: `nightwatch-self-repair.yaml` is "Self-repair (auto)" — written each run | Phase 15 only READS this file from the forge endpoint. Never writes. This is correct. |
