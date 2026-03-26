---
phase: 16
slug: health-page-enrichment
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-26
---

# Phase 16 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Bun test 1.3.9 |
| **Config file** | `app/bunfig.toml` (or none — `bun test` auto-discovers) |
| **Quick run command** | `cd app && bun test tests/server/health-api.test.ts` |
| **Full suite command** | `cd app && bun test` |
| **Estimated runtime** | ~3 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd app && bun test tests/server/health-api.test.ts`
- **After every plan wave:** Run `cd app && bun test`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 16-01-01 | 01 | 1 | VIZ-03 | unit | `bun test tests/server/health-api.test.ts` | ✅ (extend) | ⬜ pending |
| 16-01-02 | 01 | 1 | VIZ-03 | unit | `bun test tests/server/health-api.test.ts` | ✅ (extend) | ⬜ pending |
| 16-02-01 | 02 | 1 | VIZ-02 | unit | `bun test tests/frontend/calibration-table.test.ts` | ❌ W0 | ⬜ pending |
| 16-02-02 | 02 | 1 | VIZ-03 | unit | `bun test tests/frontend/sparkline.test.ts` | ❌ W0 | ⬜ pending |
| 16-02-03 | 02 | 1 | FORGE-01 | unit | `bun test tests/frontend/forge-result-card.test.ts` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `app/tests/frontend/sparkline.test.ts` — covers VIZ-03 tooltip logic (activeIdx computation, runId display guard)
- [ ] `app/tests/frontend/forge-result-card.test.ts` — covers FORGE-01 pure helpers (relativeTime, statusColor, null guard)
- [ ] `app/tests/frontend/calibration-table.test.ts` — covers VIZ-02 threshold cell logic (N-gate display, sort order, empty state)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Tooltip position on sparkline hover | VIZ-03 | Visual positioning in browser | Hover each sparkline data point, verify tooltip appears near mouse, doesn't clip at edges |
| ForgeResultCard expand/collapse | FORGE-01 | Interactive UI behavior | Click forge card, verify expand shows branch + details, collapse hides them |
| Calibration table visual layout | VIZ-02 | Visual alignment and styling | Verify table columns align, "(N/10)" text displays correctly for low-count indicators |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
