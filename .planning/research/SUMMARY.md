# Project Research Summary

**Project:** kc-nightwatch Dashboard v4.0 — Flywheel Intelligence
**Domain:** Dashboard analytics — adding feedback trend visualization, calibration display, and signal prioritization to an existing Bun/Hono/Preact dashboard
**Researched:** 2026-03-25
**Confidence:** MEDIUM (ARCHITECTURE.md complete; STACK.md, FEATURES.md, PITFALLS.md not written)

## Executive Summary

Nightwatch Dashboard v4.0 is a subsequent milestone — not a greenfield build. The target system is an existing Bun + Hono server + Preact/htm frontend running on port 3201, with a worker process for nightly pipeline execution. v4.0 adds five "flywheel intelligence" features that surface feedback loop data to users: feedback trend visualization, auto-calibration display, signal prioritization, forge results display, and enhanced indicator sparklines. The recommended approach is purely additive — extend existing routes, services, and pages rather than creating new pages or restructuring the architecture.

The key architectural insight from research is that almost all the data needed already exists: the `nightwatch-feedback.yaml` store is append-only with timestamps, the calibration formula is already implemented in `feedback-store.ts`, and the `Sparkline`/`LineChart` components already accept the right data shapes. The gap is wiring — the frontend is either using stub data (two-point fake history) or not calling existing API methods at all. This means v4.0 is lower-risk than it appears: most work is connecting existing pieces rather than building new infrastructure.

The primary risk is scope creep on the Health page, which receives all five features. The research-recommended mitigation is explicit: extend `pages/health.ts` with new sections rather than creating new pages, load signal priority data once on mount (not on 5-second polling), and keep forge results display lightweight (filter in runs page + one stat in TargetHealthData). Full forge analytics belongs in v5.0+.

## Key Findings

### Recommended Stack

**Note:** STACK.md was not written by researcher agents. Stack is inferred from direct codebase inspection in ARCHITECTURE.md.

The project runs on an established, already-deployed stack:

**Core technologies:**
- **Bun**: runtime for server + worker + test runner — already in use, no version decision needed
- **Hono**: HTTP framework for server routes — route pattern is `app.route('/api/x', routeFile)` registered in `server/index.ts`
- **Preact + htm**: frontend components compiled to `app/frontend/` — `html` template literals, no JSX, Typescript transpiled via `Bun.Transpiler` at serve time
- **YAML (js-yaml)**: runtime data store for feedback, targets, runs — all data files under `~/.claude/kc-plugins-config/`
- **Bun native IPC**: server-to-worker communication via `ipc: true` spawn — simpler than Unix sockets, no file management

### Expected Features

**Note:** FEATURES.md was not written by researcher agents. Feature set is taken directly from ARCHITECTURE.md's v4.0 feature analysis.

**Must have (table stakes — core flywheel visibility):**
- Feedback trend visualization (real time-series per indicator, replacing fake `[0, current_rate]` stub)
- Auto-calibration display (show current thresholds + raise/lower/baseline status per indicator)
- Signal prioritization within runs (sort ActionCards by confidence + north-star alignment)
- Extended sparkline history (10 runs → 20 runs)

**Should have (completes the flywheel story):**
- Cross-run signal priority view (`GET /api/signals/priority` — recurring unresolved high-confidence signals)
- Sparkline target line (horizontal dashed line at target value for visual context)
- Forge results display in run detail (self-repair run label + quick-fix filter)

**Defer (v5.0+):**
- Full forge analytics (pass rate dashboards, forge-specific metrics)
- Per-indicator trend deep-dive pages
- Feedback history pagination (not needed until hundreds of entries)

### Architecture Approach

The existing architecture has three layers: server (Hono routes + YAML services), worker (executor + scheduler + auto-action), and frontend (Preact pages + components). v4.0 touches only the server and frontend layers — the worker is unchanged. The build strategy is additive: 2 new server route files (signals.ts), 2 new frontend components (CalibrationTable, SignalPriorityList), and modifications to health.ts, runs.ts, sparkline.ts, feedback-store.ts, and api.ts. No new pages, no worker changes.

