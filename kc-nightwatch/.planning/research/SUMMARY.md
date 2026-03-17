# Project Research Summary

**Project:** Nightwatch Dashboard
**Domain:** Autonomous agent monitoring + improvement cockpit (Bun server + worker + Preact frontend)
**Researched:** 2026-03-18
**Confidence:** HIGH

## Executive Summary

The Nightwatch Dashboard is a single-user, localhost-first autonomous improvement platform that replaces a launchd cron job with a persistent Bun HTTP server + background worker. The closest analogues are CI/CD dashboards (GitHub Actions, CircleCI) for the operational shell and AI agent observability tools (LangSmith, Langfuse) for the trace/feedback model — but Nightwatch is unusual because it combines both *monitoring* (observe what happened) and *directing* (accept/reject proposals, trigger runs, inject per-run instructions) in one tool. The recommended implementation uses a two-process architecture with Hono HTTP server and a Bun worker communicating via Unix domain socket, Preact+HTM for a no-build-step frontend, and a staged feature rollout that defers flywheel health metrics until core feedback infrastructure is proven.

The recommended stack is entirely Bun-native: Hono 4.12.x for HTTP/SSE/WebSocket, `@modelcontextprotocol/sdk@1.27.x` + `@hono/mcp` for the MCP endpoint, Preact+HTM served via Bun's on-the-fly TypeScript transpilation, and `yaml`+`zod` at all YAML config boundaries. The architecture research confirms the design spec's two-process split is correct: the HTTP server must stay responsive while a 30-minute Claude run executes in the worker. All worker communication must flow through a single IPC module (never direct imports across the process boundary). SSE fans out log events from IPC to browsers; WebSocket proxies the NW-Claude chat session.

The most significant risks are not architectural but operational. Six critical pitfalls are all load-bearing infrastructure that must be built in Phase 1: claude CLI zombie processes (known bug — forced kill required after result event), Unix socket file left on crash (EADDRINUSE restart loop), worker disconnect not detected (silent queue growth), SSE subscriber leak on browser disconnect, orphaned safehouse→claude chains after worker SIGKILL, and concurrent YAML writes corrupting state files. None of these manifests in happy-path dev testing — all require deliberate failure injection to verify. The mitigation for each is straightforward, but all must be in place before any feature work starts.

## Key Findings

### Recommended Stack

The stack is fully settled by constraints (Bun runtime, Hono+Preact+HTM from design spec) and confirmed by research against official documentation. The only non-obvious decision is IPC transport: despite the design spec calling for Unix domain socket with NDJSON, Bun's native IPC (`Bun.spawn` with `ipc` option) is actually the simpler path since both processes are Bun. However, the design spec's explicit requirement for a worker-connects-to-server topology (worker is client, server is listener) is the reverse of what Bun's built-in IPC supports (parent spawns child). Use `node:net` Unix socket with NDJSON framing to honor the spec exactly.

**Core technologies:**
- **Bun 1.2.x**: Runtime, bundler, test runner — project constraint; native TS, ESM, `Bun.spawn()` for child processes
- **Hono 4.12.x**: HTTP framework — Bun-native (Web Standards APIs), provides `streamSSE()`, `upgradeWebSocket`, `serveStatic`
- **Preact 10.23.x + HTM 3.1.1**: Frontend — project constraint; ~4KB total, no build step, Bun transpiles `.ts` on-the-fly
- **`@modelcontextprotocol/sdk@1.27.x`**: MCP server — v1.27.x is latest stable; v2 pre-alpha, use v1 until stable
- **`@hono/mcp@0.2.4`**: MCP Hono middleware — mounts McpServer onto `/mcp` route, saves ~30 lines of manual transport wiring
- **`yaml@2.x`**: YAML read/write — Bun's built-in `Bun.YAML.parse()` is parse-only (no stringify); `yaml` package handles both
- **`zod@3.x`**: Schema validation — required by project conventions; use at all YAML config + IPC message boundaries
- **`@preact/signals@1.3.x`**: Fine-grained reactivity — efficient for high-frequency SSE log stream updates

See `.planning/research/STACK.md` for version compatibility matrix and full rationale.

