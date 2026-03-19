---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: complete
stopped_at: Completed 04-full-flywheel/04-04-PLAN.md
last_updated: "2026-03-19T07:16:46Z"
progress:
  total_phases: 4
  completed_phases: 4
  total_plans: 15
  completed_plans: 15
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-18)

**Core value:** The closed-loop feedback flywheel — NW monitors, proposes, learns from feedback, and gets measurably better over time
**Current focus:** Phase 04 — full-flywheel

## Current Position

Phase: 04 (full-flywheel) — COMPLETE
Plan: 4 of 4 (gap closure 04-04 complete)

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
| Phase 03-flywheel-core P01 | 16min | 3 tasks | 13 files |
| Phase 03-flywheel-core P03 | 24min | 3 tasks | 10 files |
| Phase 03-flywheel-core P02 | 18 | 3 tasks | 9 files |
| Phase 03-flywheel-core P04 | 15 | 2 tasks | 8 files |
| Phase 03-flywheel-core P05 | 135s | 2 tasks | 3 files |
| Phase 04-full-flywheel P01 | 8 | 2 tasks | 7 files |
| Phase 04-full-flywheel P02 | 6 | 3 tasks | 12 files |
| Phase 04-full-flywheel P03 | 7min | 1 task (TDD) | 2 files |
| Phase 04-full-flywheel P04 | 5min | 1 task (TDD) | 4 files |

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
- [Phase 03-flywheel-core]: 03-01: Anthropic SDK as default chat backend — claude-haiku-4-5 for cost/speed balance; briefChat injects RunSummary into system prompt
- [Phase 03-flywheel-core]: 03-01: Fire-and-forget POST /message + SSE GET /stream — decouples HTTP lifecycle from LLM streaming
- [Phase 03-flywheel-core]: 03-01: Global subscribers Set<SSEWriter> in ipc.ts — mirrors run-scoped SSE fan-out pattern from Phase 2
- [Phase 03-flywheel-core]: 03-03: Calibration formula: threshold = clamp(0.1, 0.9, 0.5 + (rejectRate - 0.5) * 0.5) — half-rate adjustment toward reject direction
- [Phase 03-flywheel-core]: 03-03: Route ordering guard: /api/feedback/calibration MUST precede /api/feedback/:runId in Hono to avoid param capture
- [Phase 03-flywheel-core]: 03-03: checkLinearStatus is Phase 3 placeholder returning null — Linear MCP integration deferred to Phase 4
- [Phase 03-flywheel-core]: 03-02: withWriteLock in-memory Map per file key — serializes concurrent YAML writes, targets and safety lock independently
- [Phase 03-flywheel-core]: 03-02: Fail-open Haiku semantic check — Haiku unavailable => WARN verdict, save proceeds; config editor never gated by LLM availability
- [Phase 03-flywheel-core]: 03-02: /api/config/warnings registered before /api/config/:file — Hono param routes are greedy, ordering prevents capture
- [Phase 03-flywheel-core]: 03-02: Wizard Step 4 uses JSON.stringify preview — yaml package is server-side only; browser frontend uses JSON for target preview
- [Phase 03-flywheel-core]: summary.yaml is the handoff contract between NW-Claude skill (writer) and dashboard executor (reader)
- [Phase 03-flywheel-core]: executor.ts non-destructive fallback: only writes legacy phases_completed if skill did not produce summary.yaml
- [Phase 03-flywheel-core]: BaselineCard always visible (not collapsible) per CONTEXT.md Indicator Baseline Display decision
- [Phase 03-flywheel-core]: Static source-read TDD for executor wiring: Bun.file + regex avoids mocking safehouse/claude spawn while verifying production code path
- [Phase 03-flywheel-core]: Feedback block placement: after summary.yaml parse, before IPC dispatch, wrapped in try/catch — fire-and-forget, never blocks run completion
- [Phase 04-full-flywheel]: MCP SDK v1.27.1 _registeredTools is plain object (not Map) — tests use Object.keys() not tools.size
- [Phase 04-full-flywheel]: Plan spec says 13 tools but breakdown totals 12 (7+1+4) — implemented 12 specified tools
- [Phase 04-full-flywheel]: nw_submit_feedback validates signal_id from run history before appendFeedback (per CONTEXT.md locked decision)
- [Phase 04-full-flywheel]: healthData prop flow: app.ts fetches per-target health data on mount and passes down to Dashboard->Sidebar (no re-fetch per component)
- [Phase 04-full-flywheel]: LineChart Y-axis fixed 0-100% for reject rate — not auto-scaled so charts are visually comparable across indicators
- [Phase 04-full-flywheel]: 04-03: messages.create() replaces messages.stream() for tool_use — streaming API doesn't expose stop_reason/content blocks needed for tool routing
- [Phase 04-full-flywheel]: 04-03: MCP client lazy-init per session via getMcpClient() — stored in ChatSession.mcpClient, reused across messages, closed on killSession
- [Phase 04-full-flywheel]: 04-03: Mock reset order — killAllSessions() BEFORE mockClear() prevents close() counts bleeding across tests
- [Phase 04-full-flywheel]: 04-04: per_indicator_rates[indicator].history = [0, currentRate] — baseline-zero is the minimal floor for LineChart >= 2 points; keeps reject_rate scalar for backward compat

### Pending Todos

None yet.

### Blockers/Concerns

- Phase 3 (Chat): `--input-format stream-json` reliability threshold unknown — plan must include API fallback
- Phase 4 (MCP): `@hono/mcp` dual-transport (Streamable HTTP + legacy SSE) needs hands-on spike before planning
- Phase 4 (Health): Flywheel metrics only meaningful after Phase 3 produces several feedback cycles

## Session Continuity

Last session: 2026-03-19T03:19:44Z
Stopped at: Completed 04-full-flywheel/04-03-PLAN.md
Resume file: None
