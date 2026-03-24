# Phase 15: Data Layer Foundations - Context

**Gathered:** 2026-03-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Server-only data layer changes: fix fake feedback trend history, add EMA calibration logic with minimum sample gate, add forge results and signal priority endpoints. No frontend/UI changes in this phase.

</domain>

<decisions>
## Implementation Decisions

### Trend Bucketing
- **D-01:** Per-run-id bucketing with 30-run window cap. Each run produces one data point in the history array. Cap at 30 to prevent unbounded array growth.
- **D-02:** History arrays populate from feedback.yaml entries grouped by run_id, with reject rate computed per-run per-indicator.

### EMA Calibration
- **D-03:** Replace raw all-time average (feedback-store.ts:83) with EMA smoothing, α=0.3. Formula: `threshold_new = α * current_rate + (1 - α) * threshold_old`.
- **D-04:** Minimum N gate: indicators with fewer than 10 feedback entries return `threshold: null` with a message "Accumulating data (N/10)". This prevents volatile thresholds from misleading users.
- **D-05:** α is hardcoded at 0.3 — not user-configurable. Premature configurability adds complexity with no user benefit at this stage.
- **D-06:** Threshold clamping range stays at [0.1, 0.9] (same as current formula).

### API Surface
- **D-07:** Trends data is added to the existing `GET /api/feedback/calibration` endpoint response (extend CalibrationData type with `history: number[]`). Same data source (feedback.yaml), natural co-location.
- **D-08:** New `GET /api/forge/results` endpoint — reads nightwatch-self-repair.yaml, returns forge_result block. Separate from /api/config/warnings because semantics differ (quality check ≠ config warning).
- **D-09:** New `GET /api/signals/priority` endpoint — aggregates last 30 runs' actions ranked by `confidence_weight × (1 - reject_rate)`. Returns sorted indicator list with scores.

### Forge Data Source
- **D-10:** Forge results read from `~/.claude/kc-plugins-config/nightwatch-self-repair.yaml` (same file as /api/config/warnings but different field). Always returns 200 — empty/missing file returns `{ forge_result: null, stale: true }`.

### Claude's Discretion
- Internal data structures for run-id bucketing (Map vs array approach)
- Error handling strategy for malformed feedback.yaml entries
- Confidence weight mapping (high=1.0, medium=0.6, low=0.3 or similar)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Feedback Data
- `app/server/services/feedback-store.ts` — CalibrationData computation, current threshold formula (line 83), getCalibrationData() function
- `app/shared/types.ts` — CalibrationData interface (needs history field), FeedbackEntry interface

### Health API
- `app/server/routes/health-api.ts` — Fake history stub at line 71 (`[0, rate]`), per_indicator_rates construction

### Forge/Self-Repair
- `app/server/routes/config.ts` — SELF_REPAIR_YAML_PATH constant, existing /api/config/warnings endpoint pattern

### Research
- `.planning/research/SUMMARY.md` — Synthesized research findings
- `.planning/research/PITFALLS.md` — 12 named pitfalls with file locations
- `.planning/research/ARCHITECTURE.md` — Integration points and build order

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `feedback-store.ts:getCalibrationData()` — Already groups by indicator and computes reject_rate. Extend this to include history.
- `feedback-store.ts:readYamlFile()` — Generic YAML reader, reusable for self-repair.yaml
- `config.ts:SELF_REPAIR_YAML_PATH` — Path constant for nightwatch-self-repair.yaml

### Established Patterns
- Hono routes in `app/server/routes/` — one file per domain (feedback.ts, health-api.ts, config.ts)
- Zod validation at API boundaries (used in feedback.ts, mcp-tools.ts)
- CalibrationData as flat interface with computed fields

### Integration Points
- `GET /api/feedback/calibration` — extend response shape (add history field to CalibrationData)
- `app/frontend/pages/health.ts` line 151 — consumes `per_indicator_rates[].history` (Phase 16 will use the real data)
- `app/frontend/components/sparkline.ts` — accepts `values: number[]` (Phase 16 feeds real history)

</code_context>

<specifics>
## Specific Ideas

- The fake `[0, rate]` history at health-api.ts:71 must be replaced with real per-run bucketed data from feedback.yaml
- EMA threshold replaces the linear formula at feedback-store.ts:83: `0.5 + (rejectRate - 0.5) * 0.5`
- Signal priority score: `confidence_weight × (1 - reject_rate)` where confidence maps to numeric weight

</specifics>

<deferred>
## Deferred Ideas

- Auto-calibration skill wire-up (propagating thresholds back to kc-nightwatch skill) — v4.1+
- Configurable EMA α via safety.yaml — premature until system has enough feedback data to evaluate responsiveness
- Historical trend export/download — no current need

</deferred>

---

*Phase: 15-data-layer-foundations*
*Context gathered: 2026-03-25*
