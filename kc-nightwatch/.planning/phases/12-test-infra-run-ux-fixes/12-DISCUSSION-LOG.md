# Phase 12: Test Infrastructure + Run UX Fixes - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-24
**Phase:** 12-test-infra-run-ux-fixes
**Areas discussed:** Run log display, Path validation, Auto-restart
**Method:** decision-debate skill (triage → direct answers based on facts)

---

## Run Log Display (RUNUX-01)

| Option | Description | Selected |
|--------|-------------|----------|
| Simple GET → full JSONL | Read `runs/{id}/log.jsonl`, return full content | ✓ |
| Paginated/chunked GET | Split response for large logs | |
| SSE replay | Re-use SSE endpoint for completed runs | |

**User's choice:** Simple GET — full JSONL
**Notes:** Triage data: max observed log is 322 lines / 542KB. Pagination is over-engineering at these sizes. Frontend reuses existing stream-json parser.

---

## Path Validation (RUNUX-02)

| Option | Description | Selected |
|--------|-------------|----------|
| Frontend-only (non-empty) | Disable submit when path empty | |
| Frontend non-empty + server existsSync | Defense in depth — catches both empty and invalid paths | ✓ |
| + git repo check | Also verify path is a git repo | |

**User's choice:** Frontend + server validation (defense in depth)
**Notes:** Same pattern as Phase 9 minimum interval enforcement (D-12~D-14). Catches typos and deleted directories at the API layer.

---

## Auto-Restart (RUNUX-03)

| Option | Description | Selected |
|--------|-------------|----------|
| Document "use bun run dev" | Already works, just document | |
| Make start = dev (always watch) | Single entry point, --watch always on | ✓ |
| Add mprocs.yaml with watch | Separate process manager | |

**User's choice:** Merge start and dev scripts — always use --watch
**Notes:** No mprocs setup exists. bun --watch is native and negligible overhead. Local-only tool has no reason for non-watch mode. Worker restarts automatically because server spawns it.

---

## Claude's Discretion

- Test mock isolation strategy for TEST-01 (21 failures from Bun mock.module contamination)
- GET /api/runs/:id/log response format details
- existsSync vs async file check
- Log endpoint error handling

## Deferred Ideas

None.
