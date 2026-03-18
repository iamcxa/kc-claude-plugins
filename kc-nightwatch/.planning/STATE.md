---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: Phase 2 approved — IPC heartbeat fix applied, all human checks passed, 104 tests green
stopped_at: Phase 3 context gathered
last_updated: "2026-03-18T08:01:16.081Z"
last_activity: "2026-03-18 — Phase 02 approved: IPC heartbeat fix (c582fae), all 5 human checks passed"
progress:
  total_phases: 4
  completed_phases: 2
  total_plans: 6
  completed_plans: 6
  percent: 50
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-18)

**Core value:** The closed-loop feedback flywheel — NW monitors, proposes, learns from feedback, and gets measurably better over time
**Current focus:** Phase 3 — Flywheel Core

## Current Position

Phase: 2 of 4 (Core Cockpit) — COMPLETE
Next: Phase 3 (Flywheel Core)
Status: Phase 2 approved — IPC heartbeat fix applied, all human checks passed, 104 tests green
Last activity: 2026-03-18 — Phase 02 approved: IPC heartbeat fix (c582fae), all 5 human checks passed

Progress: [█████░░░░░] 50% (Phase 2 complete, Phase 3 next)

## Performance Metrics

**Velocity:**
- Total plans completed: 4
- Average duration: 6.5 min
- Total execution time: 0.43 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-foundation | 3/3 | 32 min | 10.7 min |
| 02-core-cockpit | 3/3 | 96 min | 32 min |

**Recent Trend:**
- Last 5 plans: 01-02 (2 min), 01-03 (15 min), 02-01 (6 min), 02-02 (6 min), 02-03 (~90 min)
- Trend: Phase 2 in progress — frontend plan was larger due to checkpoint + 2 fix rounds

*Updated after each plan completion*
| Phase 02-core-cockpit P02 | 6min | 2 tasks | 7 files |
| Phase 02-core-cockpit P03 | ~90min | 3 tasks | 17 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- All phases: Server + Worker two-process split — UI responsive during 30-min claude runs
- Phase 1 (UPDATED 2026-03-18): Bun native IPC confirmed — NOT node:net Unix socket; CONTEXT.md decision locks this
- 01-01: Heartbeat timeout 90s (3 missed intervals) — safe buffer for system sleep/throttle
- 01-01: Zod v3 pinned explicitly — bun auto-installs v4 which has breaking API changes
- Phase 3: Use Anthropic SDK as chat default — `--input-format stream-json` unreliable for long sessions
- Phase 3: Feedback buttons land in Phase 2 (Core Cockpit) — flywheel must be seeded from day one
- [Phase 01-foundation]: PolicyTarget is minimal (name + resolved_path + optional extra_plugin_dirs) — full Target type deferred to Phase 2
- [Phase 01-foundation]: Force-kill uses RESULT_FORCE_KILL_DELAY_MS constant (not hardcoded 10_000) — GitHub #25629 workaround
- 01-03: Bun.file handle stale after write — always re-create handle for read (not reuse pre-write object)
- 01-03: tokenAuth applied at app.use('*') before app.route() — Hono order enforces auth before routing
- 01-03: cleanupOrphans called at boot AND crash recovery — prevents zombie accumulation on repeated crashes
- 02-01: RunSummary phases_completed kept as optional backward-compat field — executor.ts Phase 1 code compiles without migration
- 02-01: SSE subscribers stored as Map<runId, Set<SSEWriter>> — O(1) lookup, auto-cleaned on run:completed/run:failed
- 02-01: readTargets() normalizes both old and new field names at read time — Appendix A compat, no migration needed
- 02-01: writeAppConfig() always re-creates Bun.file handle (Pitfall: stale handle after write, per 01-03 lesson)
- [Phase 02-core-cockpit]: 02-02: ScheduleConfig.self_repair_before is required (not optional) — test configs must include it explicitly
- [Phase 02-core-cockpit]: 02-02: __all__ target expanded inline in processNextRun (sub-runs pushed to queue, drain chain handles them)
- [Phase 02-core-cockpit]: 02-02: ensureNwMemoryDir + writeNwJournalConfig exported from executor.ts for independent unit testing
- [Phase 02-core-cockpit]: 02-03: Preact vendor split — single-file esm.sh bundle has duplicate 'var V'; split into core + hooks separate files
- [Phase 02-core-cockpit]: 02-03: Bun serveStatic serves .ts with text/plain MIME — must use custom Bun.Transpiler route with Content-Type: application/javascript
- [Phase 02-core-cockpit]: 02-03: No-bundler architecture validated — import maps + vendored ESM + Bun transpile = full Preact app, zero build tooling

### Pending Todos

None yet.

### Blockers/Concerns

- Phase 3 (Chat): `--input-format stream-json` reliability threshold unknown — plan must include API fallback
- Phase 4 (MCP): `@hono/mcp` dual-transport (Streamable HTTP + legacy SSE) needs hands-on spike before planning
- Phase 4 (Health): Flywheel metrics only meaningful after Phase 3 produces several feedback cycles

## Session Continuity

Last session: 2026-03-18T08:01:16.075Z
Stopped at: Phase 3 context gathered
Resume file: .planning/phases/03-flywheel-core/03-CONTEXT.md
