# Phase 8: Schema + Safety Foundation - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning

<domain>
## Phase Boundary

All shared types, IPC state shape, and schema migrations that every downstream phase (9-11) depends on are in place and correct. No new features — pure type system, IPC shape, and safety changes. Worker queue model and parallel execution are Phase 9.

</domain>

<decisions>
## Implementation Decisions

### IPC State Shape
- **D-01:** Flat array design — `current?: Run` becomes `active: Run[]` in the `WorkerToServer` state message
- **D-02:** Queue stays flat (`queue: Run[]`) — all targets mixed, same pattern as today
- **D-03:** Per-target grouping is the worker's internal concern (Phase 9) — IPC sends flat arrays, consumers filter by `run.target` when needed
- **D-04:** Schedule remains on the state message: `schedule?: ScheduleConfig` (global schedule, unchanged position)

### Per-Target Schedule Config
- **D-05:** Per-target schedule override lives in `nightwatch-targets.yaml` as optional `schedule: { interval_hours: N }` on each target
- **D-06:** Targets without a `schedule:` block inherit from `app-config.yaml` global schedule
- **D-07:** Merge logic in worker: `target.schedule?.interval_hours ?? globalConfig.schedule.interval_hours`
- **D-08:** Phase 8 adds the `schedule?` field to the `Target` type and Zod schema; Phase 9 implements the multi-timer scheduler that reads it

### Migration Strategy
- **D-09:** Clean break — update ALL consumers in Phase 8 (no compat shims, no dual shapes)
- **D-10:** `shared/types.ts`, `worker/executor.ts`, `worker/index.ts`, `server/ipc.ts`, `frontend/lib/api.ts`, and all affected tests update atomically
- **D-11:** `max_concurrent_runs` removed from `AppConfigSchema` — use `.strip()` or equivalent so old YAML files load without error
- **D-12:** `activePids` migrates from `Set<number>` to `Map<string, number>` (keyed by `run_id`) — cancel targets only the intended run

### Claude's Discretion
- Exact Zod strategy for backward-compatible YAML loading (`.strip()` vs `.passthrough()` vs pre-parse filter)
- Test file update ordering and grouping within Phase 8 plans
- Whether to add `ImplementationOutcome` and `ActionOutcome` types now (schema prep for Phase 10) or defer
- `cleanupOldRuns` safety fix approach (skip active run IDs vs move cleanup to startup only)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Type system
- `.planning/research/SUMMARY.md` — Architecture approach, critical pitfalls (especially Pitfalls 1, 5, 7), and file change matrix
- `.planning/research/ARCHITECTURE.md` — Detailed component analysis and data flow diagrams
- `.planning/REQUIREMENTS.md` — PARA-02 (activePids), PARA-03 (IPC state shape), SCHED-04 (per-target schedule)
- `.planning/ROADMAP.md` — Phase 8 success criteria (4 criteria that must be TRUE)

### Existing code (read before modifying)
- `app/shared/types.ts` — Current type definitions (WorkerToServer, AppConfigSchema, Run, Target, ScheduleConfig)
- `app/worker/executor.ts` — Current `activePids` Set and `killAllActive()`
- `app/worker/index.ts` — Current state message sending (`send({ type: 'state', queue, current })`)
- `app/server/ipc.ts` — Current `lastWorkerState` consumer
- `app/frontend/lib/api.ts` — Current `getWorkerState()` return type

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `AppConfigSchema` (Zod): already validates config — extend with `.strip()` for backward compat
- `activePids` in `executor.ts`: isolated module export — Map migration is self-contained
- `Target` interface in `types.ts`: already has optional fields (`path?`, `auth?`) — adding `schedule?` follows established pattern
- `ScheduleConfig` interface: exists for global schedule — per-target can reuse or extend

### Established Patterns
- IPC message union pattern (`WorkerToServer`): add new shape variant, all consumers switch on `type`
- Worker state broadcasting: `send({ type: 'state', ... })` called in 4 places in `worker/index.ts` — all must update
- Zod schema validation on startup: `AppConfigSchema.parse()` in `yaml-store.ts` — controls what fields are accepted
- Test pattern: `app/tests/` mirrors `app/` structure — each module has corresponding test file

### Integration Points
- `server/ipc.ts:10` — `lastWorkerState` type must match new WorkerToServer state shape
- `frontend/lib/api.ts:141-142` — `getWorkerState()` return type must match server response
- `server/services/mcp-tools.ts` — MCP tools that expose worker state
- `server/services/chat-manager.ts` — Chat tools that reference schedule config
- `app/tests/shared/types.test.ts:30-31` — Tests asserting `max_concurrent_runs` must be removed/updated

</code_context>

<specifics>
## Specific Ideas

- Research identified `activePids` Set→Map as the #1 safety-critical change — must land before any parallel execution code
- `max_concurrent_runs: z.literal(1)` is a compile-time blocker for existing users upgrading — remove with backward compat
- Preview showed per-target schedule in targets.yaml: `schedule: { interval_hours: 6 }` — self-contained target definitions

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 08-schema-safety-foundation*
*Context gathered: 2026-03-21*