### Expected Features

Features are well-defined by the design spec (812 lines, 2 review rounds). The research confirms a three-tier MVP structure:

**Must have (P1 — table stakes):**
- Target list with last run status + schedule bar — replaces manual nightwatch-runs.yaml inspection
- Manual run trigger with mode selection (production/dry-run) + custom prompt
- Real-time log streaming during execution (SSE from worker) — single biggest UX improvement over cron
- Run history list + detail with phase progress + action summary
- Interval scheduler (enable/disable, set hours) — replaces launchd plist management
- Feedback buttons per action (thumbs up/down) + POST /api/feedback
- Per-target NW memory isolation — foundational; painful to retrofit later
- Sandboxed execution with per-target agent-safehouse policy — non-negotiable safety requirement

**Should have (P2 — differentiators, add after core cockpit is validated):**
- Indicator baseline measurement (Phase 0.5) — quantified, not qualitative
- Per-run self-assessment display (Phase 3.5 + 4.5) — surfaces agent's strategic reasoning
- Config editor with 4-step validation (static → Haiku semantic → diff → confirm)
- Add Target wizard
- NW-Claude chat panel with auto-brief after runs
- Webhook trigger

**Defer (P3 — full flywheel, needs feedback data first):**
- Implementation outcome tracking (Phase 0.6)
- Flywheel health display (sparklines, reject rate trends)
- Proposal → Implementation pipeline
- MCP server (requires stable run store API surface)

**Anti-features to avoid:** Multi-user RBAC, cron expression scheduling (intervals are clearer), auto-start NW-Claude brief (lazy init only), proposal execution without explicit user approval.

See `.planning/research/FEATURES.md` for dependency graph and competitor analysis.

### Architecture Approach

The two-process architecture is the correct choice and is confirmed by the design spec. The Hono HTTP server must remain alive and responsive during a 30-minute Claude run executing in the worker. These two concerns must never share a process. The critical path for build order is: `shared/types.ts` → `yaml-store` → worker (executor + scheduler) → `server/ipc.ts` → REST routes → SSE → frontend. The MCP endpoint is Phase 5 in build order — it depends on a stable run store but is independent of the chat and SSE features.

**Major components:**
1. **Hono HTTP server** (`server/`) — HTTP routing, SSE emission, WebSocket upgrade, MCP endpoint, static file serving
2. **Worker process** (`worker/`) — scheduler, execution queue, safehouse spawning, run lifecycle via Bun.spawn
3. **Unix domain socket IPC** — bidirectional NDJSON; server is listener, worker is client; heartbeat-based liveness
4. **log-parser** (`worker/log-parser.ts`) — parses `--output-format stream-json` into typed events before IPC crossing
5. **SSE fan-out** (`server/routes/stream.ts`) — `Map<runId, Set<SSEWriter>>` fanned from IPC `run:log` events
6. **chat-session** (`server/services/chat-session.ts`) — manages long-lived `claude --input-format stream-json` process per WebSocket
7. **yaml-store** (`server/services/yaml-store.ts`) — read/write YAML config with field rename compat layer; in-memory cache

See `.planning/research/ARCHITECTURE.md` for data flow diagrams and anti-patterns.

### Critical Pitfalls

All 6 critical pitfalls must be addressed in Phase 1. None manifests in happy-path testing.

