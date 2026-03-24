---
phase: 14
slug: extended-feedback
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-24
---

# Phase 14 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | bun:test (built-in) |
| **Config file** | app/bunfig.toml (if exists) or package.json |
| **Quick run command** | `cd app && bun test --filter feedback` |
| **Full suite command** | `cd app && bun test` |
| **Estimated runtime** | ~8 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd app && bun test --filter feedback`
- **After every plan wave:** Run `cd app && bun test`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| TBD | TBD | TBD | EXTFEED-01 | unit | `bun test --filter feedback` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | EXTFEED-02 | unit | `bun test --filter feedback` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Extend existing `app/tests/worker/feedback-collector.test.ts` or `app/tests/server/feedback.test.ts` with stubs for EXTFEED-01, EXTFEED-02
- [ ] Test helper: mock `gh pr view --json reviews` output for PR review tests

*Existing test infrastructure (bun:test, spyOn) covers framework needs.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Slack reaction reading via MCP | EXTFEED-01 | Requires live Slack MCP session | Post to Slack, add reactions, run nightwatch, verify feedback.yaml |
| Dashboard shows new feedback sources | EXTFEED-01, EXTFEED-02 | Visual verification | Open dashboard feedback view, confirm slack_feedback and pr_review_feedback entries appear |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
