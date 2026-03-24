# Project Research Summary

**Project:** Nightwatch Dashboard v4.0 — Flywheel Intelligence
**Domain:** Bun-native dashboard analytics — feedback trend visualization, auto-calibration, signal prioritization, forge results display, and enhanced sparklines added to existing Hono + Preact/HTM stack
**Researched:** 2026-03-25
**Confidence:** HIGH

## Executive Summary

Nightwatch Dashboard v4.0 is a subsequent milestone built on a complete v3.0 system. The five "flywheel intelligence" features all have their data sources already in place — `FeedbackEntry` records with timestamps in `feedback.yaml`, `CalibrationData` computed in `feedback-store.ts`, `nightwatch-self-repair.yaml` with forge results — but the dashboard either feeds fake stub data to existing chart components or does not surface the data at all. The recommended approach is purely additive: extend existing routes, services, and pages rather than building new pages or touching the worker layer. Zero new npm packages are required; all chart enhancements use inline SVG composing with the existing Preact/HTM pattern.

The key architectural insight is that the gap is wiring, not infrastructure. `LineChart` already accepts `values: number[]` — it is fed a fake `[0, current_rate]` two-point stub. `api.getCalibration()` is already defined but never called from the health page. `nightwatch-self-repair.yaml` has a stable `forge_result` block with no API endpoint reading it. The highest-complexity item (auto-calibration wiring back to the kc-nightwatch skill) is explicitly deferred to v4.1+ — v4.0 delivers display-only calibration surfacing, which requires no skill changes and reduces the milestone to a clean server+frontend additive build.

The three critical risks are: (1) the fake `[0, rate]` two-point history in `health-api.ts` must be replaced with real per-run bucketed rates before any trend visualization is built on top of it; (2) auto-calibration thresholds must be computed on-demand or persisted in a separate file — never written back to the append-only `feedback.yaml` which would create race conditions; and (3) Preact/HTM-specific pitfalls (SVG kebab-case attributes, HTM fragment syntax, vendor Preact singleton) are well-catalogued from previous milestones and must be applied as checklists when writing each new component.

## Key Findings

### Recommended Stack

**Zero new dependencies for v4.0.** The existing Bun + Hono + Preact/HTM + yaml stack handles all five features without additions.

**Core technologies (unchanged):**
- **Bun**: Runtime — already deployed, no version decisions needed
- **Hono**: HTTP framework — new routes follow existing `app.route('/api/x', routeFile)` pattern in `server/index.ts`
- **Preact + HTM**: Frontend — components use `html` tagged templates; Typescript transpiled via `Bun.Transpiler` at serve time
- **yaml (js-yaml)**: Runtime data store — `feedback.yaml`, `nightwatch-self-repair.yaml`, `nightwatch-targets.yaml` all read via existing `readYamlFile()` / `writeYamlFile()` helpers
- **SVG inline rendering**: All chart enhancements (area fill, gradient, target line) use browser-native SVG elements composing cleanly with `html` template literals

