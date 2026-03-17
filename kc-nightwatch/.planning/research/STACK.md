# Stack Research

**Domain:** Bun-native web dashboard — HTTP server + background worker + Preact frontend with real-time streaming, IPC, and MCP server
**Researched:** 2026-03-18
**Confidence:** HIGH (core stack verified via official docs and Context7; MCP SDK version verified via GitHub releases)

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Bun | 1.2.x (current: 1.2.20+) | Runtime, bundler, test runner | Constraint from PROJECT.md; TypeScript-native, ESM, no config needed. Native `Bun.spawn()` for child process streaming, `Bun.serve()` for HTTP+WebSocket, built-in YAML parse. Bun 1.2 adds 90% Node.js compat, removing most shim concerns. |
| Hono | 4.12.x (current: 4.12.2) | HTTP framework | Designed for Bun — uses Web Standards APIs (Request/Response/Headers) so no adapter needed. Provides `streamSSE()` for log streaming, `upgradeWebSocket` for chat, `serveStatic` for frontend assets. Lightweight (~14KB). The `hono/bun` import gives Bun-specific WebSocket handler. |
| Preact + HTM | Preact 10.23.1, HTM 3.1.1 | Frontend UI | Constraint from design spec. ~4KB total (Preact 3KB + HTM 1KB). No build step — Bun transpiles `.ts` files on-the-fly in dev; `Bun.build()` bundles to single file for production. HTM's tagged template syntax (`html\`...\``) is zero-dependency JSX. Component model + hooks for the chat panel and SSE log stream components. |
| `@modelcontextprotocol/sdk` | 1.27.1 (latest stable v1.x) | MCP server at `/mcp` | Official SDK. Provides `McpServer` class and `StreamableHTTPServerTransport` for the Streamable HTTP transport used in `routes/mcp.ts`. The `@hono/mcp` package (v0.2.4) adds a convenience Hono middleware to mount the MCP server without writing raw transport code. v2 SDK is in pre-alpha; use v1.27.x until stable v2 releases in Q1 2026. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `yaml` (npm) | 2.x | YAML read/write for config files | Use `yaml.stringify()` to serialize targets.yaml and app config — Bun's native `Bun.YAML.parse()` is parse-only, no stringify. The `yaml` library preserves comments and formatting better than `js-yaml`. Used in `services/yaml-store.ts`. |
| `zod` | 3.x | Schema validation at config boundaries | Validate targets.yaml, app config, and IPC messages at parse time. Prevents schema drift silently corrupting runs. Use in `yaml-store.ts` and `worker/ipc.ts`. Required by PROJECT.md "Zod at boundaries" rule. |
| `@hono/mcp` | 0.2.4 | Hono middleware for MCP Streamable HTTP | Mounts `McpServer` onto a Hono app route with correct headers + JSON body parsing. Saves ~30 lines of manual transport wiring. Use in `routes/mcp.ts`. |
| `@preact/signals` | 1.3.0 | Fine-grained reactivity for live state | SSE log stream + run status updates need efficient incremental rendering without full re-renders. Signals avoid the need for Redux/Zustand while staying in the Preact ecosystem. Load via import map in `index.html`. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `bun test` | Unit + integration testing | Built into Bun. Jest-compatible API. No separate vitest/jest dependency needed. Use for yaml-store, IPC message serialization, log-parser, and safehouse flag builder tests. |
| `Bun.build()` | Production frontend bundle | `Bun.build({ entrypoints: ['frontend/app.ts'], outdir: 'dist/' })` bundles Preact+HTM into a single JS file inlined into `index.html`. Only needed for production — dev mode serves `.ts` files directly. |
| TypeScript (via Bun) | Type checking | Bun runs TypeScript natively; no `tsc` needed at runtime. Run `bun tsc --noEmit` for type-only checks during development. Keep strict mode on. |
| `biome` | Lint + format | Already established in the workspace (e2e-pipeline uses it). Consistent with existing plugin conventions. |

## Installation

