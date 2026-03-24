---
phase: 12
slug: test-infra-run-ux-fixes
status: draft
nyquist_compliant: true
wave_0_complete: true
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
| 12-01-01 | 01 | 1 | TEST-01 | unit | `bun test` (full suite) | YES | pending |
| 12-02-01 | 02 | 1 | RUNUX-01 | unit+api | `bun test tests/server/log-route.test.ts` | YES (Task 1 creates) | pending |
| 12-02-02 | 02 | 1 | RUNUX-01 | implementation | `bun test tests/server/log-route.test.ts tests/worker/log-parser.test.ts` | YES | pending |
| 12-02-03 | 02 | 1 | RUNUX-03 | manual | verify `package.json` has `--watch` | YES | pending |
| 12-03-01 | 03 | 1 | RUNUX-02 | unit+api | `bun test tests/server/target-validation.test.ts` | YES (Task 1 creates) | pending |
| 12-03-02 | 03 | 1 | RUNUX-02 | implementation | `bun test tests/server/target-validation.test.ts` | YES | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- Existing test infrastructure covers TEST-01 (all test files exist, just failing in full suite)
- **RUNUX-01:** Plan 12-02 Task 1 creates `tests/server/log-route.test.ts` (TDD RED) before Task 2 implements the route (GREEN)
- **RUNUX-02:** Plan 12-03 Task 1 creates `tests/server/target-validation.test.ts` (TDD RED) before Task 2 implements validation (GREEN)

*All Wave 0 test files are created by dedicated TDD tasks that precede implementation.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Auto-restart on code change | RUNUX-03 | Requires running server + file edit | 1. `bun run start` 2. Edit any .ts file 3. Verify server restarts in terminal |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 5s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** ready
