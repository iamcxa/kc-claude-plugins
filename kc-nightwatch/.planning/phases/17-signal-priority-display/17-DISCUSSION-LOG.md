# Phase 17: Signal Priority Display - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-26
**Phase:** 17-signal-priority-display
**Areas discussed:** Score Computation, Score Display, Sort UX

---

## Score Computation

| Option | Description | Selected |
|--------|-------------|----------|
| signals/priority API lookup | Fetch existing API, build indicator→score map. Pure frontend. | ✓ |
| Client-side calculation | Fetch calibration + hardcode CONFIDENCE_WEIGHT, compute in frontend. | |
| Server-side (add to RunSummaryAction) | Modify type + API response, score computed at source. | |

**User's choice:** signals/priority API lookup
**Notes:** API already exists from Phase 15. Zero server-side changes needed.

---

## Score Display

| Option | Description | Selected |
|--------|-------------|----------|
| Score before confidence (0.72 high) | Number draws the eye first, text provides semantic context. | ✓ |
| Confidence before score (high 0.72) | Keeps original layout order, score supplements. | |
| Replace confidence label | Only numeric score, drops high/medium/low text. | |

**User's choice:** Score before confidence
**Notes:** Success criteria #2 requires score "alongside" confidence label — both must be present.

---

## Sort UX

| Option | Description | Selected |
|--------|-------------|----------|
| Pure sort, no visual extras | Sort descending by score. Number + order conveys priority. | ✓ |
| Gradient opacity | Lower score = more transparent. Subtle visual emphasis. | |
| Group by High/Medium/Low | Section headers per confidence tier. | |

**User's choice:** Pure sort
**Notes:** Phase 17 is v4.0's final phase — keep simple. Score display already communicates priority.

---

## Claude's Discretion

- Score prop passing strategy (prop vs inline)
- Priority fetch loading state handling
- Score decimal formatting

## Deferred Ideas

- Score-based visual grouping
- Score opacity gradient
- Score trend over time
- Configurable sort toggle
