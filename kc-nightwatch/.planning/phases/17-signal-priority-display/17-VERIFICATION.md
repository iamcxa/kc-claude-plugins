---
phase: 17-signal-priority-display
verified: 2026-03-27T00:00:00Z
status: gaps_found
score: 2/5 must-haves verified
gaps:
  - truth: "GET /api/signals/priority?run_id=<id> returns per-run signal scores keyed by signal_id"
    status: failed
    reason: "Phase 17 route (signalPriorityRoutes) is shadowed by Phase 15 route (signalsRoutes). Both register GET /api/signals/priority. Hono first-match wins — signalsRoutes at line 169 handles all requests; signalPriorityRoutes at line 170 is never reached. Confirmed by live Hono test."
    artifacts:
      - path: "app/server/index.ts"
        issue: "signalsRoutes registered at line 169, signalPriorityRoutes at line 170 — duplicate path, first wins"
      - path: "app/server/routes/signals.ts"
        issue: "Phase 15 route also declares GET /api/signals/priority at line 14, ignores run_id param"
    missing:
      - "Remove or rename the Phase 15 /api/signals/priority route — or rename Phase 17 route to /api/signals/priority/run (different path)"
      - "Ensure signalPriorityRoutes is registered before signalsRoutes in server/index.ts, OR give each a unique path"

  - truth: "priorityMap in runs.ts is populated with signal_id-keyed entries after fetch"
    status: failed
    reason: "api.getSignalPriority() calls /api/signals/priority?run_id=<id> which is intercepted by Phase 15 signalsRoutes returning SignalPriorityItem[] (keyed by indicator, no signal_id field). runs.ts builds map[e.signal_id] where e is a SignalPriorityItem — e.signal_id is undefined. All map lookups miss."
    artifacts:
      - path: "app/frontend/pages/runs.ts"
        issue: "Lines 108-111: map[e.signal_id] = e — e.signal_id is undefined when Phase 15 response is received"
      - path: "app/frontend/lib/api.ts"
        issue: "Line 164: getSignalPriority() typed as Promise<SignalPriorityEntry[]> but runtime response is SignalPriorityItem[] due to route collision"
    missing:
      - "Fix route collision (see above gap) so Phase 17 route actually handles the request"

  - truth: "ActionCards display a score badge '0.72 high' format in the collapsed header"
    status: failed
    reason: "ActionCard renders score badge only when priorityScore !== undefined. Because priorityMap is always empty (route collision + type mismatch), priorityMap[action.signal_id]?.score is always undefined. Badge conditional at action-card.ts line 101 never fires."
    artifacts:
      - path: "app/frontend/components/action-card.ts"
        issue: "Line 101: priorityScore !== undefined check never true at runtime; badge never rendered"
    missing:
      - "Fix route collision so priorityMap is populated correctly"

  - truth: "Actions in run detail are sorted by priority score descending"
    status: failed
    reason: "Sort in runs.ts lines 212-215 uses priorityMap[a.signal_id]?.score ?? 0. All scores fall back to 0 because priorityMap is always empty. Sort is a no-op — original action array order is preserved."
    artifacts:
      - path: "app/frontend/pages/runs.ts"
        issue: "Lines 211-216: sort is no-op when priorityMap is empty (all scores 0, deterministic tie-break by signal_id)"
    missing:
      - "Fix route collision so priorityMap is populated with real scores"

  - truth: "SIG-01 score formula matches requirement: confidence_weight × (1 - reject_rate)"
    status: failed
    reason: "REQUIREMENTS.md SIG-01 specifies 'confidence weight × (1 - reject_rate)'. Phase 17 implementation uses 'confidence_weight × alignment_weight (closer_to_north_star)'. The Phase 17 PLAN frontmatter has requirements: [] — SIG-01 was never claimed. The formula divergence may be intentional design evolution, but it means the literal requirement as written is not satisfied."
    artifacts:
      - path: "app/server/services/signal-priority.ts"
        issue: "Lines 26-29: formula is confidence × alignment, not confidence × (1 - reject_rate)"
    missing:
      - "Either update REQUIREMENTS.md SIG-01 to reflect the confidence × alignment formula, OR update the service to implement confidence × (1 - reject_rate) using calibration data"
