---
phase: 17
slug: signal-priority-display
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-26
---

# Phase 17 — Validation Strategy

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Bun test 1.3.9 |
| **Quick run command** | `cd app && bun test tests/frontend/action-card.test.ts` |
| **Full suite command** | `cd app && bun test` |
| **Estimated runtime** | ~3 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd app && bun test tests/frontend/action-card.test.ts`
- **After every plan wave:** Run `cd app && bun test`
- **Before `/gsd:verify-work`:** Full suite must be green

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 17-01-01 | 01 | 1 | SIG-01 | unit | `bun test tests/frontend/action-card.test.ts` | ✅ (extend) | ⬜ pending |
| 17-01-02 | 01 | 1 | SIG-01 | unit | `bun test tests/frontend/action-card.test.ts` | ✅ (extend) | ⬜ pending |

---

## Wave 0 Requirements

None — `action-card.test.ts` already exists with tests for confidenceColor.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Actions sorted by score in run detail | SIG-01 | Visual order in browser | Open run detail, verify action cards appear in descending score order |
| Score displays alongside confidence | SIG-01 | Visual layout | Verify each action card shows "0.XX confidence" format |

---

## Validation Sign-Off

- [ ] All tasks have automated verify
- [ ] No 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
