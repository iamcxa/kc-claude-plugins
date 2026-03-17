---
phase: 2
slug: core-cockpit
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-18
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | bun test (built-in, from Phase 1) |
| **Config file** | app/bunfig.toml (exists) |
| **Quick run command** | `bun test` |
| **Full suite command** | `bun test --coverage` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `bun test`
- **After every plan wave:** Run `bun test --coverage`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | EXEC-01..09 | unit+integration | `bun test tests/server/api.test.ts` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 1 | EXEC-06, HIST-04 | integration | `bun test tests/server/sse.test.ts` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 1 | SCHED-01..03 | unit | `bun test tests/worker/scheduler.test.ts` | ❌ W0 | ⬜ pending |
| 02-02-02 | 02 | 1 | EXEC-04, MEM-01..03 | unit | `bun test tests/worker/target-resolver.test.ts` | ❌ W0 | ⬜ pending |
| 02-03-01 | 03 | 2 | DASH-01..05 | manual | Browser visual check | N/A | ⬜ pending |
| 02-03-02 | 03 | 2 | HIST-01..03 | manual | Browser visual check | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Test stubs for API routes, SSE streaming, scheduler, target resolver
- [ ] Test helpers for creating mock Run objects and IPC messages

*Phase 1 test infrastructure (bunfig.toml, bun test) already exists.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Dashboard renders target cards with correct data | DASH-01 | Visual rendering in browser | Open http://localhost:3200, verify target list + detail panel |
| SSE log stream updates in real-time | EXEC-06 | Browser SSE connection | Trigger run, watch log panel update line-by-line |
| Trigger modal blocks double-trigger | EXEC-09 | UI interaction | Click Run while run active, verify button disabled |
| Run history filters work | HIST-03 | UI interaction | Filter by status and target, verify list updates |
| Schedule bar countdown updates | SCHED-01 | Real-time visual | Enable scheduler, verify countdown ticks |
| Master-detail layout responsiveness | DASH-01 | Visual | Resize browser, verify sidebar + detail panel behavior |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
