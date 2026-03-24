# Phase 12: Test Infrastructure + Run UX Fixes - Context

**Gathered:** 2026-03-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Fix test suite contamination (21 false failures from Bun mock.module cross-file pollution) and close 3 immediate run UX gaps: completed run log display, target path validation, and server auto-restart.

</domain>

<decisions>
## Implementation Decisions

### Run Log Display (RUNUX-01)
- **D-01:** Simple `GET /api/runs/:id/log` endpoint reads `runs/{id}/log.jsonl` and returns full content — no pagination, no chunking
- **D-02:** Largest observed log is 322 lines / 542KB — trivially small for a single HTTP response
- **D-03:** Frontend reuses the existing stream-json event parser to render log lines (same rendering path as SSE live view)

### Path Validation (RUNUX-02)
- **D-04:** Defense in depth — frontend disables submit when path is empty (inline validation error), server returns 400 if path empty or `!existsSync(path)`
- **D-05:** Same pattern as minimum interval enforcement (Phase 9 D-12~D-14): validate at BOTH UI and API layers
- **D-06:** Server validation applies to both Add Target and Edit Target flows

### Auto-Restart (RUNUX-03)
- **D-07:** Merge `start` and `dev` scripts — make `start` include `--watch` flag. No reason to have a non-watch mode for a local-only dev tool
- **D-08:** `bun --watch` is Bun-native, watches all imported files, and is negligible overhead
- **D-09:** Worker auto-restarts because server spawns it via `Bun.spawn` — parent restart = child restart

### Test Mock Contamination (TEST-01)
- **D-10:** Root cause: Bun `mock.module()` pollutes module cache across test files in full-suite runs; tests pass in isolation but fail together
- **D-11:** 21 failures + 8 errors concentrated in: YAML config tests, outcome store tests, auto-action tests, config routes tests, Linear status tests

### Claude's Discretion
- Test isolation strategy (per-file mock cleanup, Bun `--preload`, test file restructuring, or other approach)
- `GET /api/runs/:id/log` response format (raw JSONL vs parsed JSON array)
- Whether `existsSync` check runs synchronously or via `Bun.file().exists()`
- Log endpoint error handling (run not found, log file missing)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing Implementation
- `app/worker/executor.ts` — Log file creation (`log.jsonl`), `--output-format stream-json`, run directory structure
- `app/server/routes/stream.ts` — Current SSE endpoint pattern (`GET /api/runs/:id/stream`)
- `app/frontend/components/add-target-wizard.ts` — Current wizard with optional path (line 77: `path: targetPath || undefined`)
- `app/worker/log-parser.ts` — Stream-json line parser (reusable for GET endpoint rendering)

### Patterns to Follow
- `app/server/routes/config.ts` — Server-side validation pattern (400 responses, min interval enforcement)
- Phase 9 D-12~D-14 — Defense-in-depth validation at both UI and API layers
- `app/package.json` — Scripts section (`dev` already has `--watch`)

### Test Infrastructure
- `app/tests/` — Test directory structure (server/, shared/, worker/ subdirs)
- All failing test files (verify with `bun test` full-suite run)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `log-parser.ts`: Stream-json event parser — reuse for both SSE and GET log rendering
- `stream.ts` SSE pattern: Fan-out subscription model — GET endpoint follows same route registration pattern
- Zod schemas in `shared/types.ts`: Extend `TargetSchema` to make `path` required

### Established Patterns
- Run artifacts stored in `runs/{uuid}/` — `log.jsonl`, `nw-journal.json`, `summary.yaml`
- Server validation returns 400 with error message (config routes pattern)
- Frontend uses Preact signals for form state (wizard pattern)

### Integration Points
- New `GET /api/runs/:id/log` route registers alongside existing `GET /api/runs/:id/stream`
- Wizard path validation hooks into existing signal-based form state
- `package.json` `start` script change affects how server is launched

</code_context>

<specifics>
## Specific Ideas

No specific requirements — standard approaches aligned with existing codebase patterns.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 12-test-infra-run-ux-fixes*
*Context gathered: 2026-03-24*
