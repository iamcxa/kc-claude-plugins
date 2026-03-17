# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-18)

**Core value:** The closed-loop feedback flywheel — NW monitors, proposes, learns from feedback, and gets measurably better over time
**Current focus:** Phase 1 — Foundation

## Current Position

Phase: 1 of 4 (Foundation)
Plan: 0 of 3 in current phase
Status: Ready to plan
Last activity: 2026-03-18 — Roadmap created (4 phases, 73 requirements mapped)

Progress: [░░░░░░░░░░] 0%

## Performance Metrics

**Velocity:**
- Total plans completed: 0
- Average duration: -
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| - | - | - | - |

**Recent Trend:**
- Last 5 plans: (none yet)
- Trend: -

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- All phases: Server + Worker two-process split — UI responsive during 30-min claude runs
- Phase 1: Use `node:net` Unix socket (not Bun native IPC) — worker-connects-to-server topology requires it
- Phase 3: Use Anthropic SDK as chat default — `--input-format stream-json` unreliable for long sessions
- Phase 3: Feedback buttons land in Phase 2 (Core Cockpit) — flywheel must be seeded from day one

### Pending Todos

None yet.

### Blockers/Concerns

- Phase 3 (Chat): `--input-format stream-json` reliability threshold unknown — plan must include API fallback
- Phase 4 (MCP): `@hono/mcp` dual-transport (Streamable HTTP + legacy SSE) needs hands-on spike before planning
- Phase 4 (Health): Flywheel metrics only meaningful after Phase 3 produces several feedback cycles

## Session Continuity

Last session: 2026-03-18
Stopped at: Roadmap written, requirements traced, STATE.md initialized
Resume file: None