**Major components modified:**
1. `routes/feedback.ts` — add `/api/feedback/trends` endpoint
2. `routes/signals.ts` (new) — `/api/signals/priority` with 30-run window limit
3. `services/feedback-store.ts` — add `getFeedbackTrends()` bucketed by run_id
4. `components/calibration-table.ts` (new) — renders CalibrationData[] as a table
5. `components/signal-priority-list.ts` (new) — ranked recurring signals
6. `components/sparkline.ts` — add optional `target?: number` prop for horizontal target line
7. `pages/health.ts` — wires all new data + renders new components
8. `pages/runs.ts` — sort actions by priority, self-repair run label

### Critical Pitfalls

**Note:** PITFALLS.md was not written by researcher agents. These pitfalls are extracted from the Anti-Patterns section of ARCHITECTURE.md, which provides the same protective function.

1. **New page per feature** — health.ts already has targets + health data; splitting to a new "Analytics" page fragments UX and duplicates API calls. Extend health.ts with sections instead.

2. **Polling signal priority on 5-second interval** — signal priority is derived from historical run data that only changes after a completed run. Use one-time mount load + refresh on `brief-ready` SSE event, not constant polling.

3. **Moving CalibrationData computation to worker** — calibration is a fast read-time aggregation (single YAML file + in-memory grouping). Making it a write-time artifact creates staleness. Keep `getCalibrationData()` in feedback-store.ts as on-demand aggregation.

4. **Breaking Sparkline's existing API** — Sparkline is used in multiple places. Make `target` optional (`target?: number`), never required. Default behavior must remain identical to current.

5. **Unbounded run history scan for signal priority** — run history grows indefinitely. Hard-limit `GET /api/signals/priority` to last 30 runs and document this explicitly. Add `?window=N` only when needed.

## Implications for Roadmap

Based on ARCHITECTURE.md's Suggested Build Order section, the research recommends an 8-step build sequence organized by data dependencies (server before frontend) and risk level (zero-risk changes first).

### Phase 1: Data Layer Foundations
**Rationale:** Server-side changes must exist before frontend can call them. Zero-risk changes (history window extension) come first to establish confidence.
**Delivers:** Extended sparkline history (10→20 runs), feedback trends API endpoint, signal priority API endpoint
**Addresses:** Must-have features: feedback trends + extended history
**Avoids:** Building frontend against non-existent APIs; the two-point stub history stays until real data is ready

Steps from ARCHITECTURE.md build order:
- Step 1: Extend history window in `health-api.ts` (30 min, zero risk)
- Step 3: `getFeedbackTrends()` in feedback-store.ts + `/api/feedback/trends` route + api.ts method (60 min)
- Step 6: `routes/signals.ts` new file + register in index.ts + `getSignalPriority()` in api.ts (60 min)

### Phase 2: Component Enhancements
**Rationale:** Self-contained component changes with no new API dependencies. Sparkline target line uses already-available data from existing `Target.indicators[].target`.
**Delivers:** Sparkline with target line, frontend wiring for feedback trends on health page
**Addresses:** Must-have: extended history display; should-have: sparkline target line
**Avoids:** Breaking Sparkline's existing API (make `target` optional)

Steps:
- Step 2: Sparkline target prop + `pages/health.ts` target pass-through (45 min)
- Step 4: `pages/health.ts` replace `[0, current_rate]` stub with real trend data (45 min)

### Phase 3: New Components and Integration
**Rationale:** New components (CalibrationTable, SignalPriorityList) built after their server APIs are proven working. Forge results display last — touches most files but all changes are additive.
**Delivers:** Calibration display, cross-run signal priority list, forge results filtering in runs page
**Addresses:** Should-have: calibration display, signal priority view, forge results display
**Avoids:** New page anti-pattern (all wired into health.ts + runs.ts)

