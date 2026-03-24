---
phase: 13
slug: worktree-isolation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-24
---

# Phase 13 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | bun:test (built-in) |
| **Config file** | app/bunfig.toml (if exists) or package.json |
| **Quick run command** | `cd app && bun test --filter worktree` |
| **Full suite command** | `cd app && bun test` |
| **Estimated runtime** | ~8 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd app && bun test --filter worktree`
- **After every plan wave:** Run `cd app && bun test`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| TBD | TBD | TBD | WKTREE-01 | unit+integration | `bun test --filter worktree` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | WKTREE-02 | unit | `bun test --filter worktree` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | WKTREE-03 | unit+integration | `bun test --filter worktree` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `app/tests/worker/worktree-manager.test.ts` — stubs for WKTREE-01, WKTREE-02, WKTREE-03
- [ ] Test helper: create temporary git repos for worktree testing (similar to executor.test.ts pattern)

*Existing test infrastructure (bun:test, spyOn) covers framework needs.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Full run with worktree in dashboard | WKTREE-01~03 | Requires live Claude session + safehouse | Trigger dry-run via dashboard, verify worktree created and cleaned up |
| Git status unchanged after run | WKTREE-03 | Requires real target repo with pre-existing state | Run `git status` before and after nightwatch run on a real target |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
