# Phase 12: Test Infrastructure + Run UX Fixes - Research

**Researched:** 2026-03-24
**Domain:** Bun test isolation, Hono route extension, Preact frontend, server hot-reload
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Run Log Display (RUNUX-01)**
- D-01: Simple `GET /api/runs/:id/log` endpoint reads `runs/{id}/log.jsonl` and returns full content — no pagination, no chunking
- D-02: Largest observed log is 322 lines / 542KB — trivially small for a single HTTP response
- D-03: Frontend reuses the existing stream-json event parser to render log lines (same rendering path as SSE live view)

**Path Validation (RUNUX-02)**
- D-04: Defense in depth — frontend disables submit when path is empty (inline validation error), server returns 400 if path empty or `!existsSync(path)`
- D-05: Same pattern as minimum interval enforcement (Phase 9 D-12~D-14): validate at BOTH UI and API layers
- D-06: Server validation applies to both Add Target and Edit Target flows

**Auto-Restart (RUNUX-03)**
- D-07: Merge `start` and `dev` scripts — make `start` include `--watch` flag. No reason to have a non-watch mode for a local-only dev tool
- D-08: `bun --watch` is Bun-native, watches all imported files, and is negligible overhead
- D-09: Worker auto-restarts because server spawns it via `Bun.spawn` — parent restart = child restart

**Test Mock Contamination (TEST-01)**
- D-10: Root cause: Bun `mock.module()` pollutes module cache across test files in full-suite runs; tests pass in isolation but fail together
- D-11: 21 failures + 8 errors concentrated in: YAML config tests, outcome store tests, auto-action tests, config routes tests, Linear status tests

### Claude's Discretion
- Test isolation strategy (per-file mock cleanup, Bun `--preload`, test file restructuring, or other approach)
- `GET /api/runs/:id/log` response format (raw JSONL vs parsed JSON array)
- Whether `existsSync` check runs synchronously or via `Bun.file().exists()`
- Log endpoint error handling (run not found, log file missing)

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TEST-01 | Fix Bun mock.module cross-file contamination — 21 false failures in full suite | Root cause verified: mock.module persists in module cache permanently; solution: restructure contaminating files to use spyOn + restore |
| RUNUX-01 | Completed run detail reads log from file via GET /api/runs/:id/log | Route pattern from stream.ts confirmed reusable; log.jsonl format from executor.ts verified; LogStream component needs conditional fetch path |
| RUNUX-02 | Target `path` field required in Add Target wizard | Wizard file line 77 confirmed: `path: targetPath || undefined`; validation pattern from config.ts (400 response); frontend: disable Next on step 1 when path empty |
| RUNUX-03 | Server auto-restart on code change via Bun --watch | package.json confirmed: `start` script lacks `--watch`, `dev` has it; D-09 worker auto-restarts via Bun.spawn parent chain |
</phase_requirements>

---

## Summary

Phase 12 addresses four independent, low-risk fixes with no dependencies between them. Three are UX gaps in the live dashboard, one is test infrastructure cleanup.

The root cause of TEST-01 is definitively understood and verified by live test run: `mock.module()` in Bun 1.3.9 permanently overwrites the module registry entry within the process lifetime. `mock.restore()` explicitly does NOT restore module mocks (confirmed in Bun docs). Test files that call `mock.module('../../server/services/yaml-store.ts')` poison that module for all subsequent test files in the same run. The correct fix is to avoid `mock.module()` in integration-style test files that test real I/O (outcome-store, yaml-store, linear-status) — instead use `spyOn` with `mockRestore()`, which is correctly scoped to the current test.

The RUNUX-01 bug is straightforward: `LogStream` calls `connectSSE()` on mount, but the function returns early when `isCompleted=true` (line 65-66 in log-stream.ts), leaving `phases` empty and rendering "Waiting for output..." permanently. The fix is to fetch the completed log from a new endpoint and pipe events into the same phase-grouping logic.

RUNUX-02 and RUNUX-03 are one-liner changes with clear patterns already established in the codebase.

**Primary recommendation:** Fix test contamination by converting `mock.module()` calls in files that test real implementations to `spyOn`-based mocks with `afterEach` restore. No preload file needed.

---

## Standard Stack

### Core (already installed)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Bun | 1.3.9 | Runtime + test runner | Project standard |
| Hono | ^4.12.8 | HTTP server + routing | Already in use |
| Preact (htm) | vendor | Frontend rendering | Already in use |