1. **Claude CLI hangs after result event** — Confirmed bug (GitHub #25629, #21099): active MCP connections keep the process alive after `{"type":"result"}`. Prevention: on result event, schedule hard kill `setTimeout(() => child.kill('SIGKILL'), 10_000)`. Do not wait for stream close. Track all PIDs.

2. **Stale Unix socket file after crash** — `net.createServer().listen()` throws `EADDRINUSE` and creates a restart loop. Prevention: on server startup, `await fs.unlink(socketPath)` (ignore ENOENT), then register SIGINT/SIGTERM cleanup handlers.

3. **Worker disconnect not detected** — Socket writes buffer silently to a dead worker; runs queue into the void. Prevention: 30-second heartbeat from worker; server marks worker offline if heartbeat is >60s stale; reject enqueue with visible error.

4. **SSE subscriber leak on browser disconnect** — `stream.onAbort()` was a Bun bug (fixed in Hono PR #3042); `fan-out Set` requires explicit removal. Prevention: use `c.req.raw.signal.addEventListener('abort', cleanup)` for disconnect detection; cap in-memory log buffer at 500 lines per run.

5. **Orphaned safehouse→claude chain after worker SIGKILL** — Grandchild processes do not receive SIGTERM when worker is killed. Prevention: write `app/runs/{id}/worker.pid` immediately after spawn; on server startup, scan for stale PID files and SIGKILL orphans.

6. **NW-Claude chat session unreliability** — `--input-format stream-json` is designed for batch chaining, not long-lived interactive sessions; documented instability for sessions >7000 chars or after long idle. Prevention: implement `@anthropic-ai/sdk` API fallback in the same phase; use API path as MVP default; switch to CLI path only after confirmed stable.

See `.planning/research/PITFALLS.md` for verification checklists and recovery strategies.

## Implications for Roadmap

Based on research, all 6 critical pitfalls plus the IPC foundation must land in Phase 1. This is not negotiable — the pitfalls are invisible in happy-path dev but emerge in production within hours. The feature phases build on top.

### Phase 1: Foundation + Reliability Infrastructure

**Rationale:** All critical pitfalls are infrastructure-level and must be addressed before any feature work. The IPC boundary, socket lifecycle, and process cleanup are the foundation every subsequent feature depends on. Building features before these are solid creates compounding debt.

**Delivers:** Runnable two-process app: server starts and stays up across crashes, worker connects and stays in sync with server, basic HTTP routes serving placeholder responses, IPC message protocol fully typed and tested.

**Addresses:** P1 features (table stakes prerequisites) — IPC foundation, scheduler skeleton, run lifecycle state machine

**Avoids:** Pitfalls 1–5 from PITFALLS.md (all Phase 1 designation). Specific items: claude zombie process handling, socket file cleanup, heartbeat, SSE subscriber cleanup, orphan PID cleanup.

**Key deliverables:**
- `shared/types.ts` — all IPC message types + domain types
- `server/ipc.ts` — Unix socket client with heartbeat, reconnect, worker liveness detection
- `worker/index.ts` — socket server + message dispatch
- `worker/executor.ts` — Bun.spawn safehouse chain with forced-kill on result event, PID tracking
- `worker/policy.ts` — safehouse flag builder (no tilde paths)
- `worker/log-parser.ts` — stream-json line parser
- `server/services/yaml-store.ts` — YAML read/write with in-memory cache + file lock (async mutex)
- `server/index.ts` — socket cleanup on startup + SIGINT/SIGTERM handlers

### Phase 2: Core Cockpit (P1 Features)

**Rationale:** With the foundation solid, deliver the full P1 feature set that makes the dashboard better than the current cron+YAML-file workflow. These features are table stakes — users expect them from any CI/CD or monitoring tool.

**Delivers:** Working dashboard UI: target cards with run status, manual trigger with mode selection, real-time SSE log streaming during execution, run history and detail pages, interval scheduler, per-target NW memory isolation, and sandboxed execution enforcement.

**Addresses:** All P1 features from FEATURES.md MVP list

**Implements:** ARCHITECTURE.md Phase 3–6 build order (server REST routes → SSE → frontend pages)

**Key deliverables:**
- REST API routes (`/api/targets`, `/api/runs`, `/api/feedback`, `/api/webhook`)
- SSE streaming route (`/api/runs/:id/stream`) with fan-out and disconnect cleanup
- `worker/scheduler.ts` — interval timer
- Frontend: dashboard page, run history/detail page, log-stream component with stream-json parsing
- Trigger dialog, feedback buttons, schedule status bar
- Per-target NW journal isolation in executor (target-specific `--mcp-config`)

### Phase 3: Flywheel Core (P2 Features)

**Rationale:** Once the core cockpit is working and feedback data starts accumulating (even just a few runs), add the features that differentiate Nightwatch from generic CI/CD tools. NW-Claude chat requires run history to be meaningful; config editor requires YAML store to be stable. These features are additive — they don't change the existing data flow.

**Delivers:** NW-Claude chat panel, config editor with 4-step validation, Add Target wizard, indicator baseline measurement, self-assessment display in run detail.

**Addresses:** P2 features from FEATURES.md

**Uses:** STACK.md WebSocket pattern (chat), Hono `upgradeWebSocket` from `hono/bun`, `@anthropic-ai/sdk` API fallback for chat stability (PITFALL #6)

**Key deliverables:**
- `server/services/chat-session.ts` — API fallback as default; CLI path as optimization
- `server/routes/chat.ts` — WebSocket upgrade
- Frontend: chat-panel component, YAML editor with 4-step validation flow
- Config save flow (4-step: syntax → Haiku semantic → diff → confirm)
- Phase 0.5 baseline measurement in worker pipeline
- Self-assessment display (reads existing run data — display-only)

### Phase 4: Full Flywheel (P3 Features)

**Rationale:** Defer until flywheel core is validated and sufficient feedback + indicator data exists (several proposal→feedback cycles). Flywheel health display is meaningless without implementation outcome data. Proposal → implementation pipeline is high complexity and high risk — validate proposal quality first.

**Delivers:** MCP server, flywheel health metrics display, implementation outcome tracking (Phase 0.6), proposal → implementation pipeline.

**Addresses:** P3 features from FEATURES.md

**Avoids:** PITFALL #3 (MCP transport version mismatch) — test with actual `claude --mcp-config` session before marking complete; implement both Streamable HTTP and legacy SSE transport for compatibility

**Key deliverables:**
- `server/routes/mcp.ts` — MCP Streamable HTTP endpoint with 10 tools
- Phase 0.6 outcome tracking in worker pipeline
- Flywheel health sparklines and reject rate charts
- Proposal → implementation pipeline (accept action → spawn implementation run)

### Phase Ordering Rationale

- Phase 1 before everything: pitfalls are invisible in dev but fatal in production. Socket lifecycle + process cleanup is not a feature, it's a precondition for all features.
- Phase 2 before Phase 3: NW-Claude chat requires run history to exist (needs several runs). Config editor requires yaml-store to be stable. Both are P2 by design.
- Phase 3 before Phase 4: Flywheel health metrics require implementation outcome data. MCP server requires stable run store API. Both have data dependencies that only Phase 3 can produce.
- Feedback buttons land in Phase 2 (not Phase 3): They are table stakes for the flywheel — shipping without them means the first run creates no learning data. The flywheel must be seeded from day one.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 3 (Chat panel):** `--input-format stream-json` reliability for long sessions is an open question. Research confirms known bugs but no definitive fix version. Plan must include API fallback as default with explicit cutover criteria.
- **Phase 4 (MCP server):** `@hono/mcp` is new (appeared March 2025). Transport compatibility between Streamable HTTP and legacy SSE clients needs hands-on testing, not just doc review. Flag for a research spike before implementation.
- **Phase 4 (Flywheel metrics):** Implementation outcome tracking (Phase 0.6) — "did merged PRs actually help?" — requires cross-run data correlation that has not been designed in detail. Needs a design spike.

Phases with standard patterns (skip research):
- **Phase 1 (Foundation):** All patterns are well-documented. Unix socket cleanup, heartbeat, PID tracking — standard Node.js patterns with Bun-compatible `node:net`. Bun docs are authoritative.
- **Phase 2 (Core cockpit):** Hono REST + SSE patterns are fully verified against official docs. Preact+HTM no-build-step pattern is documented by Preact team.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Core stack verified via Context7 against Hono, Bun, MCP SDK docs. One caveat: `yaml@2.x` npm page 403'd during research — version from ecosystem inference, not direct npm verification |
| Features | HIGH | Design spec is authoritative (812 lines, 2 review rounds). Feature prioritization from external analogues is MEDIUM (community sources) |
| Architecture | HIGH | Design spec is authoritative. All patterns verified against Bun + Hono official docs. IPC topology (worker-connects-to-server) resolves correctly to `node:net` Unix socket |
| Pitfalls | HIGH | Critical pitfalls backed by specific GitHub issue numbers. Hono abort bug verified by PR number. Unix socket EADDRINUSE is documented Node.js behavior |

**Overall confidence:** HIGH

### Gaps to Address

- **`--input-format stream-json` stability threshold:** Research confirms it's unreliable but does not give a fixed version where it's resolved. The API fallback (`@anthropic-ai/sdk`) must be built in the same phase as the CLI path — treat the CLI path as an optimization, not the baseline.
- **MCP transport dual-support:** Implementing both Streamable HTTP and legacy HTTP+SSE in the MCP server is flagged as a "one-time fix" in PITFALLS.md but the exact `@hono/mcp` API for dual transport is not researched. Needs a short spike before Phase 4.
- **Flywheel outcome tracking data model:** How to correlate "PR merged" events (from GitHub webhook/polling) with indicator baseline changes is not designed. Phase 4 needs a design spike before implementation starts.
- **`yaml@2.x` version confirmation:** npm page returned 403 during research. Use `npm info yaml version` to confirm the current 2.x minor before pinning in package.json.

## Sources

### Primary (HIGH confidence)
- Design spec: `kc-nightwatch/docs/superpowers/specs/2026-03-18-nightwatch-dashboard-design.md` — authoritative 812-line spec, 2 review rounds
- PROJECT.md: `kc-nightwatch/.planning/PROJECT.md` — requirements, constraints, key decisions
- [Hono official docs — Bun getting started](https://hono.dev/docs/getting-started/bun) — verified v4.12.2, `serveStatic`, Bun-native support
- [Hono Streaming Helper docs](https://hono.dev/docs/helpers/streaming) — `streamSSE()`, `writeSSE()` signature
- [Bun IPC documentation](https://bun.com/docs/guides/process/ipc) — spawn + `.send()` / `process.on("message")`
- [Bun WebSocket docs](https://bun.com/docs/runtime/http/websockets) — native upgrade API, pub/sub
- [Bun child process docs](https://bun.com/docs/runtime/child-process) — `Bun.spawn()` stdout as ReadableStream
- [MCP TypeScript SDK GitHub releases](https://github.com/modelcontextprotocol/typescript-sdk/releases) — v1.27.1 latest stable v1.x
- [Claude Code CLI hangs after result event — GitHub #25629](https://github.com/anthropics/claude-code/issues/25629) — confirmed bug
- [Hono abort not working in Bun — GitHub PR #3042](https://github.com/honojs/hono/issues/3032) — fixed
- [Unix socket EADDRINUSE stale file — Node.js docs](https://nodejs.org/api/net.html) — documented behavior
- [MCP Transports specification 2025-03-26](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports) — Streamable HTTP current spec

### Secondary (MEDIUM confidence)
- [Preact no-build workflows guide](https://preactjs.com/guide/v10/no-build-workflows/) — HTM + import maps
- [LangSmith observability](https://www.langchain.com/langsmith/observability) — competitor feature analysis
- [Langfuse evaluation](https://langfuse.com/docs/evaluation/core-concepts) — competitor feature analysis
- [Bun 1.2 release notes](https://socket.dev/blog/bun-1-2-released-90-node-js-compatibility-built-in-s3-object-support) — 90% Node.js compat, current minor 1.2.20+
- [SSE vs WebSocket 2026 comparison](https://oneuptime.com/blog/post/2026-01-27-sse-vs-websockets/view) — confirmed design spec transport decisions
- [@hono/mcp npm package](https://www.npmjs.com/package/@hono/mcp) — v0.2.4
- [agent-safehouse official docs](https://agent-safehouse.dev/docs/overview) — path resolution, deny-first policy
- Hono SSE memory leak at 30 connections — [GitHub #3940](https://github.com/honojs/hono/issues/3940) — open issue, MEDIUM confidence

### Tertiary (LOW confidence)
- GitHub Agentic Workflows overview (The New Stack) — competitor positioning only
- Claude Code stdin freeze in long-running sessions — mentioned in community search, not linked to specific fix version

---
*Research completed: 2026-03-18*
*Ready for roadmap: yes*
