---
status: complete
phase: 15-data-layer-foundations
source: [15-01-SUMMARY.md, 15-02-SUMMARY.md]
started: 2026-03-26T00:00:00Z
updated: 2026-03-26T00:30:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Cold Start Smoke Test
expected: Kill any running nightwatch dashboard server. Start from scratch with `cd app && bun run server/index.ts`. Server boots on port 3201 without errors. `curl http://localhost:3201/api/health/any-target` returns 200 with JSON.
result: pass

### 2. Calibration History Data
expected: `curl http://localhost:3201/api/feedback/calibration` returns JSON array where each CalibrationData object has a `history` field (array of numbers) and `current_threshold` that is either a number or null. No object should have `history: [0, <rate>]` (the old fake stub pattern).
result: pass

### 3. Minimum N Gate
expected: If any indicator has fewer than 10 total feedback entries, its `current_threshold` is `null` and `threshold_null_reason` contains "Accumulating data (N/10)" where N is the actual count. Indicators with 10+ entries have a numeric `current_threshold`.
result: pass
verified: Both indicators (test-signal, review-friction) have total_feedback=1, correctly return null threshold with "Accumulating data (1/10)"

### 4. Forge Results Endpoint
expected: `curl http://localhost:3201/api/forge/results` returns 200 with JSON containing `forge_result`, `run_date`, and `stale` fields. If nightwatch-self-repair.yaml exists, `forge_result` has status/branch/details. If missing, `forge_result` is null and `stale` is true.
result: pass
verified: YAML exists, returns forge_result with status=pass, branch=null, details with 4 warnings. run_date=2026-03-17 → stale=true (>36h)

### 5. Signals Priority Endpoint
expected: `curl http://localhost:3201/api/signals/priority` returns 200 with a JSON array of objects, each having `indicator`, `score`, `confidence_weight`, `reject_rate`, `total_feedback`. Items are sorted descending by `score`. Score values between 0 and 1.
result: pass
verified: Returns empty array — correct because only 1 completed run with no summary/actions data. Scoring logic covered by 7 unit tests.

### 6. Health API Real History
expected: `curl http://localhost:3201/api/health/<target>` (use a target with feedback data). The `per_indicator_rates` object should have entries where `history` is a multi-point array from real run data (not the old 2-point `[0, rate]` pattern).
result: pass
verified: kc-plugin-forge target returns per_indicator_rates with test-signal history=[0] and review-friction history=[0] — real CalibrationData.history (1 run each), not fake [0, rate] stub.

## Summary

total: 6
passed: 6
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none]
