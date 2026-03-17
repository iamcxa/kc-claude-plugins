# Pitfalls Research

**Domain:** Bun server + worker IPC + CLI child process spawning + SSE/WebSocket streaming + Preact/HTM SPA + always-on local service
**Researched:** 2026-03-18
**Confidence:** HIGH (most claims verified via official GitHub issues or Hono/Bun docs)

---

## Critical Pitfalls

### Pitfall 1: Claude CLI hangs after emitting result event — processes accumulate silently

**What goes wrong:**
`claude -p --output-format stream-json` completes its task and emits `{"type":"result",...}` but the process never exits cleanly. The parent worker's `for await` loop never receives an end-of-stream signal, so the run stays `running` forever. If the interval scheduler fires again before the hung process is detected, a second run is attempted and queued. Over hours, zombie `claude` processes accumulate and consume memory.

**Why it happens:**
This is a confirmed Claude Code CLI bug (GitHub issues #25629 and #21099, reported February 2026). The trigger is active MCP server connections keeping the process alive after the result event is written. Claude does not call `process.exit()` cleanly when MCP servers are connected. The process keeps stdout open, so the consuming `AsyncIterable` waits forever for stream close.

**How to avoid:**
- After receiving a `{"type":"result"}` line from the stdout stream, do NOT wait for stream close. Immediately record result, then schedule a hard kill: `setTimeout(() => child.kill('SIGKILL'), 10_000)`.
- This is not optional — it is a required workaround for a known unfixed CLI bug.
- Track every child PID in a set. On worker shutdown, kill all tracked PIDs.

**Warning signs:**
- Run shows `status: running` for longer than `safety.yaml max_runtime_minutes`
- `ps aux | grep claude` shows N processes older than expected
- Worker's IPC message rate drops to zero but no `run:completed` arrives

**Phase to address:** Phase 1 (Worker core — executor.ts). Must be in the initial spawn implementation, not added later.

---

### Pitfall 2: Unix socket file survives crash — server refuses to start on restart

**What goes wrong:**
Server creates `nightwatch.sock` on startup. If the server crashes (OOM, SIGKILL from mprocs restart, uncaught exception), the socket file is left on disk. On the next start, `net.createServer().listen(socketPath)` throws `EADDRINUSE`, and the server fails to start entirely. Since mprocs restarts the server process on crash, this creates a permanent restart loop.

**Why it happens:**
Unix domain socket files are filesystem artifacts that are only cleaned up if the owning process calls `server.close()` explicitly or if the OS-level API unlinks them. A crash skips cleanup. Node.js's `net.createServer()` does NOT auto-unlink stale socket files on EADDRINUSE — the caller must handle this.

**How to avoid:**
On server startup, before calling `server.listen()`:
```typescript
try {
  await fs.unlink(socketPath)
} catch (e) {
  // ENOENT = file didn't exist, that's fine
  if ((e as NodeJS.ErrnoException).code !== 'ENOENT') throw e
}
```
Then register `process.on('SIGINT', cleanup)` and `process.on('SIGTERM', cleanup)` to unlink on graceful shutdown.

**Warning signs:**
- Server process exits with `EADDRINUSE` immediately after crash + restart
- mprocs shows rapid restart loop (restart count climbing every few seconds)
- Log shows no HTTP requests processed before exit

**Phase to address:** Phase 1 (Server entry point `server/index.ts`). Socket lifecycle must be established before any feature work starts.

---

### Pitfall 3: Worker disconnect not detected — server queues runs into the void

**What goes wrong:**
Server sends `{ type: 'enqueue', run }` to the worker via the Unix socket. Worker has crashed and the socket connection is broken, but the server's IPC write succeeds silently (the write buffer accepts the bytes). The run is recorded as `queued` in the UI. It never becomes `running`. No error is surfaced. If the interval scheduler fires every 2 hours, the queue grows indefinitely.

**Why it happens:**
TCP/Unix socket writes buffer data even after the remote end disconnects. The disconnect is only detected on the next read, or when the write exceeds the buffer limit and the kernel sends EPIPE. Since the server mostly writes to the worker (not reads), a dead worker can go unnoticed for the duration of the run timeout.

**How to avoid:**
- Implement a heartbeat: every 30 seconds, worker sends `{ type: 'heartbeat' }`, server tracks `lastHeartbeatAt`.
- If `lastHeartbeatAt` is older than 60 seconds, mark worker as offline. Reject new enqueue requests with a visible error. Mark any in-flight run as `failed`.
- Worker reconnect loop must re-request current state on reconnect: `{ type: 'status' }` so both sides re-sync.

**Warning signs:**
- Run stays `queued` past 2× expected queue wait time
- Dashboard shows worker status as unknown
- No `run:started` IPC message arrives after enqueue

**Phase to address:** Phase 1 (IPC transport `server/ipc.ts`). Add heartbeat in the same phase as the basic IPC implementation.

---

### Pitfall 4: Hono SSE disconnect not detected in Bun — log stream leaks memory

**What goes wrong:**
Browser closes the run detail page (or navigates away) while a run is streaming. The SSE connection is dropped from the client side. Hono's `streamSSE` does not reliably fire `stream.onAbort()` in the Bun runtime (this was a confirmed bug, fixed in Hono PR #3042, but version pinning may mean deploying an affected version). Even when fixed, if the server holds a reference to the stream object in a `Set<StreamWriter>` for fan-out, the reference is never removed. The set grows without bound across many page views.

**Why it happens:**
Two compounding issues: (1) `stream.onAbort()` was a Bun-specific bug (abort events not propagated), and (2) fan-out subscriber sets require explicit removal on disconnect. Neither is handled automatically. Also: AbortSignal-based cleanup holds references to large data structures if the listener captures the log buffer.

**How to avoid:**
- Use `c.req.raw.signal.addEventListener('abort', () => subscribers.delete(streamRef))` as the disconnect hook — prefer `raw.signal` over `stream.onAbort()` for Bun reliability.
- Keep the subscriber map keyed by `run_id` and clean up entries when the run completes and all subscribers are gone.
- Cap the log buffer per run at N lines in memory (e.g., 500 lines); reads beyond that come from the `.jsonl` file on disk.
- Verify with Hono version ≥ the PR #3042 merge (check changelog for "call stream.abort() explicitly when request is aborted").

**Warning signs:**
- Server heap grows steadily over days with no reduction
- `process.memoryUsage().heapUsed` climbs on each page view of the runs detail
- Bun memory debugger shows large numbers of dead `ReadableStreamDefaultController` instances

**Phase to address:** Phase 1 (SSE route `server/routes/stream.ts`). Build with abort cleanup from the start; retrofitting is error-prone.

---

### Pitfall 5: Orphaned `safehouse → claude -p` chain when worker process is killed

**What goes wrong:**
Worker spawns: `bun → safehouse → claude`. When the mprocs restart policy kills the worker process (SIGTERM), `safehouse` and `claude -p` are in a different process group and do not receive the signal. They continue running, potentially for the full `max_runtime_minutes`. With 2-hour intervals and 30-minute max runtimes, this means up to 30 minutes of an unaccounted run consuming resources, and the next run attempt finds concurrency limit already "used" (it's not — the old run is just orphaned).

**Why it happens:**
`Bun.spawn()` does not transfer signal delivery to grandchild processes. `safehouse` itself may set up its own process group (macOS `sandbox-exec` spawns a child). Neither `safehouse` nor `claude` receives SIGTERM when the worker's parent is killed.

**How to avoid:**
- Store `safehouse`'s PID in a file `app/runs/{id}/worker.pid` immediately after spawn.
- On server startup, scan `app/runs/*/worker.pid` for any PIDs from runs that were `running` at last shutdown. Send `SIGTERM` to each. Wait 5 seconds. Send `SIGKILL`.
- During graceful worker shutdown: `child.kill('SIGTERM')` → wait 3s → `child.kill('SIGKILL')`.
- Do NOT use `detached: true` when spawning `safehouse` — that would make orphaning intentional.

**Warning signs:**
- `ps aux | grep safehouse` shows processes with start times predating current server uptime
- Run history shows runs stuck at `status: running` across server restarts
- `app/runs/` directory has PID files with no corresponding live process

**Phase to address:** Phase 1 (executor.ts). PID tracking and orphan cleanup on startup is load-bearing infrastructure.

---

### Pitfall 6: `--input-format stream-json` for NW-Claude chat is unreliable for long-lived sessions

**What goes wrong:**
The design uses `claude --input-format stream-json --output-format stream-json` for the NW-Claude chat panel — a long-lived, bidirectional session. In practice, this mode has documented instability: stdin freezes where keystrokes stop being processed but the process stays alive (mentioned in search results), hangs after result event (Pitfall 1 above), and potential empty-output bugs with large inputs (>7000 characters). A chat session that silently stops responding appears broken to the user but leaves a zombie process running.

**Why it happens:**
The `--input-format stream-json` feature is relatively new and primarily designed for batch chaining, not interactive sessions. Long-lived sessions stress-test buffer management between stdin/stdout pipes. The design spec (Appendix D) explicitly notes the fallback: "If `--input-format stream-json` proves unreliable for long-lived sessions, fallback to the Anthropic API directly."

**How to avoid:**
- Implement the API fallback (`@anthropic-ai/sdk`) in the same phase as the CLI approach. Do not defer it.
- Add a health check: if no message has been written or received on the chat session within 2 minutes, emit a no-op ping or restart the session.
- Cap chat session lifetime at N messages or N minutes. Offer "Reset conversation" button.
- Use the fallback API path as the primary in MVP; switch to CLI path only when confirmed stable.

**Warning signs:**
- Browser sends a chat message but no response arrives within 30 seconds
- `process.list()` shows a `claude` process with zero stdout bytes written in last 60 seconds
- User reports chat "frozen" without any server error logged

**Phase to address:** Phase 2 (Chat implementation). Start with API fallback as default; CLI path is the optimization, not the baseline.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Write YAML files without file locking | Simpler code | Run completion + feedback submission race → corrupted `nightwatch-runs.yaml` (both processes append to the file at the same time) | Never — runs complete while user submits feedback in parallel |
| Use `JSON.stringify` to serialize run logs in memory instead of streaming to disk | Simpler in-memory fan-out | Holding 30-minute run logs in RAM crashes on memory-constrained systems | Never for production; only in unit tests with mock data |
| Reuse the same `claude` process for all NW-Claude chat contexts (no per-target isolation) | Single process, simpler lifecycle | Cross-target context leakage: NW-Claude mixes e2e-pipeline and carlove memories | Never — isolation is a named design requirement |
| Skip MCP transport version negotiation and hardcode SSE | Faster first implementation | MCP clients using Streamable HTTP (current spec since March 2025) cannot connect | MVP acceptable if only claude sessions with matching client version are used; must fix before open-source release |
| Trust `nightwatch-runs.yaml` for all run state instead of writing a separate in-memory state | One source of truth | YAML read is slow for frequent status polling during active runs; SSE push becomes a YAML parse bottleneck | Accept for MVP; add in-memory run state cache in Phase 3 if polling becomes an issue |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| `agent-safehouse` | Passing tilde (`~`) in path arguments — safehouse does not expand shell tildes | Resolve all paths to absolute before building flags: `path.resolve(os.homedir(), 'relative/path')`. Design spec (Appendix E) already notes this, but it's easy to miss in implementation |
| `agent-safehouse` | Granting `--add-dirs` to a path that doesn't exist yet (e.g., `app/runs/{id}/` before the run starts) | Create the directory before spawning safehouse. Safehouse fails silently on nonexistent allowed dirs |
| `claude -p` MCP config | Passing `--mcp-config` with a path to a file that doesn't exist | Create default MCP config files (nw-journal, nw-mcp) during app bootstrap, not on first run |
| Hono + MCP server | Following TypeScript SDK docs written for Express — headers added after response is sent cause silent failures | Use `@hono/mcp` package (JSR: `@hono/mcp`) with `StreamableHTTPTransport`. Support both Streamable HTTP and legacy SSE transport for client compatibility |
| `nightwatch-feedback.yaml` concurrent writes | Multiple feedback submissions (dashboard + MCP in parallel) both append to the same YAML file | Serialize YAML writes through a queue or file lock. Use a simple in-memory async mutex per file path |
| Preact/HTM in browser without import maps | Bare specifier `import { html } from 'htm/preact'` fails in the browser — no module resolution | Configure `<script type="importmap">` in `index.html` or use CDN-hosted ESM URLs. Bun's server can serve from `node_modules/.bun/...` in dev mode |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| SSE fan-out via polling: reading `log.jsonl` on each SSE tick | CPU spike during active runs as many browser tabs each poll the same file | Keep the authoritative live log in memory (a `Map<runId, string[]>`) during run execution. SSE writes from memory, not disk. Persist to disk asynchronously | With 3+ browser tabs watching the same run |
| YAML parse on every `/api/targets` request | 50–200ms latency on each dashboard load | Cache the parsed YAML in memory; invalidate only on write. `yaml-store.ts` should have an in-memory cache with TTL or write-invalidation | Noticeable immediately; dashboard polling at 30s makes it 3× reads per minute |
| Bun child process stdout Buffer accumulation | Memory climbs linearly with run output volume | Do NOT buffer stdout in a `Buffer[]` array awaiting process exit. Parse line-by-line with `readline` or `Bun.lineIterator` and discard raw bytes after parsing | On long (30-min) runs generating verbose stream-json output |
| Socket reconnect storm | Worker and server restart simultaneously (mprocs restart both), both try to connect before the server socket is ready | Worker reconnect uses exponential backoff: 1s, 2s, 4s, 8s, max 30s. No tight retry loops | On any simultaneous restart scenario |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Binding to `0.0.0.0` without `auth_token` | Any process on the machine (or network if port is exposed) can trigger runs, submit feedback, or read private run logs | Enforce in server startup: if `host == '0.0.0.0'` and `auth_token` is absent, refuse to start with a clear error message |
| Passing `custom_prompt` from webhook body directly to `--append-system-prompt` without sanitization | Prompt injection via webhook: attacker controls the custom prompt sent to the claude process | Whitelist webhook callers by token. Truncate custom_prompt at 2000 characters. Log full custom_prompt to run artifact for audit |
| Writing `runs/{id}/log.jsonl` with world-readable permissions | Run logs may contain API keys, file contents, or private journal text seen by claude during execution | Create `app/runs/` with mode `0700`. Each run directory inherits. Verify with `fs.mkdir(path, { mode: 0o700 })` |
| MCP endpoint exposed without auth in "remote mode" | Any caller can invoke `nw_trigger_run` or `nw_implement_proposal`, causing unexpected code changes in target repositories | Auth check must be middleware-level in Hono, not per-route. A missing route-level check is a single point of failure. Use Hono middleware that applies to all `/mcp` and `/api` routes |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Showing raw stream-json lines in the log view | User sees `{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"..."}]}}` — unreadable | `log-parser.ts` must extract human-readable text from stream-json. Only display parsed phase markers, tool calls, and text content. Raw JSONL is for disk storage only |
| Auto-starting NW-Claude brief immediately after run completes, even if chat panel is not visible | Background claude process spawns unnecessarily; costs tokens; user sees stale "new brief" notification on next open | Defer NW-Claude brief spawn until user opens the chat panel (lazy init). Store run ID for briefing; load brief on panel open |
| Config editor loses unsaved changes on navigation | User writes 10 minutes of YAML edits, clicks Dashboard tab, changes are gone | Either warn on navigation ("You have unsaved changes"), or persist draft to `localStorage` on each keystroke |
| 4-step validation modal is blocking during 30-second semantic validation step | User clicks "Review Changes", sees spinner for 30 seconds with no progress — assumes it's broken | Show per-target validation progress inline: "Validating e2e-pipeline... ✓", "Validating carlove... ⟳" |

---

## "Looks Done But Isn't" Checklist

- [ ] **Claude process cleanup**: Spawning `claude -p` and reading its output appears to work in happy-path testing, but zombie processes only manifest after hours of real use. Verify by inspecting `ps aux` after 10 test runs with deliberate SIGKILL of the worker mid-run.
- [ ] **Socket file cleanup**: IPC "works" in dev where the server is gracefully stopped. Test crash recovery: `kill -9` the server process, then restart. If the server fails to start, the stale socket cleanup is missing.
- [ ] **SSE disconnect cleanup**: Fan-out "works" when one tab is open. Open 5 tabs to the same run, then close 4. If `subscribers` set still has 4 entries after a minute, the cleanup is broken.
- [ ] **Feedback YAML writes**: Dashboard 👍 and MCP `nw_submit_feedback` firing at the same millisecond should not corrupt `nightwatch-feedback.yaml`. Test with concurrent `Promise.all([submit1, submit2])` in an integration test.
- [ ] **Safehouse absolute paths**: Flags built with `~/.claude/...` instead of `os.homedir() + '/.claude/...'` will cause safehouse to fail silently. Add a startup assertion that all safehouse paths are absolute.
- [ ] **MCP transport compatibility**: The MCP endpoint "works" when tested with curl but may not work with `claude --mcp-config` pointing to it. Test with an actual Claude session using the MCP config before calling the MCP feature complete.
- [ ] **Result event timeout**: The worker correctly calls `run:completed` after receiving the stream-json result event — but only if the forced-kill timeout fires. Test by spawning a real `claude -p` run, receiving the result, and verifying the worker sends `run:completed` within 15 seconds even without the process exiting on its own.

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Zombie claude processes accumulated from pitfall 1 | LOW | Add a `POST /api/admin/cleanup-zombies` endpoint during development. On call: scan all `running` runs older than max_runtime_minutes, kill their PIDs, mark as `timeout` |
| Stale socket file (pitfall 2) | LOW | `rm /path/to/nightwatch.sock`, then `mprocs restart nightwatch-server`. Implement auto-cleanup in startup code to prevent recurrence |
| Corrupted YAML file from concurrent writes | MEDIUM | Keep a rolling backup: before any YAML write, copy current file to `{filename}.bak`. Recovery: `cp nightwatch-runs.yaml.bak nightwatch-runs.yaml` |
| Chat session frozen (pitfall 6) | LOW | Add "Reset conversation" button that kills the claude process and starts a fresh session. Auto-detect via health check and show "Session timed out — click to reconnect" |
| MCP transport mismatch | MEDIUM | Implement both Streamable HTTP and legacy HTTP+SSE transport in the MCP server. Client compatibility negotiation makes this a one-time fix |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Claude CLI hangs after result event | Phase 1 (executor.ts) | Integration test: spawn real `claude -p`, receive result event, assert process is dead within 15s |
| Stale socket file on restart | Phase 1 (server/index.ts) | Test: `kill -9` server, `ls nightwatch.sock` (file exists), restart server — must start successfully |
| Worker disconnect not detected | Phase 1 (ipc.ts) | Test: kill worker with `SIGKILL`, assert server marks it offline within 90 seconds |
| SSE leak on client disconnect | Phase 1 (routes/stream.ts) | Test: open 5 SSE connections, close all 5, assert subscribers set is empty |
| Orphaned safehouse chain | Phase 1 (executor.ts) | Test: kill worker mid-run with `SIGKILL`, restart server, assert `ps aux` shows no orphan claude processes |
| NW-Claude chat unreliability | Phase 2 (chat-session.ts) | Build with API fallback as default; validate CLI path separately before switching to it |
| Concurrent YAML corruption | Phase 1 (yaml-store.ts) | Integration test: 10 concurrent POSTs to `/api/feedback`, verify YAML is valid and has 10 entries |
| Safehouse path with tildes | Phase 1 (policy.ts) | Unit test: `buildSafehouseFlags()` output contains no `~` characters |
| Preact/HTM import map | Phase 1 (frontend/index.html) | Manual test: load page in browser with no build server, check browser console for import errors |
| MCP transport version | Phase 3 (routes/mcp.ts) | Test with actual `claude --mcp-config` session pointing to the endpoint |

---

## Sources

- [Claude Code CLI hangs after result event — GitHub #25629](https://github.com/anthropics/claude-code/issues/25629) — HIGH confidence (closed as duplicate of #21099, confirmed behavior)
- [Claude Code input stream-json hang — GitHub #3187](https://github.com/anthropics/claude-code/issues/3187) — HIGH confidence (closed as completed)
- [Claude Code empty output with large stdin — GitHub #7263](https://github.com/anthropics/claude-code/issues/7263) — HIGH confidence (closed as not planned, known limitation)
- [Hono abort not working in Bun — GitHub #3032](https://github.com/honojs/hono/issues/3032) — HIGH confidence (fixed in PR #3042, merged)
- [Hono event listener on client disconnect — GitHub #1770](https://github.com/honojs/hono/issues/1770) — HIGH confidence (open issue, acknowledged by maintainers)
- [Hono SSE memory leak at 30 concurrent connections — GitHub #3940](https://github.com/honojs/hono/issues/3940) — MEDIUM confidence (open issue, reproduction not confirmed)
- [MCP SSE transport deprecated, Streamable HTTP is current spec — MCP spec March 2025](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports) — HIGH confidence (official spec)
- [MCP transport change — fka.dev analysis](https://blog.fka.dev/blog/2025-06-06-why-mcp-deprecated-sse-and-went-with-streamable-http/) — MEDIUM confidence (community analysis, consistent with official spec)
- [Unix socket EADDRINUSE stale file pattern — Node.js docs + community patterns](https://nodejs.org/api/net.html) — HIGH confidence (documented behavior)
- [Bun child process stdout is Buffer not ReadableStream — Bun docs](https://bun.com/reference/bun/spawn) — HIGH confidence (official reference)
- [agent-safehouse deny-first policy, path resolution — agent-safehouse.dev](https://agent-safehouse.dev/docs/overview) — HIGH confidence (official docs)
- [Claude Code stdin freeze in long-running sessions — GitHub changelog reference](https://code.claude.com/docs/en/changelog) — MEDIUM confidence (mentioned in community search, not linked to specific fix version)

---
*Pitfalls research for: Nightwatch Dashboard (Bun + Hono + Worker IPC + SSE/WebSocket + Preact/HTM + always-on mprocs service)*
*Researched: 2026-03-18*