**Why no charting library:**
Chart.js requires `@kurkle/color` bare specifier (breaks the import map), uPlot is Canvas-based DOM mutation (incompatible with Preact's declarative render), D3 is 500KB+ and requires 8+ vendor files. The existing `Sparkline` (80x20 SVG polyline) and `LineChart` (240x80 SVG with axes) components already implement the right primitives — extending them with `<path>` area fill and `<linearGradient>` is 20 lines of TypeScript.

**New types needed in `shared/types.ts`:**
- `CalibrationState`: persisted EMA thresholds per indicator (if threshold persistence is chosen over compute-on-demand)
- `ForgeResult`: `{ status: 'pass'|'fail', branch: string|null, details: string }`
- `SelfRepairData`: superset of existing config_warnings return shape
- `SignalPriorityScore`: computed score per indicator (not persisted)
- `history: number[]` field addition to existing `CalibrationData` interface

### Expected Features

**P1 — Must ship (foundational + quick wins):**
- Feedback trend data fix — replace fake `[0, rate]` stub in `health-api.ts` with real per-run bucketed rates from `FeedbackEntry.run_id` correlation; this unblocks all trend visualization
- Forge results display — new `GET /api/forge/results` endpoint reading `nightwatch-self-repair.yaml` + `ForgeResultCard` component on health page; highest value-to-complexity ratio in v4.0
- Per-indicator rejection rate sparkline alongside value sparkline — depends on data fix; uses existing `Sparkline` component with inverted color logic via `RateSparkline` wrapper
- Sparkline tooltip — add SVG `<title>` element to `Sparkline` component; fully independent, zero data dependencies
- Calibration data table (display-only) — render `CalibrationData[]` as threshold/reject-rate table; `api.getCalibration()` already exists but is never called from the health page

**P2 — Ship if scope allows:**
- Signal prioritization (display sort only) — sort `ActionCard` list in run detail by `confidence_numeric × acceptance_rate`; frontend-only computation from existing `CalibrationData`
- Calibration threshold annotation on trend chart — dotted horizontal line at `current_threshold` on `LineChart`; depends on P1 data fix

**P3 — Defer to v4.1+:**
- Auto-calibration wiring to kc-nightwatch skill — propagating thresholds back into Phase 3 of the NW pipeline requires skill changes; out of app scope for v4.0
- Signal prioritization in pipeline execution (not just display order)
- Forge status badge on target card (nice-to-have, depends on P1 scope settling)

**Anti-features (explicitly excluded):**
- Rolling average trend smoothing — hides the step-function behavior of calibration changes
- Global aggregate reject rate chart across targets — mixes incomparable signal types
- Interactive zoom/pan for trend charts — overkill for 20–180 data points; no-build constraint anyway
- Historical threshold editing — defeats the auto-calibration purpose

### Architecture Approach

All v4.0 changes are in the server and frontend layers only — the worker is unchanged. The build is additive: 2 new route files (`routes/signals.ts`, or `routes/forge.ts`), 2-3 new frontend components (`CalibrationTable`, `SignalPriorityList`, `ForgeResultCard`), and targeted modifications to `health-api.ts`, `feedback-store.ts`, `pages/health.ts`, `pages/runs.ts`, `components/sparkline.ts`, and `lib/api.ts`.

**Major components and their v4.0 changes:**
1. `services/feedback-store.ts` — add `getFeedbackTrends()` bucketed by run_id + weekly rate aggregation
2. `routes/feedback.ts` — add `GET /api/feedback/trends`
3. `routes/forge.ts` (new) or extend `routes/health-api.ts` — `GET /api/forge/results` with staleness check
4. `routes/signals.ts` (new) — `GET /api/signals/priority` with 30-run window limit
5. `routes/health-api.ts` — extend history from 10→20 runs; add forge pass/fail stats to `TargetHealthData`
6. `components/sparkline.ts` — add optional `target?: number` for horizontal target line; add SVG `<title>` tooltip; add area fill via `<polygon>` or `<path>`
7. `components/calibration-table.ts` (new) — renders `CalibrationData[]` with threshold status
8. `components/signal-priority-list.ts` (new) — ranked recurring unresolved signals
9. `components/forge-result-card.ts` (new) — status badge, run date, details, branch link
10. `pages/health.ts` — wire all new endpoints; render new components in new sections
11. `pages/runs.ts` — sort actions by priority score; self-repair run label; quick-fix filter

### Critical Pitfalls

1. **Fake two-point history is the root dependency** — `per_indicator_rates[].history = [0, currentRate]` in `health-api.ts` must be fixed before building any trend visualization. Building chart UI on top of fake data produces misleading flat lines that users will trust. Fix: bucket `FeedbackEntry[]` by run_id → compute per-run reject rate per indicator → return real history array.

2. **Auto-calibration threshold volatility with small N** — The existing formula recomputes threshold on every request. With < 10 feedback entries, a single new rejected signal moves the threshold by ~5%. Add a minimum sample size gate (< 10 entries → return `current_threshold: null` with "Accumulating data (N/10)" display). Do NOT add EMA smoothing in v4.0 — gate is sufficient and simpler.

3. **NEVER write calibration thresholds back to `feedback.yaml`** — `feedback.yaml` is append-only via `appendFeedback`. Any path that calls `writeYamlFile(FEEDBACK_YAML_PATH, ...)` outside of `appendFeedback` creates a race condition with concurrent feedback collection. Decision: keep calibration as compute-on-demand (no persistence in v4.0). If persistence is needed later, use a separate `nightwatch-calibration.yaml`.

4. **SVG attribute casing in Preact/HTM** — Preact passes SVG attributes verbatim (not normalized like React). `strokeWidth` silently renders at browser default. Always use kebab-case: `stroke-width`, `fill-opacity`, `text-anchor`. The existing `sparkline.ts` and `line-chart.ts` are the correct reference models.

5. **HTM fragment syntax crash** — `html\`<>...</>\`` produces `undefined` in HTM and crashes Preact's diff. Never use JSX fragment shorthand. Use a wrapper `<div>` or `html\`<${Fragment}>...<//>\`` with `Fragment` imported from `preact`. This is a known recurring pitfall for this project.

## Implications for Roadmap

Research supports a 3-phase build ordered by data dependencies and risk level.

### Phase 1: Data Layer Foundations
**Rationale:** All chart UI depends on real data. Server-side endpoints must exist before frontend calls them. Zero-risk data changes first to establish confidence before complex aggregation.
**Delivers:** Real feedback trend data (replacing fake stub), forge results API endpoint with staleness handling, signal priority API endpoint, extended 20-run history window
**Addresses:** P1 features: feedback trend data fix, forge results endpoint, history extension
**Avoids:** Building chart UI on top of fake data; unbounded run history scan (hard-limit to 30 runs in signals endpoint); feedback.yaml write-back race condition

Build steps:
- Extend history window in `health-api.ts` (10→20 runs): 30 min, zero risk
- Add `getFeedbackTrends()` to `feedback-store.ts` + `GET /api/feedback/trends` route + `api.getFeedbackTrends()` method: 60 min
- Add `GET /api/forge/results` (or `/api/self-repair/latest`) with staleness check: 45 min
- Add `routes/signals.ts` with `GET /api/signals/priority` (30-run window) + register in `index.ts` + `api.getSignalPriority()`: 60 min

### Phase 2: Component Enhancements
**Rationale:** Self-contained component changes with no new API dependencies. Sparkline enhancements use already-available data (existing `Target.indicators[].target`). Frontend wiring of trend data replaces the fake stub once Phase 1 server work is proven.
**Delivers:** Sparkline with target line + area fill + tooltip; frontend wiring for real feedback trends on health page; calibration data table
**Addresses:** P1 features: sparkline tooltip, calibration display, per-indicator rejection rate sparkline; P2: threshold annotation on trend chart
**Avoids:** Breaking Sparkline's existing API (all new props are optional); Preact singleton violation (no new vendor files); SVG casing pitfalls (kebab-case audit before writing each component)

Build steps:
- `Sparkline` component: add optional `target?: number` prop + horizontal target line + SVG `<title>` tooltip + area fill: 45 min
- `pages/health.ts`: replace `[0, rate]` stub with real `api.getFeedbackTrends()` data: 45 min
- `components/calibration-table.ts` (new) + wire `api.getCalibration()` in health page: 45 min

### Phase 3: New Components and Full Integration
**Rationale:** New components built after their server APIs are proven working in Phase 1. Forge results card and signal priority list render in health page alongside calibration table. Runs page sort is independent of all above — can be done anytime.
**Delivers:** ForgeResultCard on health page, SignalPriorityList section, runs page priority sort + self-repair label, forge stats on TargetHealthData
**Addresses:** P1: forge results display, per-indicator rejection rate sparkline row; P2: signal prioritization display
**Avoids:** New page anti-pattern (all wired into health.ts + runs.ts); polling signal priority (load once on mount, refresh on `brief-ready` SSE only); HTM fragment crashes (wrapper div everywhere)

Build steps:
- `components/forge-result-card.ts` (new) + wire in `pages/health.ts`: 45 min
- `components/signal-priority-list.ts` (new) + wire in `pages/health.ts`: 45 min
- `pages/runs.ts`: sort actions by priority score, self-repair run label: 30 min
- `shared/types.ts` + `routes/health-api.ts`: optional forge stats on `TargetHealthData`: 30 min

### Phase Ordering Rationale

- Server before frontend: API endpoints must be curl-testable before wiring UI — avoids building UI against non-existent data shapes
- Zero-risk first: history window extension is a one-line change that immediately improves existing sparklines with no new code paths
- CalibrationTable before ForgeResultCard: calibration uses an existing API already defined in `api.ts`; ForgeResultCard requires a new server route
- Signal priority list last: requires both the server route from Phase 1 and the component from Phase 3; complexity justifies later placement
- Runs page sort anytime: pure frontend sort using existing `CalibrationData` already available — truly independent

### Research Flags

All three phases use well-documented patterns. No `/gsd:research-phase` is needed.

- **Phase 1 (Data Layer):** All server patterns established in existing codebase. New routes follow `routes/*.ts` pattern. New service functions follow `services/feedback-store.ts` pattern. Feedback bucketing by `run_id` is pure TypeScript array grouping — no external research needed.
- **Phase 2 (Component Enhancements):** Sparkline is a simple SVG component; adding optional props is standard. Health page fetch pattern established. Calibration API already wired in `api.ts` — only the consumer page changes.
- **Phase 3 (New Components):** ForgeResultCard, SignalPriorityList, CalibrationTable all follow the existing Preact/HTM component pattern. Signal scoring formula (`confidence_numeric × (1 - reject_rate)`) is pure arithmetic requiring no external research.

The one item worth a quick pre-implementation check: verify `gh` CLI auth works in the safehouse context before building forge result PR link rendering. `gh repo view --json url` is a safe test.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Zero new packages confirmed by direct library evaluation (uPlot Canvas incompatibility, Chart.js bare-specifier issue verified against GitHub issue #11592); existing vendor files confirmed functional |
| Features | HIGH | Derived from authoritative PROJECT.md v4.0 requirements + direct codebase inspection of all affected files; existing data shapes confirmed (FeedbackEntry.submitted_at, forge_result YAML schema) |
| Architecture | HIGH | ARCHITECTURE.md provides line-level specificity on all 8 build steps, file change matrix, and data flow diagrams; all integration points verified against current code |
| Pitfalls | HIGH | Mix of project-specific patterns from direct inspection (fake history stub location, calibration formula statelessness, YAML write-back race) + known HTM/Preact pitfalls from MEMORY.md with specific error descriptions |

**Overall confidence:** HIGH

### Gaps to Address

- **Per-run bucketing strategy**: ARCHITECTURE.md and PITFALLS.md both identify `FeedbackEntry.run_id` bucketing as the right approach; FEATURES.md identifies weekly time-bucketing as an alternative. Decision needed at Phase 1 start: run-id bucketing (shows run-aligned history, matches `health-api.ts` existing run-based structure) vs. weekly bucketing (more stable with irregular run cadence). Recommendation: run-id first since it aligns with the existing `history: number[]` shape populated from runs. Add weekly aggregation if users request smoother trend lines.

- **Calibration persistence decision**: STACK.md proposes EMA + persistence to `nightwatch-calibration.yaml`; PITFALLS.md recommends starting with compute-on-demand + minimum sample gate. These are not contradictory — gate first, EMA later. Document the decision explicitly before Phase 1 implementation so the calibration API response shape is stable.

- **ForgeResultCard placement**: ARCHITECTURE.md suggests health page as a sidebar panel; FEATURES.md notes config page is natural home since self-repair data comes from the same YAML as config warnings. Decision: health page (where users look for system health) vs. config page (where self-repair data already lives). Recommendation: health page — the self-repair result is a health indicator, not a configuration item.

## Sources

### Primary (HIGH confidence)
- Direct codebase inspection of `app/server/`, `app/worker/`, `app/frontend/`, `app/shared/` (2026-03-25)
- `services/feedback-store.ts`: existing aggregation logic, YAML schema, `getCalibrationData()` formula
- `routes/health-api.ts`: fake `[0, currentRate]` two-point history (confirmed location + behavior)
- `pages/health.ts`: existing render logic for sparklines and line charts
- `shared/types.ts`: FeedbackEntry, CalibrationData, TargetHealthData, IndicatorBaseline shapes
- `~/.claude/kc-plugins-config/nightwatch-self-repair.yaml`: actual file format for forge results display
- `~/.claude/kc-plugins-config/nightwatch-feedback.yaml`: current size (35 lines / 1KB, ~5 feedback entries)
- `.planning/PROJECT.md` v4.0 target features (authoritative)

### Secondary (MEDIUM confidence)
- `reference/ROADMAP.md`: v0.5 feature intentions confirm v4.0 alignment with planned direction
- MEMORY.md entries: HTM fragment syntax pitfall, vendor module import path verification, Preact singleton, Bun IPC patterns (all project-specific validated patterns)
- uPlot ESM verification (esm.sh/uplot@1.6.32) — Canvas-based incompatibility confirmed
- Chart.js bare specifier issue (GitHub #11592) — confirmed `@kurkle/color` import map problem
- Preact SVG docs — confirmed verbatim attribute passthrough (no camelCase normalization)
- PatternFly sparkline UX guidelines — directional + metric pairing patterns

### Tertiary (LOW confidence)
- RICE scoring model — confidence × success_rate prioritization framework (general pattern, adapted to NW domain)
- Smashing Magazine dashboard UX patterns — progressive disclosure via hover states

---
*Research completed: 2026-03-25*
*Ready for roadmap: yes*
