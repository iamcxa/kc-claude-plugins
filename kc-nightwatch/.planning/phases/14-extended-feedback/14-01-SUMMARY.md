---
phase: 14-extended-feedback
plan: 01
subsystem: feedback
tags: [types, store, api, mcp, extended-feedback]
dependency_graph:
  requires: []
  provides: [3-state-verdict, 5-source-routing, uncertain-verdict-api, uncertain-verdict-mcp]
  affects: [feedback-store, feedback-api, mcp-tools, calibration]
tech_stack:
  added: []
  patterns: [3-state-verdict-union, 5-category-store-routing, includes-validation]
key_files:
  created: []
  modified:
    - app/shared/types.ts
    - app/server/services/feedback-store.ts
    - app/server/routes/feedback.ts
    - app/server/services/mcp-tools.ts
    - app/tests/server/feedback.test.ts
decisions:
  - "D-04: 'uncertain' verdict counts toward total_feedback but NOT reject_count in calibration — existing 'rejected'-only logic satisfies this automatically"
  - "Routing fallback: unknown sources fall back to 'linear_feedback' for backward compatibility"
  - "Validation: switched from equality chain to includes() array check for extensibility"
metrics:
  duration: 8min
  completed: "2026-03-24"
  tasks: 2
  files: 5
requirements_covered: [EXTFEED-01, EXTFEED-02]
---

# Phase 14 Plan 01: Extended Feedback Types, Store Routing, and API Validation Summary

## One-liner

3-state verdict ('accepted' | 'rejected' | 'uncertain') and two new feedback sources ('slack_reaction', 'pr_review') wired throughout types, store routing, API validation, MCP tool, and calibration.

## What Was Built

Foundation layer for extended feedback collection (EXTFEED-01 Slack reactions + EXTFEED-02 PR reviews). Every consumer of FeedbackEntry now handles the new verdict and source values:

1. **FeedbackEntry types** — `verdict` extended to 3-state union; `source` extended to 5-value union
2. **FeedbackStore routing** — `appendFeedback` routes `slack_reaction` → `slack_feedback`, `pr_review` → `pr_review_feedback`
3. **Aggregation functions** — `getFeedbackForRun`, `getFeedbackForSignal`, `getCalibrationData` all spread all 5 categories
4. **Calibration correctness** — `uncertain` entries count toward `total_feedback` but not `reject_count` (D-04); this is already correct because the existing code only increments `rejected` when `entry.verdict === 'rejected'`
5. **POST /api/feedback** — verdict validation updated from equality check to `includes()`, error message updated, type annotation updated
6. **MCP nw_submit_feedback** — `z.enum` extended to 3 values, description updated

## Tasks Completed

| Task | Description | Commit | Files |
|------|-------------|--------|-------|
| 1 | Extend FeedbackEntry types + FeedbackStore routing/aggregation (TDD) | 1c14724 | types.ts, feedback-store.ts, feedback.test.ts |
| 2 | Update API route and MCP tool verdict validation | 1d0c362 | feedback.ts, mcp-tools.ts |

## Test Results

- **Before:** 322 tests (baseline)
- **After:** 329 tests, 0 failures
- **New tests:** 7 tests covering 3-state verdict, 5-source routing, D-04 calibration behavior

## Acceptance Criteria Verification

- `grep -c "uncertain" app/shared/types.ts` → 2 (verdict union + source context comment)
- `grep -c "slack_feedback" app/server/services/feedback-store.ts` → 5 (interface + appendFeedback + 3 aggregation functions)
- `grep -c "pr_review_feedback" app/server/services/feedback-store.ts` → 5
- `grep "uncertain" app/server/routes/feedback.ts` → shows updated validation and type annotation
- `grep "uncertain" app/server/services/mcp-tools.ts` → shows updated z.enum
- Full test suite: 329 pass, 0 fail

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None — all changes are fully wired. The new store categories (`slack_feedback`, `pr_review_feedback`) will receive entries once the collection functions (14-02 PR reviews, 14-03 Slack reactions) are built.

## Self-Check: PASSED

- [x] `app/shared/types.ts` exists and contains 'uncertain', 'slack_reaction', 'pr_review'
- [x] `app/server/services/feedback-store.ts` exists and contains 5 occurrences of 'slack_feedback'
- [x] `app/server/routes/feedback.ts` exists and contains 'uncertain'
- [x] `app/server/services/mcp-tools.ts` exists and contains 'uncertain'
- [x] Commit 1c14724 exists (Task 1)
- [x] Commit 1d0c362 exists (Task 2)
- [x] 329 tests pass, 0 failures
