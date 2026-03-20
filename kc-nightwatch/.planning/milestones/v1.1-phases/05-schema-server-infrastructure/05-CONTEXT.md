# Phase 5: Schema + Server Infrastructure - Context

**Gathered:** 2026-03-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Add `queued_at` timestamp to the Run type and set it on all 4 enqueue paths. Expose worker queue state via a new HTTP endpoint. Broadcast `run:failed` events on the global SSE channel. This is a data/API-only phase — no frontend changes.

</domain>

<decisions>
## Implementation Decisions

### queued_at Field
- Add `queued_at?: string` to `Run` interface in `shared/types.ts` (optional for backward compat with existing runs)
- Set `queued_at: new Date().toISOString()` in all 4 enqueue paths:
  1. `server/routes/api.ts` POST /api/runs (manual trigger)
  2. `server/routes/api.ts` POST /api/webhook (webhook trigger)
  3. `worker/scheduler.ts` interval trigger
  4. `__all__` expansion in worker executor (sub-runs pushed to queue)
- Existing runs in `nightwatch-runs.yaml` will have `queued_at: undefined` — frontend handles this gracefully (Phase 6 concern)

### Worker State Endpoint
- New endpoint: `GET /api/worker/state`
- Returns FULL worker state: `{ queue: Run[], current?: Run, schedule?: ScheduleConfig }`
- Implementation: store `lastWorkerState` in ipc.ts when `state` IPC message arrives (currently discarded at line 75-76), serve via new route
- Rationale: worker already sends all this data via IPC — filtering adds code without benefit; single-user app has no security concern

### run:failed SSE Broadcast
- Add `broadcastGlobal('run:failed', { run_id: msg.run_id, target, error: msg.error })` in ipc.ts run:failed handler (line 89-91)
- Symmetric with `run:completed` handler which broadcasts `brief-ready` with `{ run_id, summary }`
- Different event name (`run:failed` vs `brief-ready`), similar shape — frontend can handle both uniformly
- Need to resolve `target` from the run — either pass it through the IPC message or look it up from run store
- Keep `closeRunSubscribers(msg.run_id)` — run-scoped SSE cleanup still needed

### Claude's Discretion
- Whether to add `target` field to the `WorkerToServer` `run:failed` message type vs looking it up server-side
- Sort order of `listRuns` — currently by `started_at` desc; may want `queued_at` as fallback for queued runs
- Whether `GET /api/worker/state` needs any caching or just reads the latest IPC state

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Core types and data flow
- `app/shared/types.ts` — Run interface (add queued_at), IPC message types (WorkerToServer run:failed may need target field)
- `app/server/ipc.ts` — IPC handler, SSE fan-out, broadcastGlobal pattern (line 59-64), run:failed handler (line 89-91), state handler (line 75-76)
- `app/server/services/run-store.ts` — appendRun, listRuns, getRun — where runs are persisted to YAML

### Enqueue paths (all 4 must set queued_at)
- `app/server/routes/api.ts` lines 28-41 — POST /api/runs (manual), lines 66-78 — POST /api/webhook
- `app/worker/scheduler.ts` lines 21-34 — interval trigger creates Run without queued_at
- `app/worker/executor.ts` — `__all__` expansion (search for `__all__` handling, pushes sub-runs to queue)

### Research findings
- `.planning/research/SUMMARY.md` — Confirms zero new deps, queued_at as optional field, run:failed 1-line fix
- `.planning/research/ARCHITECTURE.md` — Integration points, lastWorkerState capture pattern

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `broadcastGlobal(event, data)` in ipc.ts — exact pattern needed for run:failed broadcast
- `readYamlFile` / `writeYamlFile` in yaml-store.ts — run persistence pattern
- `appendRun(run)` in run-store.ts — single place to ensure queued_at is set for API-triggered runs

### Established Patterns
- SSE events: run-scoped via `fanOutLogEvent` + global via `broadcastGlobal` — run:failed uses global
- IPC state: worker sends state on connect (state message), server should store it in module-level variable (like `workerStatus`, `lastHeartbeatAt`)
- Route registration: specific routes before param routes in Hono (route ordering lesson from Phase 3)

### Integration Points
- `server/routes/api.ts` — new GET /api/worker/state route (alongside existing /api/runs, /api/targets)
- `server/ipc.ts` handleWorkerMessage — modify state handler (store) and run:failed handler (broadcast)
- `shared/types.ts` Run interface — add queued_at field
- `worker/scheduler.ts` — set queued_at when creating scheduled runs
- Frontend `lib/api.ts` — will need `getWorkerState()` method (Phase 6, not Phase 5)

</code_context>

<specifics>
## Specific Ideas

No specific requirements — straightforward infrastructure following established patterns.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 05-schema-server-infrastructure*
*Context gathered: 2026-03-20*
