# Stack Research

**Domain:** Bun-native web dashboard — HTTP server + background worker + Preact frontend with real-time streaming, IPC, and MCP server
**Researched:** 2026-03-18 (v1.0 baseline) / 2026-03-20 (v1.1 addendum)
**Confidence:** HIGH (core stack verified via official docs and Context7; v1.1 additions verified via MDN + ecosystem research)

---

## v1.1 Stack Additions (NEW — 2026-03-20)

> The v1.0 baseline stack (Bun, Hono, Preact/HTM, Zod, yaml, MCP SDK) is complete and validated. This section covers ONLY what v1.1 adds.

### What v1.1 Needs

| Feature | What's needed | Source of truth |
|---------|---------------|-----------------|
| Toast notifications | Zero-dependency custom hook + component (pure Preact/HTM) | No library — handroll it |
| Browser Notification API | Built-in Web API — zero deps | MDN, globally available in secure context |
| Auto-refresh (Runs page) | `useInterval` custom hook — already the pattern in `dashboard.ts` | Copy the dashboard polling pattern |
| `queued_at` timestamp | Schema addition to `Run` type + `run-store.ts` write | No new library needed |
| Queue display in TargetDetail | Read `/api/runs?status=queued&target=X` — existing API | No new route needed |

**Summary: No new npm packages.** All five v1.1 features are implementable with existing stack.

---

### Toast Notification System

**Decision: Custom hook — no library.**

Rationale: The existing codebase is a no-build Preact/HTM app with vendored ESM. Adding a toast library (react-toastify, sonner, hot-toast) would require either a bundler step or an esm.sh CDN import. The toast requirement is simple (trigger feedback + auto-dismiss after 3s), and the dashboard's inline-style convention means a ~50-line custom component fits naturally.

**Pattern to implement:**

```typescript
// frontend/hooks/use-toast.ts
// useToast() → { toasts, addToast, removeToast }
// Toast type: { id: string, message: string, variant: 'success' | 'error' | 'info', at: number }
// Auto-dismiss: setTimeout in addToast, clearTimeout on removeToast
// Position: fixed bottom-right, z-index 200 (above dialog at z-index 100)
```

**Integration point:** App-level singleton hook in `app.ts`, passed down as a context value (or via `@preact/signals` signal) to avoid prop-drilling. The `TriggerDialog` → `handleTrigger` path in `dashboard.ts` fires the toast after `api.triggerRun()` resolves.

**Confidence:** HIGH — standard React/Preact pattern, no library coupling risk.

---

### Browser Notification API

**Decision: Raw Web API — no library, no Service Worker.**

The dashboard runs on localhost (single user, desktop-only per PROJECT.md). Service Worker notifications are needed for mobile/push scenarios. Direct `new Notification()` is the correct choice here.

**Key constraints (from MDN, HIGH confidence):**

1. **Secure context only** — Chrome and Firefox require HTTPS. Exception: `localhost` is a secure context by spec. This dashboard defaults to `127.0.0.1:3201` — no HTTPS needed for Notification API.
2. **User gesture required for `requestPermission()`** — must be called inside a click handler, not on page load. Firefox enforces this from v72+.
3. **Mobile throws TypeError** — `new Notification()` is desktop-only. Not a concern for this dashboard.

**Permission flow:**

```typescript
// frontend/lib/notifications.ts
// Check Notification.permission before requesting
// 'granted' → fire directly
// 'default' → ask once, on a user click (e.g., first run trigger)
// 'denied' → silently skip (never re-request)
```

**Integration point:** The existing global SSE in `app.ts` already listens to `brief-ready` (fires when `run:completed` IPC arrives). The same `es.addEventListener('brief-ready', ...)` handler fires the browser notification. The `run:failed` IPC case currently only calls `closeRunSubscribers()` — add a `broadcastGlobal('run-failed', ...)` call in `ipc.ts` to enable failure notifications too.

**One server change required:** Add `run-failed` global SSE event broadcast alongside the existing `brief-ready`. Currently `run:failed` only closes SSE subscribers — it does not broadcast to global listeners. This is a one-line change in `ipc.ts`.

**Confidence:** HIGH — verified via MDN official docs.

---

### Auto-Refresh (Runs Page)

**Decision: Copy the polling pattern from `dashboard.ts` exactly.**

The `Dashboard` component already has a working `useRef<ReturnType<typeof setInterval>>` + conditional start/stop pattern (poll when active runs present, clear on unmount). The `Runs` page is missing this. No new hook library is needed.

**Current gap in `Runs` component (`frontend/pages/runs.ts`):**
- `useEffect` calls `api.getRuns()` once on mount.
- No polling when a run is `running` or `queued`.
- Parity with dashboard: poll every 5s when any run is active, stop when idle.

