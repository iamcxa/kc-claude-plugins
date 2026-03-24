# Pitfalls Research

**Domain:** Adding feedback trend visualization, auto-calibration, signal prioritization, forge results display, and indicator sparklines to existing Bun + Hono + Preact/HTM dashboard (v4.0 Flywheel Intelligence milestone)
**Researched:** 2026-03-25
**Confidence:** HIGH (based on direct codebase inspection of sparkline.ts, line-chart.ts, health-api.ts, feedback-store.ts, yaml-store.ts, frontend/index.html import map, vendor/ directory + known project-specific patterns from MEMORY.md)

> Note: This file covers v4.0 pitfalls only. For v1.0–v3.0 pitfalls (IPC shape, parallel execution, scheduler timers, concurrent YAML writes, auto PR dedup), see the previous research files for those milestones.

---

## Critical Pitfalls

### Pitfall 1: SVG attribute casing — Preact uses kebab-case for SVG, not camelCase

**What goes wrong:**
The existing `sparkline.ts` and `line-chart.ts` use `stroke-width="1.5"` correctly. If any new chart component is added that copies SVG from an external source (e.g., an icon, a reference implementation), camelCase attributes like `strokeWidth`, `strokeLinejoin`, `fillOpacity`, `textAnchor` will be passed as-is by Preact/HTM and silently fail to render in the browser. This is a Preact-specific behavior difference from React (which maps camelCase to SVG attributes) that has bitten this project before.

**Why it happens:**
Preact intentionally applies SVG attributes verbatim — what you write is what lands in the DOM. React normalizes camelCase to kebab-case; Preact does not. In HTM template literals, it is easy to copy SVG markup from a reference without noticing this difference.

**Consequences:**
Charts render with default stroke widths, wrong line joins, or missing text anchors. The chart appears to "work" but looks different than expected — lines are too thin, text is misaligned, rounded corners are missing. No error is thrown.

**Prevention:**
- Always use kebab-case for SVG attribute names in HTM templates: `stroke-width`, `stroke-linejoin`, `fill-opacity`, `text-anchor`, `font-size`, `font-family`.
- The existing sparkline.ts and line-chart.ts are correct models — follow their attribute naming exactly.
- When the browser renders unexpectedly, inspect the DOM element attributes directly in DevTools — a camelCase attribute that made it into the DOM is the tell.

**Detection:**
SVG element in browser DevTools shows `strokeWidth="1.5"` as a literal attribute name (instead of rendered as `stroke-width`). The line renders at browser default (1px) instead of 1.5px.

**Phase to address:** Any phase adding new chart components. Pre-check: audit every SVG attribute name before writing the component, not after noticing visual bugs.

---

### Pitfall 2: Preact singleton violation — adding a chart library via CDN or a second `<script type="module">` creates a second Preact instance

**What goes wrong:**
The import map in `index.html` maps `"preact"` to `/vendor/preact.module.js`. If any new vendor file (e.g., a charting library added to `/vendor/`) internally imports `preact` from a CDN URL (e.g., `https://esm.sh/preact`) instead of relying on the import map, two separate Preact instances will coexist. Hooks state, signals, and reconciliation break in subtle ways: `useState` updates don't re-render, `useEffect` fires twice, signals don't propagate.

**Why it happens:**
esm.sh bundles dependencies. If you download a pre-bundled ESM file (e.g., some chart library that depends on Preact), the bundle may have Preact inlined. The Preact docs explicitly warn: "Duplication of preact and some other libraries will cause (often subtle and unexpected) issues."

**Consequences:**
This is the "ghost Preact" failure mode. Symptoms are non-deterministic: components render once and stop updating, signals lose reactivity, error boundaries don't catch, hooks call order diverges. Debugging is extremely difficult because nothing throws — the app just stops working in portions.

**Prevention:**
- Do NOT add any pre-bundled chart library that has Preact as a dependency. The v4.0 features use inline SVG (as sparkline.ts and line-chart.ts already do) — stick to this pattern.
- If a library MUST be added, use the `?external=preact` esm.sh flag when downloading: `https://esm.sh/library@version?external=preact`. This produces a file that imports `preact` from the import map instead of inlining it.
- After adding any vendor file, open browser DevTools → Network tab → filter by `vendor` → inspect the file's source to confirm it does not contain inline `var h = ` (Preact's pragma) other than in `preact.module.js` itself.