### No new dependencies needed
All four fixes use existing installed libraries.

---

## Architecture Patterns

### Pattern 1: Bun Test Mock Isolation

**What:** The contamination is caused by `mock.module()` overwriting Bun's module registry permanently within a process. Files like `mcp.test.ts` and `mcp-outcomes.test.ts` call `mock.module('../../server/services/yaml-store.ts', ...)` which replaces the real module for ALL subsequent test files.

**Confirmed contaminating files (use `mock.module` on shared modules):**
- `tests/server/mcp.test.ts` — mocks yaml-store, outcome-store, run-store, feedback-collector, feedback-store
- `tests/server/mcp-outcomes.test.ts` — mocks outcome-store, yaml-store, run-store, feedback-store
- `tests/server/chat-tools.test.ts` — mocks yaml-store, @anthropic-ai/sdk, MCP SDK
- `tests/server/health-api.test.ts` — mocks yaml-store
- `tests/server/outcomes-api.test.ts` — mocks outcome-store, run-store, yaml-store
- `tests/server/config-validator.test.ts` — mocks @anthropic-ai/sdk only (lower blast radius)

**Files that fail due to contamination (use real I/O, need real modules):**
- `tests/server/yaml-store.test.ts` — tests real `loadOrCreateAppConfig`, `readYamlFile`
- `tests/server/outcome-store.test.ts` — tests real `readOutcomes`, `appendOutcome`, `queryOutcomes`
- `tests/worker/auto-action.test.ts` — uses `spyOn` but outcome-store mock is already baked in from prior file
- `tests/worker/linear-status.test.ts` — uses dynamic `import()` but module is already replaced

