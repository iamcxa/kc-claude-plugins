---
phase: 12
slug: test-infra-run-ux-fixes
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-24
---

# Phase 12 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Bun test (built-in) |
| **Config file** | none — Bun test uses defaults |
| **Quick run command** | `bun test --filter {related}` |
| **Full suite command** | `bun test` |
| **Estimated runtime** | ~3 seconds |

---

## Sampling Rate

- **After every task commit:** Run `bun test --filter {related}`
- **After every plan wave:** Run `bun test`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 12-01-01 | 01 | 1 | TEST-01 | unit | `bun test` (full suite) | ✅ | ⬜ pending |
| 12-02-01 | 02 | 2 | RUNUX-01 | unit+api | `bun test --filter log` | ❌ W0 | ⬜ pending |
| 12-02-02 | 02 | 2 | RUNUX-02 | unit+api | `bun test --filter wizard\|target` | ❌ W0 | ⬜ pending |
| 12-02-03 | 02 | 2 | RUNUX-03 | manual | verify `package.json` has `--watch` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- Existing test infrastructure covers TEST-01 (all test files exist, just failing in full suite)
- New tests needed for RUNUX-01 (log endpoint) and RUNUX-02 (path validation) — created during implementation

*Existing infrastructure covers most phase requirements. New tests added alongside implementation.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Auto-restart on code change | RUNUX-03 | Requires running server + file edit | 1. `bun run start` 2. Edit any .ts file 3. Verify server restarts in terminal |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