Steps:
- Step 5: `components/calibration-table.ts` new + wire in health.ts (45 min)
- Step 7: `components/signal-priority-list.ts` new + wire in health.ts (45 min)
- Step 8: runs.ts sort + self-repair label + optional forge stats on TargetHealthData (45 min)

### Phase Ordering Rationale

- Server-before-frontend dependency: API endpoints must exist before frontend calls them (curl-testable intermediate state)
- Zero-risk-first: history window extension (Step 1) establishes confidence before complex aggregation (Step 6)
- CalibrationTable before SignalPriorityList: calibration uses an existing API already defined in api.ts; signal priority requires a new server route
- Forge display last: touches multiple files (types.ts, health-api.ts, runs.ts) but all changes are additive optional fields

### Research Flags

Phases with well-documented patterns (skip research-phase):
- **Phase 1 (Data Layer):** All server patterns are already established in the codebase. New routes follow existing `routes/*.ts` pattern; new service functions follow `services/feedback-store.ts` pattern.
- **Phase 2 (Component Enhancements):** Sparkline is a simple SVG component; adding an optional prop is straightforward. Health page fetch pattern is already established.
- **Phase 3 (New Components):** CalibrationTable and SignalPriorityList follow the existing component pattern (Preact + htm, typed fetch via api.ts).

No phases require deeper research — this is a subsequent milestone with well-understood existing code. The ARCHITECTURE.md provides sufficient implementation detail for all 8 build steps.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Inferred from direct codebase inspection; no version decisions needed (existing stack) |
| Features | HIGH | Derived from ARCHITECTURE.md's per-feature integration analysis; FEATURES.md not written but feature set is clear |
| Architecture | HIGH | ARCHITECTURE.md is thorough — existing system mapped, integration points identified per feature, component boundaries defined |
| Pitfalls | HIGH | Anti-patterns section in ARCHITECTURE.md covers the same ground as a dedicated PITFALLS.md would |

**Overall confidence:** HIGH for implementation decisions; MEDIUM overall because 3 of 4 research files were not written (though ARCHITECTURE.md compensates for FEATURES.md and partially for PITFALLS.md, the absence of STACK.md means no external best-practice validation was performed).

### Gaps to Address

- **No external stack research performed**: STACK.md was not written. For this milestone, this is acceptable — the stack is fixed (Bun/Hono/Preact already deployed). No new technology decisions are needed.
- **No community/best-practice validation for feedback trend bucketing strategy**: The ARCHITECTURE.md prescribes bucketing by `run_id` using `submitted_at` ordering. This is reasonable but unvalidated against alternatives (time-bucket by week, sliding window). If feedback volume is low (< 50 entries), bucketing by run_id is clearly correct. Validate assumption during Phase 1 implementation.
- **`getFeedbackTrends` performance with large feedback files**: ARCHITECTURE.md notes risk is LOW at current scale. Monitor on first implementation; if file grows beyond ~1000 entries, add server-side caching.

## Sources

### Primary (HIGH confidence)
- Direct code inspection of `app/server/`, `app/worker/`, `app/frontend/`, `app/shared/` (2026-03-25) — ARCHITECTURE.md
- `shared/types.ts`: FeedbackEntry, CalibrationData, TargetHealthData, IndicatorBaseline shapes
- `services/feedback-store.ts`: existing aggregation logic and YAML schema
- `routes/health-api.ts`: existing history construction (10-run window, fake two-point reject rate history)
- `pages/health.ts`: existing render logic for sparklines and line charts

### Secondary (MEDIUM confidence)
- `reference/ROADMAP.md`: v0.5 feature intentions (improvement-log analytics, reject ratio trends) — confirms v4.0 aligns with planned direction
- MEMORY.md entries on Nightwatch Dashboard development patterns (2026-03-18 through 2026-03-21)

### Not Available
- STACK.md — not written (acceptable: stack is fixed, no new technology decisions)
- FEATURES.md — not written (feature set inferred from ARCHITECTURE.md)
- PITFALLS.md — not written (anti-patterns captured in ARCHITECTURE.md)

---
*Research completed: 2026-03-25*
*Ready for roadmap: yes*
