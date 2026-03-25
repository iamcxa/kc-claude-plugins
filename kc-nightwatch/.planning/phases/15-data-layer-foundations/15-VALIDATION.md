---
phase: 15
slug: data-layer-foundations
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-25
---

# Phase 15 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | bun:test (built-in) |
| **Config file** | `app/bunfig.toml` |
| **Quick run command** | `cd app && bun test` |
| **Full suite command** | `cd app && bun test` |
| **Estimated runtime** | ~3 seconds (373 tests) |

---

## Sampling Rate

- **After every task commit:** Run `cd app && bun test`
- **After every plan wave:** Run `cd app && bun test`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 15-01-01 | 01 | 1 | VIZ-01, SIG-02, SIG-03 | unit | `cd app && bun test tests/server/calibration.test.ts tests/server/feedback.test.ts` | ✅ | ⬜ pending |
| 15-02-01 | 02 | 2 | VIZ-01 | unit | `cd app && bun test tests/server/forge.test.ts` | ✅ (created in task) | ⬜ pending |
| 15-02-02 | 02 | 2 | SIG-02, SIG-03 | unit | `cd app && bun test tests/server/signals.test.ts` | ✅ (created in task) | ⬜ pending |
| 15-02-03 | 02 | 2 | VIZ-01 | unit | `cd app && bun test tests/server/health-api.test.ts` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

**Note:** Plan 02 Tasks 1 and 2 create their test files (forge.test.ts, signals.test.ts) alongside the production code within the same task. No separate Wave 0 test stub step is needed — each task writes tests as part of its implementation.

---

## Wave 0 Requirements

*None. All test files either already exist (calibration.test.ts, feedback.test.ts, health-api.test.ts) or are created inline by the task that implements the feature (forge.test.ts, signals.test.ts in Plan 02 Tasks 1-2).*

---

## Manual-Only Verifications

*All phase behaviors have automated verification.*

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or create tests inline
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] No Wave 0 gaps — all test files accounted for
- [x] No watch-mode flags
- [x] Feedback latency < 5s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
