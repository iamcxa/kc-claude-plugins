# Phase 1: Foundation - Context

**Gathered:** 2026-03-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Two-process architecture (Hono server + Bun worker) that starts, stays up across crashes, and handles every process-lifecycle failure mode. No features, no UI — only infrastructure that all subsequent phases build on. Includes security defaults (localhost binding + optional remote token auth).

</domain>

<decisions>
## Implementation Decisions

### CLI Interface
- Single entry point: `bun run app/server/index.ts` spawns both server and worker
- Server process is the parent; worker is spawned as child process
- Flags: `--port` (override yaml), `--host` (for remote), `--token` (remote auth)
- package.json scripts: `start` (production), `dev` (bun --watch for hot reload)
- mprocs-friendly: one process to manage, stdout captured by terminal
- No separate `stop` command — kill server → graceful shutdown handles worker

### Crash Behavior
- Worker auto-restart with exponential backoff: 2s, 5s, 15s (3 attempts)
- After 3rd crash: stop retrying, server enters read-only mode
- Dashboard shows "Worker offline" banner when worker is down
- Manual restart via page refresh or POST /api/worker/restart
- Server stays up regardless — last run results always viewable
- Orphaned safehouse+claude processes cleaned up on each crash recovery

### Logging
- Structured JSON to stdout: `{"ts":"...","level":"info","component":"server|worker","msg":"..."}`
- Worker stdout piped to server, forwarded to mprocs terminal
- Default level: INFO, --verbose flag for DEBUG
- File rotation: app/logs/nightwatch.log (5 files × 10MB) for post-mortem
- Custom 10-line structured logger — no external logging library

### IPC Transport
- **Bun native IPC** (`Bun.spawn` with `ipc: true`), NOT `node:net` Unix socket
- Server is parent, worker is child — matches Bun IPC direction naturally
- `proc.send()` / `process.on('message')` with JSON serialization
- Eliminates socket file management, EADDRINUSE risk, and FOUND-04 complexity
- Overrides design spec Appendix C (which specified Unix socket) — simpler, zero dependencies
- Heartbeat: worker sends heartbeat every 30s via IPC; server marks offline if >60s stale

### Claude Process Lifecycle
- Force-kill claude child process within 10s after receiving `{"type":"result"}` event
- PID tracking: store claude PIDs in memory (not file) — worker has direct handle
- Orphan scan on startup: `pgrep -f "safehouse.*claude"` to find zombies from prior crash
- Timeout from safety.yaml `max_runtime_minutes` (default 30min)

### Security Defaults
- Bind to 127.0.0.1 by default
- Remote mode: explicit --host 0.0.0.0 + --token required
- Token checked on all routes (API, SSE, WebSocket, MCP) when remote mode active
- Bearer token in Authorization header

### Claude's Discretion
- Heartbeat interval (30s suggested, can adjust)
- Exact structured logger implementation
- Run artifact directory structure details
- nightwatch-app.yaml default values beyond what spec defines

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Design Spec
- `docs/superpowers/specs/2026-03-18-nightwatch-dashboard-design.md` — Full architecture, data model, IPC protocol, safehouse policy, all types. **Note: Appendix C (Unix socket) is overridden by Bun native IPC decision above.**

### Research
- `.planning/research/STACK.md` — Bun APIs, Hono version, library versions
- `.planning/research/ARCHITECTURE.md` — Component boundaries, IPC patterns, data flow
- `.planning/research/PITFALLS.md` — 6 critical infrastructure pitfalls (all must land in this phase)

### Existing Plugin
- `config/safety.yaml` — max_runtime_minutes, max_concurrent_runs, other limits
- `CLAUDE.md` — Plugin conventions, commit prefixes, self-repair rules

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None — `app/` directory is new (greenfield within existing plugin)

### Established Patterns
- Plugin uses YAML for all config (`nightwatch-targets.yaml`, `safety.yaml`)
- `kc-plugins-config/` directory at user scope for runtime state
- Existing cron wrapper (`config/nightwatch-cron.sh`) shows current execution pattern

### Integration Points
- `app/nightwatch-app.yaml` — new app-scope config (created on first start)
- `~/.claude/kc-plugins-config/` — existing user-scope config files (read by server)
- `app/runs/` — new run artifacts directory (gitignored)
- `app/logs/` — new log directory (gitignored)

</code_context>

<specifics>
## Specific Ideas

- "Always-on in mprocs" — must be stable enough to run 24/7 without attention
- Worker offline should degrade gracefully, not crash the whole dashboard
- Bun native IPC chosen over node:net to eliminate socket file management entirely

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-foundation*
*Context gathered: 2026-03-18*