**Detection:**
`window.__preactInstances` does not exist as a standard check, but you can verify by adding `console.log(window.__preact)` and checking uniqueness. Simpler: if `@preact/signals`'s `.value` changes but the component that uses `signal.value` doesn't re-render, a second Preact instance is almost certainly the cause.

**Phase to address:** Any phase that evaluates adding a third-party chart library (Phase X: Forge results display, or if sparklines need a more complex visualization). Decision: avoid external chart libraries entirely for v4.0 — all charts are SVG-in-HTM. This avoids the problem entirely.

---

### Pitfall 3: `per_indicator_rates.history` is currently a hardcoded 2-element fake — trend charts will look flat until real history is accumulated per-run

**What goes wrong:**
In `health-api.ts:71`, the reject rate history array is hardcoded:
```
history: [0, Math.round(cal.reject_rate * 100) / 100]  // baseline zero -> current rate
```
This means LineChart in `health.ts` always renders a straight line from 0% to the current reject rate — it has exactly 2 data points, which is the minimum to render. Any new "trend visualization" feature that adds more chart panels or a time-windowed view will pull this same fake history array and render meaningless flat-line charts, with no indication to the user that the data is synthetic.

**Why it happens:**
`feedback-store.ts` stores `FeedbackEntry` objects without timestamps bucketed per-run or per-time-window. `getCalibrationData()` computes a single aggregate reject rate from all historical entries — it does not produce a time series. The health API then fakes a two-point history from this scalar.

**Consequences:**
Feedback trend visualization (the core v4.0 feature) renders charts that appear to show trends but show no meaningful trend because the history is 2 points. Users will trust the flat lines and conclude "reject rate is stable at X%" when in reality they have no temporal data at all.

**Prevention:**
The real fix is to add a `week` or `submitted_at` timestamp bucketing step in `getCalibrationData()`:
- Group `FeedbackEntry` by week (ISO week number from `submitted_at`)
- Compute reject rate per week
- Return `history: number[]` with one point per week in chronological order

This requires no schema change to `FeedbackEntry` (it already has `submitted_at: string`). The computation is in `feedback-store.ts`, not in the frontend.

Specifically:
1. In `getCalibrationData()`, bucket entries by `submitted_at` week.
2. Sort weeks chronologically.
3. Produce one reject rate per week: `reject_count / total` for that week.
4. Return `history: weeklyRejectRates`.
5. `CalibrationData` interface needs a `history: number[]` field (currently absent from `shared/types.ts`).

**Detection:**
`GET /api/feedback/calibration` returns `history: [0, 0.5]` — exactly two elements regardless of how many feedback entries exist. Any chart using this data will be a straight diagonal line.

**Phase to address:** Phase 1 (feedback trend visualization). This is the foundation data fix. All chart UX depends on it being real data.

---

### Pitfall 4: Auto-calibration threshold formula is stateless — recalculated from scratch on every request, making calibration volatile with small sample sizes

**What goes wrong:**
`feedback-store.ts:83`:
```typescript
const currentThreshold = Math.min(0.9, Math.max(0.1, 0.5 + (rejectRate - 0.5) * 0.5))
```
This formula recomputes the threshold from the current aggregate reject rate every time `getCalibrationData()` is called. With only 3 feedback entries (e.g., 2 rejected, 1 accepted = 67% reject rate), the threshold jumps to 0.585. With 4 entries (2 rejected, 2 accepted = 50% reject rate), it falls back to 0.5. The threshold oscillates wildly with small N.

There is no persistence of the computed threshold. Every API call recalculates from all historical data — there is no "previous threshold" to compare against, no dampening, and no minimum sample size gate.

**Why it happens:**
The formula was designed as a first-pass placeholder. It works correctly in the limit (large N, stable reject rate) but is unreliable during the early feedback accumulation period (first 5–20 runs), which is exactly when a new user is using the system.

**Consequences:**
- Auto-calibration "jumps" by large amounts between runs when sample size is small.
- The NW skill, if it reads the threshold via API, gets a different value each run even if no new feedback has arrived (due to floating point and ordering).
- Dashboard shows confusing threshold changes that don't correspond to any user action.

