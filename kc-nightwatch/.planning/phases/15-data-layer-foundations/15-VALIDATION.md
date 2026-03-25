---
phase: 15
slug: data-layer-foundations
status: draft
nyquist_compliant: false
wave_0_complete: false
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
| 15-01-01 | 01 | 1 | VIZ-01, SIG-02, SIG-03 | unit | `cd app && bun test tests/server/calibration.test.ts` | ✅ | ⬜ pending |
| 15-02-01 | 02 | 1 | — | unit | `cd app && bun test tests/server/forge.test.ts` | ❌ W0 | ⬜ pending |
| 15-03-01 | 03 | 1 | — | unit | `cd app && bun test tests/server/signals.test.ts` | ❌ W0 | ⬜ pending |
| 15-04-01 | 04 | 2 | VIZ-01 | unit | `cd app && bun test tests/server/health-api.test.ts` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `app/tests/server/forge.test.ts` — stubs for forge results endpoint
- [ ] `app/tests/server/signals.test.ts` — stubs for signal priority endpoint

*Existing test infrastructure (bun:test, fixtures) covers all other needs.*

---

## Manual-Only Verifications

*All phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