**Implementation:** Extract the polling logic from `dashboard.ts` into a `useInterval` custom hook (`frontend/hooks/use-interval.ts`), then use it in both `Dashboard` and `Runs`. This deduplicates ~15 lines of poll/cleanup logic.

**Confidence:** HIGH — direct code pattern from existing dashboard, verified working in Phase 1–4.

---

### `queued_at` Timestamp

**Decision: Add `queued_at?: string` to `Run` type in `shared/types.ts`. Set it in `api.ts` when enqueuing.**

**Current state:**
- `Run` type has `started_at?: string` (set when worker picks up the run) and `completed_at?: string`.
- No field captures when the run was queued (i.e., when `POST /api/runs` was called).
- The Runs page displays `timeAgo(run.started_at)` — queued runs with no `started_at` show `—`.

**Change scope:**
1. `shared/types.ts` — add `queued_at?: string` to `Run` interface.
2. `server/routes/api.ts` — set `queued_at: new Date().toISOString()` when constructing the `Run` object (lines 28–37 in current `api.ts`).
3. `server/routes/api.ts` — same for the webhook route (lines 70–77).
4. `frontend/pages/runs.ts` — display `queued_at` in the run list when `started_at` is absent.
5. `shared/types.ts` — update `WorkerToServer` types if worker needs to relay queued_at (likely not needed — server sets it).

**Confidence:** HIGH — trivial schema addition, no YAML migration needed (YAML store reads with optional fields gracefully).

---

## v1.0 Baseline Stack (Unchanged)

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

# v1.1: No new packages required
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Custom toast hook (no library) | react-toastify, sonner, hot-toast | Use a library if the toast requirements expand to include: stacking, progress bars, rich actions, or theme matching. Currently overkill — the no-build constraint means any library needs a CDN import or bundler step. |
| Raw `Notification` Web API (no library) | `react-use-notifications` or `use-notification` hooks | Use a wrapper library only if cross-browser fallback behavior needs standardizing. Desktop-only dashboard on localhost has no cross-browser concern. |
| Copy dashboard's `useRef` + `setInterval` pattern | SWR, React Query, TanStack Query | These caching/fetching libraries are excellent for complex stale-while-revalidate needs. This dashboard has simple polling (5s interval, active-only) — a full cache library would be overengineering. |
| `queued_at` field on `Run` type | Separate `queue-store` or event log | A dedicated event log is better for audit trails in multi-user systems. For a single-user dashboard, a timestamp field on the run is sufficient. |
| Bun native IPC (`Bun.spawn` + `ipc` handler) | Unix domain socket via `node:net` | Use `node:net` if the worker needs to be a non-Bun process. For this project, both server and worker are Bun, so native IPC is simpler — no socket file cleanup, no reconnect loop, structured clone serialization. |
| Preact + HTM (no build) | Preact + Vite | Vite is the right choice if the frontend grows beyond ~10 components or if tree-shaking matters. For this dashboard (internal tool, Bun serves it), no build step is simpler to maintain. Switch if performance becomes an issue. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `react-toastify` or `sonner` | Both require npm install + either bundler or esm.sh CDN. No-build constraint makes this complicated and fragile. Toast is ~50 lines of Preact — not worth the dependency. | Custom `useToast` hook |
| `Notification.requestPermission()` on page load | Chrome and Firefox block this (user gesture required). Will silently fail or show a browser warning. | Request on first run trigger (user gesture context) |
| `window.Notification` without feature detection | Throws in non-browser environments (Bun SSR tests). Always gate: `if ('Notification' in window && Notification.permission !== 'denied')` | Feature-detected notification wrapper |
| Service Worker for notifications | Needed for push/mobile; overkill for this localhost desktop dashboard. Adds 50+ lines of SW registration + caching to a zero-config app. | `new Notification()` directly |
| Adding a polling library (SWR, React Query) | Heavyweight for a 5s interval pattern. The dashboard already implements its own polling correctly. | Extract `useInterval` hook from dashboard's existing `setInterval` logic |
| Express or Fastify | Not Bun-native — wrap Node.js HTTP which is slower and heavier. Hono is designed for Web Standards runtimes. | Hono |
| React (full) | 45KB+ bundle for a single-user internal dashboard. No SSR needed. | Preact + HTM |
| `socket.io` | Requires Node.js adapter + extra binary protocol. Bun has WebSocket built into `Bun.serve()` and Hono wraps it cleanly. | Hono `upgradeWebSocket` from `hono/bun` |
| `node:child_process.spawn` | Works on Bun but misses Bun-specific features. `Bun.spawn()` returns a `ReadableStream` for stdout (cleaner async), has native timeout, and integrates with `AbortSignal`. | `Bun.spawn()` |
| MCP SDK v2 pre-alpha | "We anticipate a stable v2 release in Q1 2026" — not stable yet. v1.27.x is the recommended production version. | `@modelcontextprotocol/sdk@^1.27.1` |