**Prevention:**
Add two safeguards:
1. **Minimum sample size gate**: If `total_feedback < 10`, do not compute a calibrated threshold — return `current_threshold: null` and the UI shows "Accumulating data (N/10 feedback entries)".
2. **Exponential moving average (EMA) dampening**: Instead of a direct formula, use `newThreshold = alpha * formulaResult + (1 - alpha) * previousThreshold` where `alpha = 0.2` (slow adjustment). Requires persisting the previous threshold per-indicator in the YAML store.

The simpler option for v4.0: just gate on minimum sample size. EMA can come later.

**Detection:**
`GET /api/feedback/calibration` returns a different `current_threshold` value after adding a single new feedback entry that changes the reject rate by <5%. Threshold should be stable until N >= 10.

**Phase to address:** Phase 2 (auto-calibration). Fix the minimum sample gate before wiring calibration results into the dashboard display — otherwise the UI will show constantly-changing thresholds that confuse users.

---

### Pitfall 5: Signal prioritization adds a new scoring concept that is not in `shared/types.ts` — if score is computed in the worker and never returned to the server, the dashboard cannot show it

**What goes wrong:**
Signal prioritization (confidence × historical success ranking) requires computing a score at the point signals are evaluated — inside the NW skill execution, or in a post-run aggregation step. If the score is only computed within the `claude -p` subprocess (the NW skill itself), it lives in the LLM's reasoning and never gets written to a structured output file that the dashboard can read.

Currently, `RunSummaryAction` in `shared/types.ts` has `assessment.confidence: 'high' | 'medium' | 'low'` — a string enum, not a numeric score. There is no `priority_score: number` field anywhere in the type system.

**Why it happens:**
The NW skill was not designed to output a numeric priority score — it outputs string-based confidence levels. Adding signal prioritization in v4.0 requires either: (a) the skill emits numeric scores in Appendix B, (b) the dashboard computes scores from the existing confidence string + feedback history, or (c) a new server-side scoring step runs post-run on the stored summary.

**Consequences:**
If the dashboard tries to show "signal priority" but the data source doesn't exist yet, the feature ships as all-zeros or all-nulls. Or worse: the feature is wired to the confidence string (`high=3, medium=2, low=1`) without any historical success weighting, making it "just a confidence display" not actual prioritization.

**Prevention:**
Option B (server-side scoring from existing data) is the correct approach for v4.0:
- `RunSummaryAction.assessment.confidence` maps to a numeric base score.
- Historical success rate = accepted / total for signals with the same `indicator` field.
- Priority score = `confidenceScore * (1 + historicalSuccessRate)`.
- This computation belongs in a new `computeSignalPriority(action, calibration)` function in a shared utility — NOT in the frontend and NOT requiring skill changes.
- The API endpoint returns scored actions: `GET /api/runs/:id/signals` → `Array<RunSummaryAction & { priority_score: number }>`.

**Detection:**
Search `shared/types.ts` for `priority_score` — if absent, the feature has no data contract yet. Confirm before writing any UI code.

**Phase to address:** Phase 3 (signal prioritization). Define the data contract in `shared/types.ts` first, then the scoring logic, then the API, then the UI. In that order — never reverse.

---

## Moderate Pitfalls

### Pitfall 6: `feedback.yaml` grows unboundedly — `getCalibrationData()` scans all entries on every health API call

**What goes wrong:**
`feedback-store.ts` reads the entire `feedback.yaml` file and flattens all five source arrays on every `getCalibrationData()` call. The health API calls this on every `GET /api/health/:target`. The health page has a polling interval (via `usePoll`). At current scale (35 lines / ~1KB), this is fine. After 12 months of daily nightwatch runs generating 5–10 feedback entries per run, `feedback.yaml` will be ~500KB with ~2000 entries. YAML parse at 500KB is ~2ms. But scanning all 2000 entries to group by indicator adds O(N) overhead that compounds with the number of targets.

**Why it happens:**
The feedback store was designed for small N (prototype phase). There is no index, no TTL, no pagination, and no archival strategy.

**Consequences:**
Health page load time increases linearly with feedback history. At 10K entries, `yaml.parse()` on a 2MB file takes ~20ms and the array scan takes another 5ms. Still acceptable for a local tool, but it means the health endpoint is never cached and always re-reads disk.