**The fix (Claude's discretion):**

Two viable approaches:

**Option A: spyOn in contaminating files (preferred)**
- In `mcp.test.ts`, `mcp-outcomes.test.ts`, etc.: replace `mock.module(...)` at file top with `spyOn` calls inside `beforeEach`
- Add `afterEach(() => { appendSpy.mockRestore() })` for each spy
- Works because `spyOn` modifies the live binding on the exported object, not the module cache
- Does not affect which module the system-under-test imported at load time — fine for these files since they test the HTTP handler (which doesn't hold a reference to the module itself)

**Option B: Restructure affected test files to not require real module**
- Move `mock.module` calls into test files that NEED them (mcp.test.ts) and remove from files that don't strictly need real I/O
- Keep `mock.module` ONLY in files that are self-contained and have no downstream victims

**Recommended: Option A** — lowest total change surface, preserves test intent.

**Critical Bun behavior (confirmed from docs):**
- `mock.restore()` does NOT restore module mocks
- `mock.module()` effects are permanent for the process
- There is NO per-file module cache reset in Bun 1.3.9
- `--preload` is for setup that should run before tests, not for cleanup

```typescript
// BEFORE (contaminates all subsequent test files):
mock.module('../../server/services/yaml-store.ts', () => ({
  readYamlFile: mock(async () => null),
  // ...
}))

// AFTER (scoped to tests in this file only):
import * as yamlStore from '../../server/services/yaml-store.ts'

let readSpy: ReturnType<typeof spyOn>
beforeEach(() => {
  readSpy = spyOn(yamlStore, 'readYamlFile').mockResolvedValue(null)
})
afterEach(() => {
  readSpy.mockRestore()
})
```

**When spyOn is not viable:** For files that need to mock entire modules with constructors (e.g., `new MockAnthropic()`), use `mock.module` BUT only in test files that do not have downstream victims. `config-validator.test.ts` mocks `@anthropic-ai/sdk` — this is safe because no other test file imports Anthropic SDK through a chain that touches yaml-store or outcome-store directly.

### Pattern 2: GET /api/runs/:id/log Route

**Route registration pattern** (from `stream.ts`):
```typescript
// Source: app/server/routes/stream.ts
export const streamRoutes = new Hono()
streamRoutes.get('/api/runs/:id/stream', (c) => { ... })
```

New log route follows same pattern — add to `streamRoutes` or create new `logRoutes`:

```typescript
// GET /api/runs/:id/log — fetch completed run log as parsed events
streamRoutes.get('/api/runs/:id/log', async (c) => {
  const runId = c.req.param('id')
  const runDir = path.join(RUNS_DIR, runId)
  const logPath = path.join(runDir, 'log.jsonl')

  const exists = await Bun.file(logPath).exists()
  if (!exists) {
    return c.json({ error: 'log not found' }, 404)
  }

  const text = await Bun.file(logPath).text()
  const lines = text.split('\n').filter(Boolean)
  // Return as-is (raw JSONL text) or as parsed JSON array — Claude's discretion
  return c.json({ lines })
})
```

**RUNS_DIR path:** executor.ts uses `opts.runsDir` passed from worker. The server needs to know where `runs/` lives. It's `path.join(import.meta.dir, '../../runs')` relative to `app/server/routes/`. Alternatively: `run.log_path` is stored in the run record as `runs/{id}/log.jsonl` — server can resolve from this field using the server's base directory.

**Response format decision (Claude's discretion):**
- Raw JSONL text: frontend parses using `parseStreamJsonLine` (already available in `worker/log-parser.ts`)
- Parsed JSON array: `{ lines: ParsedLogEvent[] }` — simpler for frontend
- Recommended: `{ lines: string[] }` (raw JSONL lines) — consistent with how executor writes them, and `parseStreamJsonLine` is already a tested, reusable function

### Pattern 3: LogStream — Conditional Fetch for Completed Runs

The existing `LogStream` component in `log-stream.ts` at line 65:
```typescript
function connectSSE() {
  if (isCompleted) return  // BUG: returns early, phases stays empty
  // ...
}
```

Fix: add a `useEffect` that fires when `isCompleted=true` to fetch from `GET /api/runs/:id/log`:

```typescript
useEffect(() => {
  if (!isCompleted) return
  // Fetch completed log from file
  fetch(`/api/runs/${runId}/log`)
    .then(r => r.json())
    .then(({ lines }) => {
      const events = lines.map(parseStreamJsonLine)
      // Feed events into phase grouping
      setPhases(events.reduce(appendToPhases, []))
      setRawLines(lines)
    })
    .catch(console.error)
}, [runId, isCompleted])
```

Note: `parseStreamJsonLine` lives in `worker/log-parser.ts`. The frontend currently imports types from `../../shared/types.ts` — it does NOT currently import `parseStreamJsonLine`. Options:
- Move `parseStreamJsonLine` to `shared/` (cleaner, reusable)
- Duplicate the minimal parsing logic inline in the frontend (simpler, avoids refactor)
- Recommended: move `parseStreamJsonLine` to `shared/log-parser.ts` since it's pure logic with no Node/Bun imports

### Pattern 4: Path Validation — Defense in Depth

**Frontend** (wizard step 1, `add-target-wizard.ts`):

Current state:
- Line 77: `path: targetPath || undefined` — path is optional
- Next button disabled when `!name.trim() && !isEdit` — no path check

Fix: disable "Next" (step 1 → 2) when `targetPath.trim() === ''`, show inline error:

```typescript
// Step 1 Next button:
disabled=${step === 1 && (!name.trim() && !isEdit || !targetPath.trim())}

// Inline validation error below path input:
${step === 1 && !targetPath.trim() && html`
  <div style="font-size:12px;color:var(--error);margin-top:4px;">Path is required</div>
`}
```

**Server** (config.ts `POST /api/config/targets/add` and `PUT /api/config/targets/:name`):

Add path validation before writing, using `existsSync` from `node:fs`:

```typescript
import { existsSync } from 'node:fs'

// In POST /api/config/targets/add:
const targetData = target as { path?: string }
if (!targetData.path?.trim()) {
  return c.json({ error: 'path is required' }, 400)
}
if (!existsSync(targetData.path)) {
  return c.json({ error: `path does not exist: ${targetData.path}` }, 400)
}
```

**D-06 note:** Applies to both Add AND Edit flows. The edit endpoint is `PUT /api/config/targets/:name` in `config.ts` — same validation added there.

**`existsSync` vs `Bun.file().exists()`:**
- `existsSync` works for both files AND directories (target path is a directory) — correct choice
- `Bun.file().exists()` is only for files

### Pattern 5: Auto-Restart via `bun --watch`

`package.json` current state:
```json
"scripts": {
  "start": "bun run server/index.ts",
  "dev": "bun --watch run server/index.ts",
  "test": "bun test"
}
```

Fix (D-07): merge `start` and `dev`:
```json
"scripts": {
  "start": "bun --watch run server/index.ts",
  "dev": "bun --watch run server/index.ts",
  "test": "bun test"
}
```

Or simply make `start` be the watch variant. The `dev` alias can remain for backward compat.

**D-09 confirmed:** `server/index.ts` uses `Bun.spawn(['bun', 'run', '...worker/index.ts'])` — when `bun --watch` detects a file change, it restarts the server process. The restarted server calls `spawnWorker()` at startup, which spawns a fresh worker process. Worker auto-restart is fully covered by parent restart.

**`bun --watch` behavior (from Bun docs):**
- Watches all imported files automatically — no `nodemon`-style glob config needed
- Restarts the process when any imported file changes
- Handles TypeScript natively — no transpile step delay

### Anti-Patterns to Avoid

- **Using `mock.module()` in files that test real I/O:** The contamination is permanent per process. Any test file that imports a module previously mocked with `mock.module()` gets the mock, not the real implementation.
- **Relying on `mock.restore()` to undo `mock.module()`:** The Bun docs explicitly state this does not work for module mocks.
- **Adding `--preload` for cleanup:** `--preload` runs BEFORE tests, not between files. It cannot reset per-file state.
- **Using `Bun.file().exists()` for directory paths:** Only valid for files. Target paths are directories; use `existsSync` from `node:fs`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Module cache reset | Custom test runner or per-file worker | spyOn + mockRestore | No Bun API exists for per-file module cache reset; spyOn is scope-safe |
| File watching | chokidar / nodemon wrapper | `bun --watch` (native) | Already a Bun built-in, zero config |
| Log file reading | Custom streaming | `Bun.file(path).text()` | Synchronous full read is correct for 542KB max |

---

## Common Pitfalls

### Pitfall 1: mock.module Cannot Be Un-Mocked

**What goes wrong:** A test calls `mock.module('../../some-module', ...)` then later calls `mock.restore()` expecting the module to be restored. Later test files importing the same module get the mock.
**Why it happens:** Bun's `mock.module()` patches the runtime module registry directly. `mock.restore()` only restores `spyOn`-based function replacements, not module registry entries.
**How to avoid:** Never use `mock.module()` for modules that are shared with test files that need real implementations. Use `spyOn` for function-level mocking — it patches the exported object's property, not the module cache entry.
**Warning signs:** Tests pass in isolation (`bun test tests/foo.test.ts`) but fail in full suite (`bun test`). Failures are in real-I/O tests that follow mock-heavy test files in execution order.

### Pitfall 2: LogStream isCompleted=true with Empty initialEvents

**What goes wrong:** The `LogStream` component is passed `isCompleted=true` and `initialEvents=[]`. It skips `connectSSE()`, phases stays empty, "Waiting for output..." is shown forever.
**Why it happens:** The SSE path and the file-fetch path are mutually exclusive — currently only SSE exists.
**How to avoid:** Add a separate `useEffect` that fires when `isCompleted=true` to fetch from `GET /api/runs/:id/log`.

### Pitfall 3: Path Validation with Bun.file vs existsSync

**What goes wrong:** Using `await Bun.file(path).exists()` to check if a target directory exists — returns `false` for directories.
**Why it happens:** `Bun.file()` is designed for files; directory existence requires `node:fs` `existsSync` or `fs.stat`.
**How to avoid:** Use `existsSync(path)` from `node:fs` for directory existence checks.

### Pitfall 4: parseStreamJsonLine in Frontend Import Chain

**What goes wrong:** `log-parser.ts` imports from `worker/` which may have Bun-specific or Node-specific imports not available in browser context. The server transpiles TypeScript to JavaScript and serves it — if log-parser imports anything that doesn't exist in browser context, it fails at runtime.
**Why it happens:** Worker files may use `node:path`, `node:fs`, etc. The frontend is served as browser JS.
**How to avoid:** Before importing `parseStreamJsonLine` from `worker/log-parser.ts` in the frontend, verify that file has no Node/Bun-specific imports. It doesn't — `log-parser.ts` is pure logic with only TypeScript types. It's safe. Alternatively, move it to `shared/` as a signal that it's environment-agnostic.

### Pitfall 5: RUNS_DIR path resolution in new log route

**What goes wrong:** The new `GET /api/runs/:id/log` route needs to know where the `runs/` directory is. If hardcoded wrong, it fails for every request.
**Why it happens:** `executor.ts` accepts `opts.runsDir` as a parameter. The server's route files need an independent way to resolve this path.
**How to avoid:** The runs directory is `app/runs/` relative to the app root, which is `path.resolve(import.meta.dir, '../../runs')` from inside `app/server/routes/`. Or better: use the `run.log_path` field from the stored run record (e.g., `runs/{id}/log.jsonl`) and resolve it relative to the `app/` root.

---

## Code Examples

### Example 1: Fixing mock.module contamination in mcp.test.ts

```typescript
// Source: verified from tests/server/mcp.test.ts + Bun docs
import { describe, it, expect, spyOn, beforeEach, afterEach } from 'bun:test'
import * as yamlStore from '../../server/services/yaml-store.ts'
import * as outcomeStore from '../../server/services/outcome-store.ts'

let readTargetsSpy: ReturnType<typeof spyOn>
let queryOutcomesSpy: ReturnType<typeof spyOn>

beforeEach(() => {
  readTargetsSpy = spyOn(yamlStore, 'readTargets').mockResolvedValue({})
  queryOutcomesSpy = spyOn(outcomeStore, 'queryOutcomes').mockResolvedValue([])
})

afterEach(() => {
  readTargetsSpy.mockRestore()
  queryOutcomesSpy.mockRestore()
})
```

### Example 2: New GET /api/runs/:id/log route

```typescript
// Source: modeled on app/server/routes/stream.ts pattern
import path from 'node:path'

const APP_ROOT = path.resolve(import.meta.dir, '../..')
const RUNS_DIR = path.join(APP_ROOT, 'runs')

streamRoutes.get('/api/runs/:id/log', async (c) => {
  const runId = c.req.param('id')
  const logPath = path.join(RUNS_DIR, runId, 'log.jsonl')

  const exists = await Bun.file(logPath).exists()
  if (!exists) return c.json({ error: 'log not found' }, 404)

  const text = await Bun.file(logPath).text()
  const lines = text.split('\n').filter(Boolean)
  return c.json({ lines })
})
```

### Example 3: LogStream fetch for completed run

```typescript
// Source: modeled on app/frontend/components/log-stream.ts
useEffect(() => {
  if (!isCompleted) return
  fetch(`/api/runs/${runId}/log`)
    .then(r => r.json() as Promise<{ lines: string[] }>)
    .then(({ lines }) => {
      const events = lines.map(parseStreamJsonLine)
      setPhases(events.reduce(
        (acc: PhaseGroup[], ev) => appendToPhases(acc, ev),
        []
      ))
      setRawLines(lines)
    })
    .catch(console.error)
}, [runId, isCompleted])
```

### Example 4: path validation in server

```typescript
// Source: modeled on app/server/routes/config.ts validation pattern
import { existsSync } from 'node:fs'

// In POST /api/config/targets/add, before writing:
const targetPath = (target as Record<string, unknown>).path as string | undefined
if (!targetPath?.trim()) {
  return c.json({ error: 'path is required' }, 400)
}
if (!existsSync(targetPath)) {
  return c.json({ error: `path does not exist: ${targetPath}` }, 400)
}
```

---

## Environment Availability

Step 2.6: SKIPPED (no external dependencies identified — all changes are code edits to existing Node/Bun/browser code)

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Bun test v1.3.9 |
| Config file | `app/bunfig.toml` (timeout: 10000) |
| Quick run command | `bun test tests/server/yaml-store.test.ts tests/server/outcome-store.test.ts tests/worker/linear-status.test.ts tests/worker/auto-action.test.ts` |
| Full suite command | `bun test` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TEST-01 | Full suite passes without false failures (21 tests green) | integration | `bun test` (full suite pass = success) | ✅ existing tests |
| RUNUX-01 | Completed run log content fetched from file and rendered | unit | `bun test tests/server/sse.test.ts` (new route test) | ❌ Wave 0: new test for log endpoint |
| RUNUX-02 | Path empty → inline error, submit disabled; server returns 400 | unit | `bun test tests/server/api.test.ts tests/server/config-editor.test.ts` | ✅ existing + Wave 0 assertion |
| RUNUX-03 | `start` script includes `--watch` flag | smoke | manual: verify `package.json` script + restart behavior | ✅ trivial — inspect package.json |

### Sampling Rate
- **Per task commit:** Run subset: `bun test tests/server/yaml-store.test.ts tests/server/outcome-store.test.ts tests/worker/auto-action.test.ts tests/worker/linear-status.test.ts`
- **Per wave merge:** `bun test` (full suite)
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/server/log-route.test.ts` (or extend `tests/server/api.test.ts`) — covers RUNUX-01: tests `GET /api/runs/:id/log` returns 200 with `{ lines: [...] }` for existing log, 404 for missing run
- [ ] Path validation assertions in `tests/server/config-editor.test.ts` or a new `tests/server/target-validation.test.ts` — covers RUNUX-02: tests that empty path returns 400

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `jest.fn()` for module mocking | Bun `mock.module()` | Bun adoption | mock.module has permanent process-wide effects unlike Jest's per-test isolation |
| `nodemon` / `ts-node-dev` for watch | `bun --watch` native | Bun adoption | Zero config, no file glob needed |

**Deprecated/outdated:**
- `mock.module()` for test files that need to co-exist with real-I/O tests: use `spyOn` instead

---

## Open Questions

1. **Where to add new `GET /api/runs/:id/log` route**
   - What we know: stream.ts exports `streamRoutes`; api.ts exports `apiRoutes`; both are registered in `server/index.ts`
   - What's unclear: whether to add to `streamRoutes` (thematically appropriate) or `apiRoutes` (REST convention) or a new file
   - Recommendation: add to `streamRoutes` (keeps run-related streaming/log routes together) — low impact either way

2. **Where to add `parseStreamJsonLine` import in frontend**
   - What we know: `log-parser.ts` is in `worker/`, has no Node/Bun-specific imports (verified)
   - What's unclear: whether to move to `shared/` for semantic clarity
   - Recommendation: move to `shared/log-parser.ts` — it's pure logic used by both worker (during execution) and frontend (during replay); rename the import in `worker/` to point to `shared/`

3. **Path validation in wizard: which step shows the error**
   - What we know: Path input is on Step 1; `name` is also on Step 1; Next button is disabled when name is empty
   - Unclear: whether to block at Next (step 1 → 2) or only at Save (step 5) — D-04 says "disables submit"
   - Recommendation: block at step 1 Next button (consistent with name validation), not at final save — better UX to catch early

---

## Sources

### Primary (HIGH confidence)
- Direct code inspection: `app/server/routes/stream.ts`, `app/server/routes/config.ts`, `app/server/routes/api.ts`, `app/frontend/components/log-stream.ts`, `app/frontend/components/add-target-wizard.ts`, `app/worker/log-parser.ts`, `app/worker/executor.ts`, `app/package.json`
- Bun docs (WebFetch): https://bun.sh/docs/test/mocks — confirmed `mock.restore()` does NOT restore module mocks
- Bun docs (WebFetch): https://bun.sh/docs/cli/test — confirmed single-process test runner, no per-file isolation

### Secondary (MEDIUM confidence)
- Live `bun test` run output — verified 21 failures + 8 errors in full suite, 0 failures in isolation
- Cross-file contamination confirmed: `bun test tests/server/mcp.test.ts tests/server/outcome-store.test.ts` reproduces failures; `bun test tests/server/outcome-store.test.ts` alone passes

### Tertiary (LOW confidence)
None.

---

## Project Constraints (from CLAUDE.md)

From `kc-nightwatch/CLAUDE.md`:
- **Commit convention:** Use standard semantic prefixes (`feat`, `fix`, `docs`, `chore`) for human development of the plugin
- **No direct safety.yaml modification:** Changes require human review; this phase doesn't touch safety.yaml

From `~/.claude/CLAUDE.md`:
- **Circuit breaker:** 2 consecutive identical errors → stop and report
- **Root cause first:** Diagnose before proposing fix — done (TEST-01 root cause verified by live test)
- **No fabricated version numbers:** Version pins verified against actual `bun --version` (1.3.9)
- **E2E-First:** Phase changes are code-only (server + frontend) — browser E2E verification is NOT applicable (no mapping for this local dev tool)

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all packages already installed, versions verified
- Architecture: HIGH — root cause verified by live test execution; patterns confirmed from source code
- Pitfalls: HIGH — Bun docs confirmed mock.module behavior; directory existence trap verified from API docs

**Research date:** 2026-03-24
**Valid until:** 2026-04-24 (Bun mock behavior is stable; no fast-moving dependencies)
