# Phase 8: Schema + Safety Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-21
**Phase:** 08-schema-safety-foundation
**Areas discussed:** IPC state shape design, Per-target schedule config location, Migration & compatibility depth

---

## IPC State Shape Design

| Option | Description | Selected |
|--------|-------------|----------|
| Flat: active: Run[] | Minimal change from current shape. current?: Run becomes active: Run[]. Queue stays flat. Frontend filters by run.target when needed. Phase 9 worker groups internally but sends flat. | ✓ |
| Grouped: targets: Record<string, TargetState> | Worker sends per-target grouped state. Bigger Phase 8 blast radius (all consumers change), but Phase 11 target cards consume directly without filtering. | |
| Hybrid: flat active + target metadata | active: Run[] stays flat, add target_meta: Record<string, {schedule, queue_depth}> for per-target info. Two structures to sync. | |

**User's choice:** Flat: active: Run[]
**Notes:** User reviewed code preview showing the type change and Phase 11 usage pattern (`state.active.filter(r => r.target === name)`). Chose flat for minimal blast radius — per-target grouping is worker's internal concern.

---

## Per-Target Schedule Config Location

| Option | Description | Selected |
|--------|-------------|----------|
| targets.yaml + global fallback | Optional schedule.interval_hours on each target in nightwatch-targets.yaml. Targets without it inherit from app-config.yaml global schedule. Self-contained target definitions. | ✓ |
| Centralized in app-config.yaml | New `schedules:` section in app-config.yaml maps target names to intervals. All schedule info in one place, but target definitions split across two files. | |
| Only in targets.yaml (no global) | Every target must declare its own schedule. No fallback. Explicit but verbose. | |

**User's choice:** targets.yaml + global fallback
**Notes:** User reviewed YAML preview showing `schedule: { interval_hours: 6 }` nested under target definition alongside monitors/keywords. Matches GitHub Actions pattern (per-workflow schedule, org defaults).

---

## Migration & Compatibility Depth

| Option | Description | Selected |
|--------|-------------|----------|
| Clean break — update all | Change types.ts AND update all consumers (server ipc.ts, frontend api.ts, tests) in Phase 8. No shims. Tests pass with new shape. | ✓ |
| Additive + compat shim | Add active: Run[] alongside current?: Run. Worker sends both. Consumers migrate incrementally in Phases 9/11. | |
| Schema-only, defer consumer updates | Only change types.ts + activePids. Let Phase 9/11 update their own consumers. Smallest Phase 8 but tests won't pass. | |

**User's choice:** Clean break — update all consumers
**Notes:** User reviewed scope preview listing 7 change areas (types, executor, worker, server ipc, frontend api, AppConfigSchema, ~15 test files). Chose atomic clean break for consistency — no dual shapes, no shims.

---

## Claude's Discretion

- Zod backward compat strategy for `max_concurrent_runs` removal
- Test update ordering within plans
- Whether to pre-add Phase 10 types (`ActionOutcome`, `OutcomeItem`) in Phase 8
- `cleanupOldRuns` safety approach

## Deferred Ideas

None — discussion stayed within phase scope