**Prevention:**
No immediate action needed for v4.0 (current scale is far from problematic). Design the time-bucketed history from Pitfall 3's fix to only retain per-week aggregates — this naturally caps the working dataset. The raw entries can be archived after aggregation.

Add a comment in `feedback-store.ts` marking the file as "archival target after 1000 entries" so the threshold is documented before it's a problem.

**Detection:**
`wc -l ~/.claude/kc-plugins-config/nightwatch-feedback.yaml` > 500 lines. Add a warning log in `getCalibrationData()` if entry count exceeds 200.

**Phase to address:** Note in Phase 1 (feedback trend) when adding weekly bucketing. The bucketing step is a natural ceiling on working set size.

---

### Pitfall 7: Forge results display requires reading `nightwatch-self-repair.yaml` — this file may not exist or may be stale

**What goes wrong:**
`nightwatch-self-repair.yaml` is written by the `--self-repair` run (a separate `claude -p` session before the regular pipeline). The dashboard wants to display forge results from this file. If the server's API endpoint for forge results reads this file at request time, it may find: (a) no file (self-repair never ran), (b) a stale file from 3 days ago (self-repair ran but not today), (c) a file written mid-self-repair run (partial write).

The file path is `~/.claude/kc-plugins-config/nightwatch-self-repair.yaml`. The app does not currently have a route for this.

**Why it happens:**
Self-repair writes the file at the end of its session. The dashboard has no mechanism to know when the file was last written or whether it reflects the most recent self-repair outcome. The `run_date` field in the file IS present (verified from the actual file format), but the API consumer needs to check it before presenting the data as "recent".

**Consequences:**
Forge results panel shows yesterday's data labeled as current. User sees "0 config fixes" and thinks nothing was repaired today, but yesterday's self-repair is what's shown.

**Prevention:**
- Add `run_date` staleness check in the forge results API: if `run_date` is older than 36 hours, mark results as `stale: true` and the UI shows a "Last updated: 3 days ago" badge instead of presenting the data as current.
- The API response shape should include `run_date`, `stale: boolean`, and the raw `config_fixes` / `config_warnings` arrays.
- Empty state: if the file doesn't exist, return `{ run_date: null, stale: true, config_fixes: [], config_warnings: [] }` — do not 404.

**Detection:**
`ls -la ~/.claude/kc-plugins-config/nightwatch-self-repair.yaml` and compare `run_date` in the file to the current date. If they differ, the UI must communicate this.

**Phase to address:** Phase 4 (forge results display). Add staleness check before wiring the UI.

---

### Pitfall 8: HTM fragment syntax crash — adding wrapper-free multi-element returns in new components

**What goes wrong:**
This project has already hit this pitfall (documented in MEMORY.md: "htm fragment syntax: htm template literals do NOT support JSX `<>...</>` shorthand — produces undefined type that crashes Preact diff"). Any new component added for v4.0 (forge results panel, calibration table, trend chart section) that attempts to return two sibling elements without a wrapper will crash at runtime.

**Why it happens:**
HTM's template literal parser does not implement JSX fragment shorthand. `html\`<>...</>\`` evaluates to `html\`${undefined}...\``, which Preact's diff algorithm receives as an invalid vnode and either throws or silently drops the content.

**Consequences:**
New component renders nothing. No error in the console unless Preact's error boundary catches it. Component appears "not rendering" — developer wastes time checking imports and component registration before finding the real cause.

**Prevention:**
Always wrap multi-element returns in a `<div>` or use `html\`<${Fragment}>...<//>\``. The `Fragment` must be imported from `preact`. Check the import in the new component file:
```typescript
import { Fragment } from 'preact'
// Then: html`<${Fragment}><div>A</div><div>B</div><//>`
```

Simpler: just use a wrapper div. Position:fixed elements (toasts, overlays) can go in any parent without affecting layout.

**Detection:**
Component function returns `html\`<>...</>\`` — immediate red flag. Grep new component files for `html\`<>\`` before the phase ships.

**Phase to address:** All phases. This is a "new file" checklist item, not a phase-specific risk. Apply when writing any new frontend component.

---

### Pitfall 9: Calibration threshold changes must NOT be written back to `feedback.yaml` — they belong in a separate config layer