human_verification:
  - test: "Open run detail with completed run that has actions"
    expected: "ActionCards sorted by priority score descending, each card shows '0.XX confidence-level' badge in header"
    why_human: "Visual layout and sort order only verifiable in browser"
---

# Phase 17: Signal Priority Display Verification Report

**Phase Goal:** Run detail actions are sorted by priority score so the most credible signals appear first
**Verified:** 2026-03-27
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

The phase goal is NOT achieved. The core wiring between the Phase 17 route and the frontend is broken by a route registration collision. All four user-visible behaviors (route response, priorityMap population, score badge, sort order) fail as a consequence of a single root cause.

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | GET /api/signals/priority?run_id=<id> returns per-run scores keyed by signal_id | FAILED | Route shadowed by Phase 15 signalsRoutes (registered first at line 169). Hono first-match confirmed by live test. |
| 2 | priorityMap in runs.ts populated with signal_id-keyed entries | FAILED | Phase 15 response returns SignalPriorityItem[] with no signal_id field; map[e.signal_id] = map[undefined] |
| 3 | Score badge "0.XX high" renders in collapsed ActionCard header | FAILED | priorityScore is always undefined — badge conditional at action-card.ts line 101 never fires |
| 4 | ActionCards sorted by priority score descending | FAILED | All priorityMap lookups miss → scores all 0 → sort is no-op |
| 5 | SIG-01 formula: confidence_weight × (1 - reject_rate) | FAILED | Implementation uses confidence × alignment (closer_to_north_star); REQUIREMENTS.md specifies × (1 - reject_rate) |

**Score:** 0/5 truths verified (behaviors) | 2/5 artifacts verified (service + test exist and are correct in isolation)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `app/server/services/signal-priority.ts` | Priority scoring service | VERIFIED | Exists, 53 lines, real computation, not a stub |
| `app/server/routes/signal-priority.ts` | GET /api/signals/priority route | STUB (shadowed) | Exists but unreachable at runtime due to route collision |
| `app/tests/server/signal-priority.test.ts` | 14 unit tests | VERIFIED | Exists, all 14 pass, covers score math + sort + API |
| `app/shared/types.ts` — SignalPriorityEntry | Interface for Phase 17 response | VERIFIED | Exists at line 253 with correct shape |
| `app/frontend/lib/api.ts` — getSignalPriority() | Client method | PARTIAL | Method exists and is typed correctly, but calls wrong route at runtime |
| `app/frontend/pages/runs.ts` — priorityMap + sort | State + sorted rendering | PARTIAL | Code exists and is structurally correct, but data never arrives due to type mismatch |
| `app/frontend/components/action-card.ts` — priorityScore prop + badge | Score badge rendering | PARTIAL | Code exists and is correct in isolation, but badge never renders (score always undefined) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `server/index.ts` | `routes/signal-priority.ts` | `app.route('/', signalPriorityRoutes)` at line 170 | NOT_WIRED | Shadowed by signalsRoutes at line 169 — identical path, first match wins |
| `frontend/lib/api.ts` getSignalPriority() | Phase 17 route | GET /api/signals/priority?run_id= | NOT_WIRED | Request intercepted by Phase 15 signalsRoutes |
| `frontend/pages/runs.ts` priorityMap | `components/action-card.ts` priorityScore prop | `priorityMap[action.signal_id]?.score` | NOT_WIRED | priorityMap always empty; all lookups return undefined |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|--------------------|--------|
| `action-card.ts` (score badge) | `priorityScore` prop | `priorityMap[signal_id]?.score` in runs.ts | No — map always empty | DISCONNECTED |
| `runs.ts` (sort + ActionCard render) | `priorityMap` state | `api.getSignalPriority(selectedId)` | No — Phase 15 response has no signal_id field | HOLLOW_PROP |
| `signal-priority.ts` service | `actions` array | `getRun()` from run-store | Yes — reads real run data | FLOWING (in isolation) |
| `signal-priority.ts` route | response | `computePriorities()` from service | Yes — correct response shape | FLOWING (in isolation, never reached) |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Route collision check | `node -e "const {Hono}=require('./node_modules/hono/dist/index.js');const app=new Hono();app.get('/api/signals/priority',(c)=>c.json({from:'phase15'}));app.get('/api/signals/priority',(c)=>c.json({from:'phase17'}));app.request('/api/signals/priority?run_id=test').then(r=>r.json()).then(console.log)"` | `{ from: 'phase15' }` | FAIL — Phase 17 never reached |
| Unit tests pass | `bun test tests/server/signal-priority.test.ts` | 14 pass, 0 fail | PASS (isolated, correct) |
| Full suite no regressions | `bun test` | 450 pass, 0 fail | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| SIG-01 | VALIDATION.md (plan frontmatter: `requirements: []`) | Each action has numeric priority score = confidence_weight × (1 - reject_rate), sorted descending | BLOCKED | Route collision prevents runtime delivery. Formula also diverges: implementation uses confidence × alignment, not × (1 - reject_rate). PLAN.md did not claim SIG-01 in its requirements field. |

