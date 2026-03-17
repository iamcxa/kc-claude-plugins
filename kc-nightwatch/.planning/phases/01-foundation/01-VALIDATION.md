---
phase: 1
slug: foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-18
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | bun test (built-in) |
| **Config file** | none — Wave 0 installs |
| **Quick run command** | `bun test` |
| **Full suite command** | `bun test --coverage` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `bun test`
- **After every plan wave:** Run `bun test --coverage`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | FOUND-01 | unit | `bun test app/shared/` | ❌ W0 | ⬜ pending |
| 01-01-02 | 01 | 1 | FOUND-01 | integration | `bun test app/server/ipc.test.ts` | ❌ W0 | ⬜ pending |
| 01-02-01 | 02 | 1 | FOUND-05 | unit | `bun test app/worker/executor.test.ts` | ❌ W0 | ⬜ pending |
| 01-02-02 | 02 | 1 | FOUND-06 | integration | `bun test app/worker/orphan.test.ts` | ❌ W0 | ⬜ pending |
| 01-03-01 | 03 | 1 | FOUND-02,03 | integration | `bun test app/server/lifecycle.test.ts` | ❌ W0 | ⬜ pending |
| 01-03-02 | 03 | 1 | SEC-01,02,03 | integration | `bun test app/server/auth.test.ts` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `app/package.json` — init bun project with typescript
- [ ] `app/tsconfig.json` — strict mode
- [ ] `app/shared/types.ts` — core types (Run, Target, AppConfig, IPC messages)
- [ ] Test stubs for IPC, executor, lifecycle, auth

*Existing infrastructure: none — greenfield `app/` directory.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Worker auto-restart 3x with backoff | FOUND-03 | Requires timing observation | Start server, kill worker 4 times, verify 3 restarts then read-only mode |
| Orphaned safehouse process cleanup | FOUND-06 | Requires spawning real claude -p | Start a run, kill server mid-run, restart server, verify orphan killed |
| mprocs integration | FOUND-01 | Requires mprocs environment | Add to mprocs.yaml, verify startup/shutdown behavior |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
