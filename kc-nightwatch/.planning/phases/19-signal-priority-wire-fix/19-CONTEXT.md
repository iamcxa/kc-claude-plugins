# Phase 19: Signal Priority Wire Fix - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning
**Source:** Gap closure from v4.0-MILESTONE-AUDIT.md

<domain>
## Phase Boundary

Phase 17 created a signal priority scoring service (`signal-priority.ts`) and route (`signal-priority.ts` in routes/) that are correct in isolation but never wired into the application. The integration checker found 3 coordinated breaks that cascade into a fully broken "run detail priority display" flow. This phase fixes the wiring + resolves a formula divergence in REQUIREMENTS.md.

**Root cause:** GSD executor worktree-drift — Phase 17 was executed in an isolated worktree that didn't see Phase 15's `signalsRoutes` already occupying `/api/signals/priority`. The executor created correct files but missed registration in `server/index.ts`.

</domain>

<decisions>
## Implementation Decisions

### Break 1: Route Registration (server/index.ts)
- `signalPriorityRoutes` is completely absent from `server/index.ts` — never imported, never registered
- Current state (line 24-25): only `forgeRoutes` and `signalsRoutes` imported
- Current state (line 167-168): only `forgeRoutes` and `signalsRoutes` registered
- **Fix:** Import `signalPriorityRoutes` from `./routes/signal-priority.ts` and register BEFORE `signalsRoutes` (Hono first-match semantics)
- **Alternative (preferred):** Give Phase 17 route a distinct path `/api/signals/priority/run` to eliminate collision entirely. This is cleaner — no ordering dependency. Update the route file to use `/api/signals/priority/run` instead of `/api/signals/priority`.

### Break 2: API Client (api.ts)
- Current: `getSignalPriority(): Promise<SignalPriorityItem[]>` at line 164 — no `runId` param, returns Phase 15 type
- **Fix:** Change to `getSignalPriority(runId: string): Promise<SignalPriorityEntry[]>` calling the new path
- Import `SignalPriorityEntry` instead of using `SignalPriorityItem` for this method

### Break 3: Frontend Mapping (runs.ts)
- Current (line 107, 128): `api.getSignalPriority()` called without `runId`
- Current (line 109, 130): `map[item.indicator] = item.score` — maps by `indicator` (Phase 15 shape)
- Current (line 213-214): sort uses `priorityMap[a.indicator]`
- **Fix:** Pass `selectedId` to `getSignalPriority(selectedId)`, map by `item.signal_id`, sort by `priorityMap[a.signal_id]`
- ActionCard already receives `priorityScore` prop correctly — just needs data to arrive

### Formula Divergence (SIG-01)
- REQUIREMENTS.md: `confidence_weight × (1 - reject_rate)`
- Implementation: `confidence_weight × alignment_weight (closer_to_north_star)`
- **Decision: Update REQUIREMENTS.md** to match the implementation. The `alignment_weight` formula is a design evolution that uses the run's own assessment data (available per-action) rather than requiring cross-referencing with calibration data. This is simpler and more accurate for per-action scoring. Update the SIG-01 description to: "Each action has a numeric priority score computed as confidence weight × alignment weight (closer to north star), sorted descending."

### Orphan Cleanup
- `app/shared/types.ts` line 253: `SignalPriorityEntry` — duplicate of the one in `signal-priority.ts` service. Remove from types.ts since the service's local definition is authoritative and the route imports from the service.
- After fixing route registration, the `signal-priority.ts` route and service files are no longer orphans.

### Claude's Discretion
- Test file updates for the new route path
- Whether to add integration tests for the full priority flow

</decisions>

<canonical_refs>
## Canonical References

### Audit Findings
- `.planning/v4.0-MILESTONE-AUDIT.md` — SIG-01 gap details, integration breaks

### Phase 17 Artifacts
- `.planning/phases/17-signal-priority-display/17-VERIFICATION.md` — Detailed gap analysis with cascade description
- `.planning/phases/17-signal-priority-display/17-01-PLAN.md` — Original plan for signal priority

### Key Implementation Files
- `app/server/index.ts` — Route registration (lines 24-25, 167-168)
- `app/server/routes/signal-priority.ts` — Phase 17 route (correct in isolation, 30 lines)
- `app/server/services/signal-priority.ts` — Phase 17 service (correct, 53 lines)
- `app/frontend/lib/api.ts` — getSignalPriority() at line 164
- `app/frontend/pages/runs.ts` — priorityMap at line 61, mapping at lines 107-130, sort at lines 213-214
- `app/frontend/components/action-card.ts` — priorityScore prop at line 12, badge at line 101-105
- `app/server/routes/signals.ts` — Phase 15 route (the one that currently handles /api/signals/priority)
- `app/shared/types.ts` — SignalPriorityItem (line 196), SignalPriorityEntry (line 253, to remove)
- `app/tests/server/signal-priority.test.ts` — 14 tests (all pass in isolation)

</canonical_refs>

<specifics>
## Specific Ideas

- The route path change from `/api/signals/priority` to `/api/signals/priority/run` is cleaner than registration order because:
  1. No hidden ordering dependency in server/index.ts
  2. Semantically clearer: Phase 15's `/api/signals/priority` returns aggregate data, Phase 17's `/api/signals/priority/run` returns per-run data
  3. Both routes can coexist without conflict
- ActionCard component needs zero changes — it already handles `priorityScore` prop correctly
- The full cascade fix is: route path → API client → frontend mapping → done

</specifics>

<deferred>
## Deferred Ideas

None — this phase is scoped to wiring fix only.

</deferred>

---

*Phase: 19-signal-priority-wire-fix*
*Context gathered: 2026-03-27 via gap closure audit*