**Orphaned requirements check:** The VALIDATION.md per-task map lists SIG-01 for both task 17-01-01 and 17-01-02, but the PLAN frontmatter has `requirements: []`. SIG-01 is mapped to Phase 17 in REQUIREMENTS.md traceability table but not formally claimed by the plan. Flagged as discrepancy.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `app/server/index.ts` | 169–170 | Duplicate route path `/api/signals/priority` — two different route files both handle the same method+path | BLOCKER | Phase 17 route unreachable; all priority data served by Phase 15 route (wrong shape for Phase 17 consumers) |
| `app/frontend/pages/runs.ts` | 108 | `map[e.signal_id]` — TypeScript type is `SignalPriorityEntry` but runtime value is `SignalPriorityItem` (no signal_id field) | BLOCKER | priorityMap always empty at runtime; score badge and sort never work |

### Human Verification Required

#### 1. Score Badge Visual Appearance

**Test:** Open a run detail page with at least one completed run containing actions. Inspect ActionCard collapsed headers.
**Expected:** Each card shows a badge like "0.72 high" (numeric score + confidence level) in green/amber/muted color.
**Why human:** Visual rendering and color coding can only be verified in browser.

#### 2. Sort Order in Run Detail

**Test:** Trigger a nightwatch run and wait for completion. Open run detail. Check that ActionCards appear in descending order of priority score.
**Expected:** Higher-scored cards appear first. Cards with same score appear in signal_id alphabetical order.
**Why human:** Requires a live run with real action data to observe ordering.

---

## Gaps Summary

**Root cause: single route collision, cascading to four broken behaviors.**

`signalsRoutes` (Phase 15) and `signalPriorityRoutes` (Phase 17) both register `GET /api/signals/priority` on the Hono app. Hono first-match semantics mean Phase 15 handles every request — Phase 17 is dead code at runtime. A live test confirms `{ from: 'phase15' }` is always returned.

The consequence cascades:
- `api.getSignalPriority(runId)` receives `SignalPriorityItem[]` (keyed by `indicator`) instead of `SignalPriorityEntry[]` (keyed by `signal_id`)
- `runs.ts` builds `map[e.signal_id]` where `e.signal_id` is `undefined` in every Phase 15 response → `priorityMap` stays empty
- ActionCard never receives a defined `priorityScore` → score badge never renders
- Sort falls back to `score ?? 0` for every action → no reordering

**Secondary issue: formula divergence from SIG-01.**

REQUIREMENTS.md SIG-01 specifies `confidence_weight × (1 - reject_rate)`. The Phase 17 service implements `confidence_weight × alignment_weight (closer_to_north_star)`. The plan's `requirements: []` field did not claim SIG-01. This may reflect an intentional design choice captured in the DISCUSSION-LOG, but the requirement as written is not satisfied by the current formula.

**What works correctly in isolation:**
- `computePriorityScore()` and `computePriorities()` service functions are correct
- `signal-priority.ts` route returns correct shape when reached directly
- 14 unit tests for the service all pass (450 total, 0 fail)
- ActionCard score badge rendering code is correct when `priorityScore` is provided
- Sort logic in `runs.ts` is correct when `priorityMap` has data

**Minimum fix:** In `server/index.ts`, register `signalPriorityRoutes` before `signalsRoutes` (swap lines 169 and 170). This alone resolves the route collision and restores the data flow. The formula question is a separate design decision.

---

_Verified: 2026-03-27_
_Verifier: Claude (gsd-verifier)_
