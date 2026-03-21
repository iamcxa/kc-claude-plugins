# Phase 9: Worker Parallel Execution + Scheduling - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-22
**Phase:** 09-worker-parallel-scheduling
**Areas discussed:** `__all__` target under parallelism, Per-target queue depth + conflict rules, Minimum interval enforcement strategy

---

## `__all__` Target Under Parallelism

| Option | Description | Selected |
|--------|-------------|----------|
| Immediate concurrent | __all__ enqueues N sub-runs, all N targets start immediately in parallel. Per-target isolation ensures same-target queuing still works. Total run time = max(target durations). | ✓ |
| Staggered (30s delay) | Spread out target starts by 30s each. Smooths resource usage but adds timer complexity. | |
| Keep serial for __all__ | __all__ runs targets one-at-a-time as today. Only explicitly different-target manual triggers run in parallel. | |

**User's choice:** Immediate concurrent
**Notes:** User reviewed preview showing 30min concurrent vs 75min serial. Chose concurrent — the whole point of v2.0.

---

## Per-Target Queue Depth + Conflict Rules

| Option | Description | Selected |
|--------|-------------|----------|
| Depth 1 + scheduled skip | Max 1 queued + 1 active per target. Manual trigger accepted if queue not full, rejected with message if full. Scheduled runs skip silently if target already has active or queued run. | ✓ |
| Unlimited queue | No queue limit. All triggers always queue. Simple but risks pile-up. | |
| Depth 2 + scheduled skip | Max 2 queued + 1 active. More buffer for manual overrides but arbitrary. | |

**User's choice:** Depth 1 + scheduled skip
**Notes:** User reviewed per-target queue diagram showing reject/skip scenarios. Chose depth 1 to prevent pile-up.

---

## Minimum Interval Enforcement Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Both: UI + scheduler | Config editor rejects with 400 error. Scheduler validates on startup and logs warning for direct YAML edits. Both use shared MIN_SCHEDULE_INTERVAL_HOURS constant. | ✓ |
| Config editor only | Frontend/server rejects on save. Worker trusts input. Doesn't catch direct YAML edits. | |
| Scheduler only | Worker validates on startup. Delayed feedback. | |

**User's choice:** Both (defense in depth)
**Notes:** User reviewed preview showing server-side 400 error + worker-side log.warn skip pattern.

---

## Claude's Discretion

- Queue data structure (`Map<string, Run[]>` vs alternatives)
- `processNextRun` → `processTarget()` refactoring approach
- `__all__` expansion timing (enqueue vs scheduler)
- SSE log routing under parallelism
- `cleanupOldRuns` interaction with per-target active runs

## Deferred Ideas

None — discussion stayed within phase scope
