---
phase: 14-extended-feedback
plan: 02
subsystem: feedback
tags: [pr-review, feedback-collector, executor, extended-feedback, tdd]
dependency_graph:
  requires: [14-01]
  provides: [pr-review-collection, review-verdict-parsing, executor-review-wiring]
  affects: [feedback-collector, executor, calibration]
tech_stack:
  added: []
  patterns: [pure-function-extract-for-tdd, fire-and-forget-collection, per-reviewer-dedup, cross-reviewer-aggregation]
key_files:
  created:
    - app/tests/worker/feedback-collector.test.ts
  modified:
    - app/worker/feedback-collector.ts
    - app/worker/executor.ts
    - app/tests/worker/executor-feedback-wiring.test.ts
decisions:
  - "D-17: Latest review per reviewer wins — ISO timestamp string comparison (lexicographic = chronological)"
  - "D-03: CHANGES_REQUESTED from any reviewer overrides all others (strongest signal = rejected)"
  - "Extract parseReviewVerdict as exported pure function for deterministic testing without Bun.spawn mocking"
  - "collectPrReviewFeedback placed inside same try/catch as collectImplicitFeedback — shared fire-and-forget error boundary"
metrics:
  duration: 12min
  completed: "2026-03-24"
  tasks: 2
  files: 4
requirements_covered: [EXTFEED-02]
---

# Phase 14 Plan 02: PR Review Feedback Collection Summary

## One-liner

GitHub PR review verdicts (APPROVED/CHANGES_REQUESTED/COMMENTED/DISMISSED) collected via gh CLI and written as 'pr_review' feedback entries using per-reviewer dedup and cross-reviewer aggregation.

## What Was Built

PR review feedback collection closing the loop between nightwatch proposals and human reviewer actions:

1. **parseReviewVerdict** — exported pure function; D-17 latest-per-reviewer dedup via ISO timestamp comparison; D-03 CHANGES_REQUESTED wins cross-reviewer aggregation; DISMISSED is skipped; returns 3-state verdict or null
2. **checkPrReviews** — async function calling `gh pr view --json reviews`; URL-guards non-GitHub URLs; calls parseReviewVerdict on parsed response
3. **collectPrReviewFeedback** — orchestrator function mirroring collectImplicitFeedback signature; creates FeedbackEntry with source='pr_review'; fire-and-forget (never throws)
4. **executor.ts wiring** — collectPrReviewFeedback added to import and called after collectImplicitFeedback inside the existing try/catch; EXTFEED-02 comment traces requirement
5. **20 new unit tests** — feedback-collector.test.ts (new file): 9 parseReviewVerdict tests, 3 checkPrReviews URL tests, 4 collectPrReviewFeedback contract tests
6. **6 new wiring tests** — executor-feedback-wiring.test.ts: import check, call site check, try/catch boundary check, EXTFEED-02 trace check, module resolution

## Tasks Completed

| Task | Description | Commit | Files |
|------|-------------|--------|-------|
| 1 | Implement parseReviewVerdict, checkPrReviews, collectPrReviewFeedback with TDD | 82c84d7 | feedback-collector.ts, feedback-collector.test.ts (new) |
| 2 | Wire collectPrReviewFeedback into executor finally block + wiring tests | 98d9a8e | executor.ts, executor-feedback-wiring.test.ts |

## Test Results

- **Before:** 329 tests (baseline after Plan 01)
- **After:** 355 tests, 0 failures
- **New tests:** 26 tests (20 unit + 6 wiring)

## Acceptance Criteria Verification

- `grep -c "parseReviewVerdict" app/worker/feedback-collector.ts` → 3 (export + 2 usages)
- `grep -c "checkPrReviews" app/worker/feedback-collector.ts` → 2 (export + 1 usage)
- `grep -c "collectPrReviewFeedback" app/worker/feedback-collector.ts` → 1 (export)
- `grep -c "source: 'pr_review'" app/worker/feedback-collector.ts` → 1
- `grep -c "CHANGES_REQUESTED" app/worker/feedback-collector.ts` → 3
- `grep -c "parseReviewVerdict" app/tests/worker/feedback-collector.test.ts` → 14 (well above required 5+)
- `grep -q "collectPrReviewFeedback" app/worker/executor.ts` → PASS
- `grep -q "import.*collectPrReviewFeedback" app/worker/executor.ts` → PASS
- `grep -q "EXTFEED-02" app/worker/executor.ts` → PASS
- `grep -c "CHANGES_REQUESTED" app/tests/worker/feedback-collector.test.ts` → 9 (above required 2+)
- Full test suite: 355 pass, 0 fail

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None — all functions are fully implemented. The pr_review_feedback store category (from Plan 01) will receive entries on every executor run that has PR URLs with reviewer activity.

## Self-Check: PASSED

- [x] `app/worker/feedback-collector.ts` contains parseReviewVerdict, checkPrReviews, collectPrReviewFeedback
- [x] `app/tests/worker/feedback-collector.test.ts` created with 20 tests
- [x] `app/worker/executor.ts` imports and calls collectPrReviewFeedback with EXTFEED-02 comment
- [x] `app/tests/worker/executor-feedback-wiring.test.ts` updated with 6 new tests
- [x] Commit 82c84d7 exists (Task 1)
- [x] Commit 98d9a8e exists (Task 2)
- [x] 355 tests pass, 0 failures