**What goes wrong:**
Auto-calibration computes a `current_threshold` per indicator. If this threshold is persisted into `feedback.yaml` alongside feedback entries, the file becomes both a log (append-only) and a config (read-modify-write). Concurrent writes from the feedback collection path (append) and the calibration update path (rewrite) create a race condition where the file is corrupted or one write silently overwrites the other.

**Why it happens:**
`writeYamlFile` in `yaml-store.ts` is a full overwrite (`Bun.write(filePath, stringify(data))`). If the calibration path calls `writeYamlFile(FEEDBACK_YAML_PATH, {...data, calibration_thresholds: ...})`, it rewrites the entire file. Any concurrent `appendFeedback` call that read the file before the calibration write will overwrite the calibration back to the old value.

**Consequences:**
Calibration thresholds are lost intermittently. User sees threshold change in the UI, but the next request returns the old threshold because an `appendFeedback` call overwrote it.

**Prevention:**
Keep `feedback.yaml` as append-only. Store computed thresholds in a separate file: `nightwatch-calibration.yaml`. The file is small (one entry per indicator, ~10–20 entries). Update it only from the health API layer, never from `feedback-store.ts`.

Alternatively: compute thresholds on-the-fly from `feedback.yaml` on every request (current approach) and never persist them — display only. This avoids the race entirely at the cost of re-computation on each request (acceptable at current scale).

**Detection:**
If a new PR adds `writeYamlFile(FEEDBACK_YAML_PATH, ...)` anywhere other than `appendFeedback`, that is the anti-pattern. Code review gate: no one should be calling `writeYamlFile` on `FEEDBACK_YAML_PATH` except `appendFeedback`.

**Phase to address:** Phase 2 (auto-calibration). Decide at the start: computed-only (no persist) vs. persisted-separately. Document the decision before writing any calibration persistence code.

---

## Minor Pitfalls

### Pitfall 10: Vendor module import path verification after adding new vendor files

**What goes wrong:**
The import map in `index.html` maps four specifiers to four vendor files. If a new vendor file is added (e.g., `preact-compat.module.js`) that internally imports from `/vendor/preact.module.js` but the actual vendor path is `/vendor/preact-core.module.js`, the import fails with a 404 at runtime. This is the pattern that broke `@preact/signals` in a previous milestone (MEMORY.md: "Vendor module import path verification: hardcoded import paths must match the import map").

**Prevention:**
After downloading any new vendor file, open it and search for all `import` statements. Verify each import path matches what is served. The current vendor files:
- `preact.module.js` — serves `preact`
- `preact-hooks.module.js` — serves `preact/hooks`
- `htm.module.js` — serves `htm/preact` (imports from `preact.module.js`)
- `signals.module.js` — serves `@preact/signals` (imports from `signals-core.module.js`)
- `signals-core.module.js` — serves the signals core

Any new file must be verified in this chain.

**Phase to address:** Any phase that adds a new vendor file. Low risk for v4.0 if no new vendor files are added (SVG-inline charts need no vendor additions).

---

### Pitfall 11: `health-api.ts` issues one `getRun()` call per run (up to 10 calls) on every health page load — no caching

**What goes wrong:**
`health-api.ts` calls `listRuns({ target })` then `getRun(r.id)` for each of the last 10 runs. With 3 targets on the health page, this is 30 individual file reads on every `GET /api/health/:target` call. The health page polls via `usePoll`. Each poll triggers one request per target.

**Why it happens:**
Each run stores its summary in a separate JSON file in the `runs/` directory. `getRun()` reads and parses one file per call. There is no summary index or cached aggregate.

