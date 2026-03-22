---
phase: 11
slug: frontend-outcomes-ui-polish
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-22
---

# Phase 11 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Bun test (built-in) |
| **Config file** | none — Bun discovers `app/tests/**/*.test.ts` automatically |
| **Quick run command** | `cd /Users/kent/Project/kc-claude-workspace/kc-claude-plugins/kc-nightwatch/app && bun test tests/server/outcomes-api.test.ts` |
| **Full suite command** | `cd /Users/kent/Project/kc-claude-workspace/kc-claude-plugins/kc-nightwatch/app && bun test` |
| **Estimated runtime** | ~8 seconds |

---

## Sampling Rate

- **After every task commit:** Run `bun test tests/server/outcomes-api.test.ts`
- **After every plan wave:** Run `bun test` (full suite)
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 11-01-01 | 01 | 1 | OUT-02 | unit (route) | `bun test tests/server/outcomes-api.test.ts` | ❌ W0 | ⬜ pending |
| 11-01-02 | 01 | 1 | OUT-04 | unit (route) | `bun test tests/server/outcomes-api.test.ts` | ❌ W0 | ⬜ pending |
| 11-02-01 | 02 | 1 | PARA-04 | manual visual | n/a — frontend Preact component | manual | ⬜ pending |
| 11-02-02 | 02 | 1 | SCHED-06 | manual visual | n/a — frontend Preact component | manual | ⬜ pending |
| 11-02-03 | 02 | 1 | SCHED-07 | manual visual | n/a — frontend Preact component | manual | ⬜ pending |
| 11-02-04 | 02 | 1 | AUTO-04 | manual visual | n/a — frontend Preact component | manual | ⬜ pending |
| 11-02-05 | 02 | 1 | OUT-01 | manual visual | n/a — frontend Preact component | manual | ⬜ pending |
| 11-02-06 | 02 | 1 | UI-01 | manual visual | n/a — CSS layout | manual | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `app/tests/server/outcomes-api.test.ts` — covers OUT-02 (GET /api/outcomes filter), OUT-04 (GET /api/outcomes/:id/status), route 404 behavior
- [ ] Framework already installed — no setup needed

*Existing infrastructure: bun test, 23 test files, outcome-store.test.ts already exists as reference*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Sidebar dots reflect running/queued state | PARA-04 | Frontend Preact component — no headless test infra | Trigger 2+ targets, verify sidebar dots change color |
| Target detail shows "Next: HH:MM" | SCHED-06 | Frontend rendering | Open target detail, verify schedule section appears |
| Wizard step 4 validates interval floor | SCHED-07 | Frontend form interaction | Enter value < 0.17, verify inline error |
| Action card status badge renders | AUTO-04 | Frontend rendering | View run with outcome, verify badge color/text |
| Action card clickable URL | OUT-01 | Frontend rendering | Click link, verify new tab opens correct URL |
| No nav gap | UI-01 | Visual CSS layout | Scroll to bottom, verify no black line above nav |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
