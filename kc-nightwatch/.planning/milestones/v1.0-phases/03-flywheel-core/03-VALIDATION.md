---
phase: 03
slug: flywheel-core
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-18
---

# Phase 03 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | bun:test (built-in) |
| **Config file** | none — uses bun test defaults |
| **Quick run command** | `bun test` |
| **Full suite command** | `bun test` |
| **Estimated runtime** | ~2 seconds (104 tests currently) |

---

## Sampling Rate

- **After every task commit:** Run `bun test`
- **After every plan wave:** Run `bun test`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 3 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | CHAT-01, CHAT-03 | unit + integration | `bun test tests/server/chat.test.ts` | ❌ W0 | ⬜ pending |
| 03-01-02 | 01 | 1 | CHAT-02 | unit | `bun test tests/server/auto-brief.test.ts` | ❌ W0 | ⬜ pending |
| 03-01-03 | 01 | 1 | CHAT-06, CHAT-07 | unit | `bun test tests/server/chat-session.test.ts` | ❌ W0 | ⬜ pending |
| 03-02-01 | 02 | 2 | CONF-01, CONF-02, CONF-03 | unit | `bun test tests/server/config-editor.test.ts` | ❌ W0 | ⬜ pending |
| 03-02-02 | 02 | 2 | CONF-04 | unit + integration | `bun test tests/server/config-validator.test.ts` | ❌ W0 | ⬜ pending |
| 03-02-03 | 02 | 2 | CONF-06, CONF-07, CONF-08 | unit | `bun test tests/server/target-wizard.test.ts` | ❌ W0 | ⬜ pending |
| 03-03-01 | 03 | 2 | FEED-01, FEED-02 | unit | `bun test tests/server/feedback.test.ts` | ❌ W0 | ⬜ pending |
| 03-03-02 | 03 | 2 | FEED-04, FEED-05 | unit | `bun test tests/server/feedback-polling.test.ts` | ❌ W0 | ⬜ pending |
| 03-03-03 | 03 | 2 | FEED-06, FEED-07 | unit | `bun test tests/server/calibration.test.ts` | ❌ W0 | ⬜ pending |
| 03-04-01 | 04 | 3 | ASSESS-01, ASSESS-02 | unit | `bun test tests/worker/assessment.test.ts` | ❌ W0 | ⬜ pending |
| 03-04-02 | 04 | 3 | MEAS-01, MEAS-02 | unit | `bun test tests/worker/baseline.test.ts` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/server/chat.test.ts` — stubs for CHAT-01, CHAT-03
- [ ] `tests/server/auto-brief.test.ts` — stubs for CHAT-02
- [ ] `tests/server/chat-session.test.ts` — stubs for CHAT-06, CHAT-07
- [ ] `tests/server/config-editor.test.ts` — stubs for CONF-01, CONF-02, CONF-03
- [ ] `tests/server/config-validator.test.ts` — stubs for CONF-04
- [ ] `tests/server/target-wizard.test.ts` — stubs for CONF-06, CONF-07, CONF-08
- [ ] `tests/server/feedback.test.ts` — stubs for FEED-01, FEED-02
- [ ] `tests/server/feedback-polling.test.ts` — stubs for FEED-04, FEED-05
- [ ] `tests/server/calibration.test.ts` — stubs for FEED-06, FEED-07
- [ ] `tests/worker/assessment.test.ts` — stubs for ASSESS-01, ASSESS-02
- [ ] `tests/worker/baseline.test.ts` — stubs for MEAS-01, MEAS-02

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Chat drawer slide-over UX | CHAT-01 | Visual rendering + animation | Open dashboard, click Chat — drawer slides in from right |
| Auto-brief popup after run | CHAT-02 | Requires real run completion + visual confirmation | Trigger run, wait for completion — drawer auto-opens with summary |
| Config YAML editor UX | CONF-01 | Visual rendering of textarea + syntax | Open Config tab — YAML displays in editable textarea |
| 4-step validation visual flow | CONF-04 | Step-by-step visual progression | Edit YAML, save — observe syntax→semantic→diff→confirm flow |
| Add Target wizard modal | CONF-06 | Multi-step modal interaction | Click Add Target — 4-step wizard in modal |
| Feedback button visual state | FEED-01 | Icon highlight on click | View action card, click thumbs up — icon fills/highlights |
| Baseline summary card layout | MEAS-03 | Visual rendering of trend arrows | Open completed run — baseline card at top with ↑/↓/→ indicators |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 3s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
