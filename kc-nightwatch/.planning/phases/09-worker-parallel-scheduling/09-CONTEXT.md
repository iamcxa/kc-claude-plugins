# Phase 9: Worker Parallel Execution + Scheduling - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Different targets execute concurrently in the worker, same-target runs queue behind each other, and each target has its own independently ticking scheduler. No server or frontend changes — pure worker internals. Server/frontend already consume `active: Run[]` from Phase 8.

</domain>

<decisions>
## Implementation Decisions

### `__all__` Target Behavior
- **D-01:** `__all__` expands to N per-target sub-runs that all start concurrently (not serially)
- **D-02:** Each sub-run enqueues into its own per-target queue — per-target isolation applies naturally
- **D-03:** Total `__all__` run time = max(target durations), not sum — ~30min instead of ~75min for 3 targets

### Per-Target Queue Rules
- **D-04:** Queue depth 1 per target — max 1 active + 1 queued run per target
- **D-05:** Manual trigger: accepted if queue slot available, rejected with clear message if full ("target already has a queued run")
- **D-06:** Scheduled trigger: skip silently if target already has an active or queued run (prevents scheduler pile-up)
- **D-07:** The flat IPC arrays (`active: Run[]`, `queue: Run[]`) already support multiple targets — no IPC shape changes needed

### Per-Target Scheduler
- **D-08:** Multi-timer model — `Map<string, Timer>` replacing single `schedulerTimer`
- **D-09:** Each target reads `target.schedule?.interval_hours ?? globalConfig.schedule.interval_hours` (merge logic from Phase 8 D-07)
- **D-10:** Updating one target's schedule restarts only that target's timer — other timers continue undisturbed (SC #4)
- **D-11:** `stopAllSchedulers()` must clear the full Map before rebuilding (Pitfall 3 from research)

### Minimum Interval Enforcement
- **D-12:** Defense in depth — enforced at BOTH config editor (server) AND scheduler startup (worker)
- **D-13:** Config editor: `PUT /api/targets/:name` rejects with 400 if `interval_hours < MIN_SCHEDULE_INTERVAL_HOURS`
- **D-14:** Scheduler: `startPerTargetScheduler()` logs warning and skips timer for targets with interval below minimum — other targets unaffected
- **D-15:** Both use shared `MIN_SCHEDULE_INTERVAL_HOURS` constant (1/6 ≈ 10 minutes, from Phase 8)

### Claude's Discretion
- Queue data structure choice (`Map<string, Run[]>` vs alternatives)
- How to handle `processNextRun` → per-target `processTarget()` refactoring
- Whether `__all__` expansion happens at enqueue time or scheduler time
- SSE log routing (if needed — all per-run SSE already has `run_id`)
- `cleanupOldRuns` interaction with per-target active runs

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Worker execution model
- `.planning/research/SUMMARY.md` — Architecture approach: `Map<string, Run[]>` queue model, `processTarget()` pattern, `sendState()` consolidation
- `.planning/research/ARCHITECTURE.md` — Detailed data flow diagrams, file change matrix
- `.planning/research/PITFALLS.md` — Pitfalls 3 (timer leak), 4 (concurrent YAML writes), 8 (schedule IPC wipes timers), 9 (SSE cross-contamination)
- `.planning/REQUIREMENTS.md` — PARA-01 (per-target queue isolation), SCHED-05 (minimum interval)
- `.planning/ROADMAP.md` — Phase 9 success criteria (5 criteria)

### Phase 8 decisions (carry forward)
- `.planning/phases/08-schema-safety-foundation/08-CONTEXT.md` — D-01 (flat IPC), D-03 (per-target grouping is worker internal), D-05-08 (schedule config location + merge logic)

### Existing code (read before modifying)
- `app/worker/index.ts` — Current serial queue model (`activeRun`, `queue`, `processNextRun`, `enqueue`, `sendState`)
- `app/worker/scheduler.ts` — Current single-timer model (`schedulerTimer`, `startScheduler`, `stopScheduler`)
- `app/worker/executor.ts` — `executeRun()`, `activePids` Map, `cleanupOldRuns()` — NOT modified by Phase 9
- `app/shared/constants.ts` — `MIN_SCHEDULE_INTERVAL_HOURS`, `SCHEDULER_RUNS_ALL_TARGET`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `sendState()` in `worker/index.ts`: Already emits flat `active: Run[]` — just needs to collect from all per-target active runs
- `enqueue()` in `worker/index.ts`: Entry point for all run triggers — becomes the routing layer to per-target queues
- `executeRun()` in `executor.ts`: Unchanged — takes a single Run, spawns `claude -p`, manages PID. Phase 9 just calls it from multiple per-target queues concurrently
- `resolveTarget()` in `worker/index.ts`: Already resolves target name → PolicyTarget path
- `MIN_SCHEDULE_INTERVAL_HOURS` in `constants.ts`: Ready for validation logic

### Established Patterns
- Worker uses `process.on('message')` switch for IPC — `schedule` case already exists, extend for per-target
- `startScheduler(config, enqueue)` pattern — extend to `startPerTargetSchedulers(targets, globalConfig, enqueue)`
- `__all__` expansion already exists at lines 78-103 of `worker/index.ts` — refactor to use per-target enqueue

### Integration Points
- `server/routes/schedule.ts` — `PUT /api/schedule` sends `schedule` IPC to worker; per-target interval enforcement adds here
- `server/services/yaml-store.ts` — `readTargets()` provides target definitions with `schedule?` field
- `server/routes/api.ts` — Target CRUD endpoints (`PUT /api/targets/:name`) for interval validation
- `sendState()` — Already correct shape (`active: Run[]`); just needs to collect from all per-target actives

</code_context>

<specifics>
## Specific Ideas

- Research identified `Map<string, Run[]>` + `Map<string, Run | null>` as the per-target queue model — zero new dependencies
- Current `__all__` expansion (lines 78-103) is the natural place to route into per-target queues
- `sendState()` consolidation from Phase 8 means only ONE function needs updating to collect all active runs
- STATE.md blocker note: "Audit which files kc-nightwatch skill writes during a run before enabling parallel spawning" — address as a pre-execution audit task

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 09-worker-parallel-scheduling*
*Context gathered: 2026-03-22*