## Stack Patterns by Variant

**Toast position strategy:**
- Use `position: fixed; bottom: 24px; right: 24px; z-index: 200` — above TriggerDialog (`z-index: 100`) and BottomNav.
- Stack multiple toasts vertically with `gap: 8px` using a flex column container.
- Auto-dismiss at 3s for success, 5s for error (keep error visible longer for user action).

**Browser notification permission strategy:**
- Check `Notification.permission` before every `new Notification()` call.
- Request permission inside the `handleTrigger` callback in `dashboard.ts` — this is user-gesture context (button click inside TriggerDialog → Start Run).
- Store "asked once" state in `sessionStorage` to avoid re-prompting on page refresh during the same session.

**Auto-refresh parity pattern:**
- Extract to `frontend/hooks/use-poll.ts`:
  ```typescript
  // usePoll(fn, intervalMs, enabled)
  // enabled: boolean — polling only runs when true
  // Returns: void
  // Cleanup: clearInterval on unmount or enabled→false
  ```
- `Dashboard` uses: `usePoll(loadRuns, 5_000, hasActiveRun)`
- `Runs` uses: `usePoll(loadRuns, 5_000, runs.some(r => r.status === 'running' || r.status === 'queued'))`

**`queued_at` display strategy:**
- In run list: show `timeAgo(run.queued_at ?? run.started_at)` — queued runs show time since queuing; running/completed runs show time since start.
- Queue badge in TargetDetail: filter `runs` where `status === 'queued' && target === selectedTarget`. Count > 0 → show badge "N queued".

**`run-failed` SSE event (server change):**
- In `ipc.ts`, case `'run:failed'`: add `broadcastGlobal('run-failed', { run_id: msg.run_id, error: msg.error })` after `closeRunSubscribers()`.
- In `app.ts`, add `es.addEventListener('run-failed', ...)` handler alongside `brief-ready`.
- This enables browser notification on failure without polling.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| `hono@4.12.x` | `bun@1.2.x` | Official Bun support. Import `upgradeWebSocket` from `hono/bun` specifically. |
| `@modelcontextprotocol/sdk@1.27.x` | `hono@4.x` | Use `@hono/mcp@0.2.4` for the Hono middleware. These are independent packages — SDK handles the protocol, @hono/mcp handles route mounting. |
| `preact@10.23.x` + `htm@3.1.1` | Bun frontend transpile | Bun handles `.ts` files with tagged template literals natively. No `.babelrc` or `jsxImportSource` config needed for HTM (HTM bypasses JSX transform entirely). |
| `yaml@2.x` | `zod@3.x` | No compatibility concern — independent packages. |
| `bun@1.2.x` `node:net` | Unix domain sockets | Verified: `Bun.serve({ unix: '/path/to/sock' })` and `node:net` both support Unix sockets in Bun 1.2+. Use `node:net` for the IPC transport (server + worker) to get full TCP-style socket API with reconnect support. |
| Browser Notification API | localhost (no HTTPS needed) | localhost is a secure context by spec — `Notification.requestPermission()` works without HTTPS. Verified in Chrome and Firefox. |

## Sources

**v1.0 sources:**
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

**v1.1 sources:**
- [MDN: Using the Notifications API](https://developer.mozilla.org/en-US/docs/Web/API/Notifications_API/Using_the_Notifications_API) — permission states, secure context requirement, user gesture requirement, `new Notification()` signature — HIGH confidence
- [MDN: Notification.requestPermission()](https://developer.mozilla.org/en-US/docs/Web/API/Notification/requestPermission_static) — promise-based API, callback deprecated — HIGH confidence
- [Chrome Lighthouse: notification-on-start](https://developer.chrome.com/docs/lighthouse/best-practices/notification-on-start) — do not request on page load; request in user gesture — HIGH confidence
- [Preact no-build workflows guide v11](https://preactjs.com/guide/v11/no-build-workflows/) — custom hooks work identically to React hooks in HTM/Preact — HIGH confidence
- [overreacted.io: Making setInterval Declarative with React Hooks](https://overreacted.io/making-setinterval-declarative-with-react-hooks/) — canonical useInterval pattern, applies to Preact identically — HIGH confidence
- Existing codebase (dashboard.ts lines 54–62) — working polling pattern in production, Phase 1–4 validated — HIGH confidence

---
*Stack research for: Nightwatch Dashboard (Bun + Hono + Preact autonomous agent platform)*
*Researched: 2026-03-18 (v1.0) / 2026-03-20 (v1.1 addendum)*
