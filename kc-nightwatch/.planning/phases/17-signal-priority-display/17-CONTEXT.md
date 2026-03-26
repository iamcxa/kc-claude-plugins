# Phase 17: Signal Priority Display - Context

**Gathered:** 2026-03-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Sort run detail actions by priority score and display the score alongside the existing confidence label. Pure frontend work — uses existing `GET /api/signals/priority` endpoint from Phase 15.

</domain>

<decisions>
## Implementation Decisions

### Score Computation
- **D-01:** Use `GET /api/signals/priority` API lookup — fetch once, build `indicator → score` map, use for both sorting and display. No client-side computation, no server-side type changes.
- **D-02:** Actions with no matching indicator in the priority map get score 0 (sorted to bottom).
- **D-03:** API client needs new `api.getSignalPriority()` method returning `Promise<SignalPriorityItem[]>`.

### Score Display
- **D-04:** Score displayed as decimal (e.g., `0.72`) — not percentage. This is a computed weight × rate product, not a percentage.
- **D-05:** Score appears BEFORE confidence label: `0.72 high` — number first draws the eye, text provides semantic context.
- **D-06:** Score uses same color as confidence label (green for high, yellow for medium, muted for low).

### Sort Behavior
- **D-07:** Actions sorted descending by priority score. Higher score = more credible signal = appears first.
- **D-08:** Pure sort, no visual grouping or opacity changes. Score number + sort order is sufficient to convey priority.
- **D-09:** Sort happens in runs.ts before passing actions to ActionCard. ActionCard component itself is unchanged except for receiving and displaying score.

### Claude's Discretion
- Whether to pass score as a prop to ActionCard or compute inline in runs.ts render
- Handling of the priority fetch loading state (show unsorted initially, re-sort when data arrives vs wait)
- Score formatting (2 decimal places vs variable)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Frontend Components
- `app/frontend/pages/runs.ts` — Run detail view. Lines 196-204: `targetData.actions.map(action => <ActionCard>)` — this is where sort + score injection happens
- `app/frontend/components/action-card.ts` — ActionCard component. Line 84-86: confidenceColor logic. Line 98-106: collapsed header rendering with confidence badge

### API Layer
- `app/frontend/lib/api.ts` — Frontend API client. Needs new `getSignalPriority()` method
- `app/server/routes/signals.ts` — `GET /api/signals/priority` (Phase 15). Returns `SignalPriorityItem[]`

### Types
- `app/shared/types.ts` — `SignalPriorityItem` (line 196): `{ indicator, score, confidence_weight, reject_rate, total_feedback }`
- `app/shared/types.ts` — `RunSummaryAction` (line 91): has `indicator` field used for lookup, `assessment.confidence` for label

### Phase 15 Context
- `.planning/phases/15-data-layer-foundations/15-CONTEXT.md` — CONFIDENCE_WEIGHT mapping: high=1.0, medium=0.6, low=0.3

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `api.ts:get<T>()` — Generic fetch helper, trivial to add `getSignalPriority()`
- `ActionCard` confidenceColor logic (line 84-86) — already maps confidence to CSS vars, can reuse for score color

### Established Patterns
- Preact + HTM with inline styles
- State via `useState`, data fetching in `useEffect`
- API methods follow consistent pattern: `getX(): Promise<T> { return get<T>('/api/x') }`

### Integration Points
- `runs.ts` line 196-204 — actions rendering loop. Sort before `.map()` and pass score as additional prop or inline display
- `runs.ts` already has state for `selectedRun` — priority data fetch should key on run selection or load once globally

</code_context>

<specifics>
## Specific Ideas

- Priority map is global (not per-run), so fetch once when component mounts — not on every run selection
- Score format: `0.72` (2 decimal places, `score.toFixed(2)`)
- When signals/priority API returns empty array (no feedback data), all actions show score `0.00` and retain original order

</specifics>

<deferred>
## Deferred Ideas

- Score-based visual grouping (High/Medium/Low sections) — premature UI complexity
- Score opacity gradient (lower score = more transparent) — interesting but not in scope
- Score trend over time (how an indicator's priority score changes) — would need historical data
- Configurable sort toggle (sort by score vs original order) — no user need yet

</deferred>

---

*Phase: 17-signal-priority-display*
*Context gathered: 2026-03-26*