```bash
# Core app (from kc-nightwatch/app/)
bun add hono zod yaml @modelcontextprotocol/sdk @hono/mcp

# Frontend (loaded via import map in index.html — no npm install needed)
# preact@10.23.1 + htm@3.1.1 + @preact/signals@1.3.0 served from esm.sh CDN
# OR vendored into frontend/lib/ for offline use

# Dev dependencies
bun add -D @types/bun biome
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Bun native IPC (`Bun.spawn` + `ipc` handler) | Unix domain socket via `node:net` | Use `node:net` if the worker needs to be a non-Bun process. For this project, both server and worker are Bun, so native IPC is simpler — no socket file cleanup, no reconnect loop, structured clone serialization. |
| `node:net` Unix socket for server↔worker | Bun native IPC | Use if the design spec's "reconnect loop with 1s backoff" is required — Bun's built-in IPC doesn't expose a low-level reconnect API. The design spec specifies Unix socket explicitly (`nightwatch.sock`), so `node:net` is actually the correct choice here to honor the spec (see note below). |
| Hono `upgradeWebSocket` from `hono/bun` | Raw `Bun.serve()` WebSocket handlers | Use raw Bun WebSocket if you need pub/sub broadcasting to many clients. For this project (single chat session per browser), Hono's helper is sufficient and keeps routing uniform. |
| `yaml` npm package | `js-yaml` | js-yaml works fine but has fewer TypeScript types and doesn't preserve YAML comments. The `yaml` package is the modern successor with 85M+ weekly downloads. |
| `@modelcontextprotocol/sdk` v1.27.x | v2 pre-alpha | v2 is in pre-alpha as of 2026-03-18; stable v2 expected Q1 2026. Switch when stable. |
| Preact + HTM (no build) | Preact + Vite | Vite is the right choice if the frontend grows beyond ~10 components or if tree-shaking matters. For this dashboard (internal tool, Bun serves it), no build step is simpler to maintain. Switch if performance becomes an issue. |
| `@preact/signals` | `useState` + Context | Signals are more efficient for high-frequency updates (SSE log lines). `useState` is fine for static forms. Use signals for `log-stream.ts` and `run-timeline.ts`; useState is fine elsewhere. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Express or Fastify | Not Bun-native — wrap Node.js HTTP which is slower and heavier. Hono is designed for Web Standards runtimes. | Hono |
| React (full) | 45KB+ bundle for a single-user internal dashboard. No SSR needed. | Preact + HTM |
| `socket.io` | Requires Node.js adapter + extra binary protocol. Bun has WebSocket built into `Bun.serve()` and Hono wraps it cleanly. | Hono `upgradeWebSocket` from `hono/bun` |
| `node:child_process.spawn` | Works on Bun but misses Bun-specific features. `Bun.spawn()` returns a `ReadableStream` for stdout (cleaner async), has native timeout, and integrates with `AbortSignal`. | `Bun.spawn()` |
| MCP SDK v2 pre-alpha | "We anticipate a stable v2 release in Q1 2026" — not stable yet. v1.27.x is the recommended production version. | `@modelcontextprotocol/sdk@^1.27.1` |
| Bun native YAML (`Bun.YAML.parse`) for write | Parse-only — no stringify. Writing config files requires a library. | `yaml` npm package |

## Stack Patterns by Variant

**IPC transport: Bun native IPC vs. node:net Unix socket:**
- Bun native IPC (`{ ipc: handler }` in `Bun.spawn()`) is simplest for one-way parent→child. Messages are automatically serialized via structuredClone.
- However, the design spec explicitly calls for a Unix domain socket (`nightwatch.sock`) with server-is-listener / worker-is-client topology AND a reconnect loop. This topology (worker connects to server) is the reverse of what Bun's built-in IPC supports (parent spawns child).
- Use `node:net` (fully supported in Bun 1.2+): server calls `net.createServer()` on `nightwatch.sock`, worker connects via `net.createConnection()`. NDJSON framing (one JSON object per line) handles message delimiting.
- This matches the design spec exactly and avoids Bun IPC's "only compatible with bun processes" limitation if the socket is ever opened to non-Bun tooling.

**Frontend assets in production:**
- Dev: `Bun.serve({ static: { '/': './frontend/index.html' } })` — Bun transpiles TypeScript on request.
- Production: `Bun.build({ entrypoints: ['./frontend/app.ts'], outdir: './dist' })` + serve `dist/` as static files. No separate build server needed.

**SSE log streaming pattern:**
- Worker sends `{ type: 'run:log', run_id, event }` over Unix socket to server.
- Server holds a `Map<run_id, SSEStreamingApi>` of active SSE connections.
- On each IPC message, server looks up the run's SSE stream and calls `stream.writeSSE({ data: JSON.stringify(event), event: 'log' })`.
- Client disconnection detected via `c.req.raw.signal.addEventListener('abort', cleanup)`.

**Chat WebSocket bidirectional pattern:**
- `chat.ts` route uses `upgradeWebSocket` from `hono/bun`.
- On `onOpen`: spawn `claude --input-format stream-json --output-format stream-json` via `Bun.spawn()` with stdin set to `'pipe'`.
- Write user messages to `claude.stdin` as stream-json; read `claude.stdout` via `ReadableStream` and forward to WebSocket.
- On `onClose`: call `claude.kill('SIGTERM')`.
- If `--input-format stream-json` proves unreliable for long sessions, fall back to `@anthropic-ai/sdk` directly (design spec Appendix D notes this explicitly).

**MCP server mounting:**
- Use `@hono/mcp` to mount the `McpServer` instance onto `/mcp` in Hono.
- Alternatively, use `StreamableHTTPServerTransport` from `@modelcontextprotocol/sdk/server/streamableHttp.js` manually if `@hono/mcp` has dependency conflicts.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| `hono@4.12.x` | `bun@1.2.x` | Official Bun support. Import `upgradeWebSocket` from `hono/bun` specifically. |
| `@modelcontextprotocol/sdk@1.27.x` | `hono@4.x` | Use `@hono/mcp@0.2.4` for the Hono middleware. These are independent packages — SDK handles the protocol, @hono/mcp handles route mounting. |
| `preact@10.23.x` + `htm@3.1.1` | Bun frontend transpile | Bun handles `.ts` files with tagged template literals natively. No `.babelrc` or `jsxImportSource` config needed for HTM (HTM bypasses JSX transform entirely). |
| `yaml@2.x` | `zod@3.x` | No compatibility concern — independent packages. |
| `bun@1.2.x` `node:net` | Unix domain sockets | Verified: `Bun.serve({ unix: '/path/to/sock' })` and `node:net` both support Unix sockets in Bun 1.2+. Use `node:net` for the IPC transport (server + worker) to get full TCP-style socket API with reconnect support. |

## Sources

- [Hono official docs — Bun getting started](https://hono.dev/docs/getting-started/bun) — verified Bun-native support, `serveStatic`, current version 4.12.2
- [Hono SSE streaming helper docs](https://hono.dev/docs/helpers/streaming) — `streamSSE()` API, `writeSSE()` signature
- [Hono WebSocket helper docs](https://hono.dev/docs/helpers/websocket) — `upgradeWebSocket` from `hono/bun`, header mutation limitation
- [Bun WebSocket docs](https://bun.com/docs/runtime/http/websockets) — uWebSockets-based, 7x Node throughput, pub/sub, 120s idle timeout default
- [Bun IPC docs](https://bun.com/docs/guides/process/ipc) — confirmed "only compatible with bun processes"; Unix socket via node:net as alternative
- [Bun child process docs](https://bun.com/docs/runtime/child-process) — `Bun.spawn()` stdout as ReadableStream, `proc.kill('SIGTERM')`
- [Bun YAML docs](https://bun.com/docs/runtime/yaml) — parse-only (no stringify); Zig implementation
- [MCP TypeScript SDK GitHub releases](https://github.com/modelcontextprotocol/typescript-sdk/releases) — v1.27.1 is latest stable v1.x; v2 pre-alpha in progress
- [MCP SDK GitHub README](https://github.com/modelcontextprotocol/typescript-sdk) — `@modelcontextprotocol/hono` helpers, Streamable HTTP transport added 2025-03-26
- [@hono/mcp npm](https://www.npmjs.com/package/@hono/mcp) — v0.2.4, Hono middleware for MCP server mounting
- [Preact no-build workflows guide](https://preactjs.com/guide/v10/no-build-workflows/) — HTM + import maps; Preact 10.23.1, HTM 3.1.1 current
- [yaml npm package](https://www.npmjs.com/package/yaml) — 85M weekly downloads, parse + stringify, TypeScript types (MEDIUM confidence — npm page 403'd, version from ecosystem research)
- [Bun 1.2 release notes](https://socket.dev/blog/bun-1-2-released-90-node-js-compatibility-built-in-s3-object-support) — 90% Node.js compat, Bun 1.2 current minor is 1.2.20+

---
*Stack research for: Nightwatch Dashboard (Bun + Hono + Preact autonomous agent platform)*
*Researched: 2026-03-18*