**Consequences:**
At 3 targets with polling at 5s, this is ~60 file reads per minute from the health page alone. On macOS with SSD, each read is ~0.1ms. Total: ~6ms/minute. Negligible. But indicator history arrays are recomputed on every request, which means the health page shows different "histories" on back-to-back loads if the YAML parse produces different floating point results (it won't, but the computation is unnecessary).

**Prevention:**
For v4.0, no action needed — the overhead is immaterial. If the health page becomes a performance concern in v5.0, cache the `TargetHealthData` with a 60-second TTL keyed by `(target, lastRunId)`. Invalidate when a `run:completed` IPC event arrives.

**Phase to address:** Not in v4.0 scope. Document as a known limitation.

---

### Pitfall 12: `FeedbackEntry` has no deduplication — the same signal can accumulate multiple identical feedback entries

**What goes wrong:**
`appendFeedback` in `feedback-store.ts` always appends without checking for existing entries for the same `signal_id + verdict + source` combination. The external feedback collectors (`collectImplicitFeedback`, `collectPrReviewFeedback`) are called before each run. If a PR is merged but no new runs have cleared the signal from cooldown, the next 7 runs will each add `{ signal_id: X, verdict: 'accepted', source: 'pr_status' }` to `feedback.yaml`. The calibration computation then counts this as 7 accepted signals when it was one PR merge.

**Why it happens:**
The feedback collectors are designed as fire-and-forget. They don't check for existing entries before appending. The cooldown mechanism is in the NW skill's `improvement-log.md`, not in the feedback store.

**Consequences:**
Calibration data is inflated by repeat identical entries. A target that merged 1 PR (1 true accepted signal) will show 7 accepted entries → artificially high acceptance rate → threshold drops too fast.

**Prevention:**
Add a `deduplicate` step in `getCalibrationData()`: before computing rates, filter entries by `(signal_id, source)` keeping only the most recent entry per pair. This is a read-time dedup that doesn't require changing the append logic.

Alternatively (better long-term): add a pre-append check in `appendFeedback`: if an entry with the same `signal_id + source` exists with the same `verdict`, skip appending.

**Phase to address:** Phase 1 (feedback trend). The weekly bucketing fix from Pitfall 3 naturally mitigates this — multiple entries in the same week for the same signal collapse to a single rate. But the explicit dedup is still worth adding to `getCalibrationData()`.

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|----------------|------------|
| Feedback trend visualization | Fake 2-point history in health-api.ts (Pitfall 3) | Add weekly bucketing to `getCalibrationData()` first |
| Feedback trend visualization | Missing `history` field in `CalibrationData` type | Add to `shared/types.ts` before writing any chart component |
| Auto-calibration | Volatile threshold with small N (Pitfall 4) | Gate on minimum 10 feedback entries per indicator |
| Auto-calibration | Writing thresholds back to feedback.yaml (Pitfall 9) | Decision: computed-only. Document explicitly |
| Signal prioritization | No `priority_score` in type system (Pitfall 5) | Define data contract in `shared/types.ts` first |
| Signal prioritization | Confidence string → numeric mapping is ad-hoc | Codify: `high=3, medium=2, low=1` as a named constant |
| Forge results display | Stale `nightwatch-self-repair.yaml` (Pitfall 7) | Add `run_date` staleness check, never 404 on missing file |
| Forge results display | No existing API route for self-repair results | New route: `GET /api/forge/results` returns `{ run_date, stale, config_fixes, config_warnings }` |
| Per-indicator sparklines | SVG attribute casing (Pitfall 1) | Audit all SVG attributes in new components, use kebab-case |
| Per-indicator sparklines | HTM fragment syntax (Pitfall 8) | Never use `<>...</>` shorthand — use wrapper div |
| Any new vendor file | Second Preact instance (Pitfall 2) | No new vendor files needed for v4.0 — all charts are SVG-in-HTM |
| Any new vendor file | Import path mismatch (Pitfall 10) | Verify vendor file's internal imports match the served paths |

---

## Sources

- Direct codebase inspection: `app/frontend/components/sparkline.ts`, `line-chart.ts`, `health.ts`, `health-api.ts`, `feedback-store.ts`, `yaml-store.ts`, `shared/types.ts`, `frontend/index.html`, `frontend/vendor/` directory listing
- MEMORY.md (this project): htm fragment syntax pitfall, vendor module import path verification, Preact vendor bundling (esm.sh var collision), `signals.module.js` import chain
- Previous PITFALLS.md for v2.0: concurrent YAML write patterns, yaml-store.ts write semantics
- Preact documentation (WebSearch 2026-03-25): singleton requirement (`?external=preact`), SVG attribute behavior, import map necessity for no-build workflows
- `~/.claude/kc-plugins-config/nightwatch-self-repair.yaml`: actual file format verification for forge results display feature
- `~/.claude/kc-plugins-config/nightwatch-feedback.yaml`: current file size (35 lines / 1KB) establishing growth baseline
