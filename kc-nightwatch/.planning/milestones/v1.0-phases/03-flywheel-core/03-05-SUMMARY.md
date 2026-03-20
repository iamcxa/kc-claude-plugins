---
phase: 03-flywheel-core
plan: "05"
subsystem: feedback-flywheel
tags: [feedback, executor, wiring, requirements, gap-closure]
dependency_graph:
  requires:
    - "03-03 (feedback-store.ts + feedback-collector.ts implemented)"
    - "03-04 (executor.ts summary.yaml parsing in place)"
  provides:
    - "Complete feedback flywheel loop: run -> PR poll -> append -> trends -> journal"
    - "Accurate REQUIREMENTS.md Phase 3 completion status"
  affects:
    - "app/worker/executor.ts (new imports + post-run feedback block)"
    - ".planning/REQUIREMENTS.md (FEED-01/02/04/06/07 marked complete)"
tech_stack:
  added: []
  patterns:
    - "Fire-and-forget post-processing: wrapped in try/catch, errors logged not propagated"
    - "Static wiring verification: TDD via Bun.file source read + regex, avoids full executor mock"
    - "Guard pattern: !timedOut && Object.keys(summary.per_target).length > 0"
key_files:
  created:
    - "app/tests/worker/executor-feedback-wiring.test.ts"
  modified:
    - "app/worker/executor.ts"
    - ".planning/REQUIREMENTS.md"
decisions:
  - "Static source-read TDD: test reads executor.ts as text + regex-matches import/call patterns. Avoids mocking safehouse/claude spawn while still verifying production wiring."
  - "Per-target feedback trends: writeFeedbackTrends called per-target using ensureNwMemoryDir (reuses existing helper, consistent journal path)"
  - "actionsWithTargets collector: flatten per_target.actions with target name + run_id before passing to collectImplicitFeedback (matches function signature)"
metrics:
  duration: "135 seconds"
  completed_date: "2026-03-18"
  tasks_completed: 2
  files_changed: 3
---

# Phase 3 Plan 5: Gap Closure — Feedback Flywheel Wiring Summary

**One-liner:** Wired collectImplicitFeedback + writeFeedbackTrends into executor.ts post-run finally block, closing the feedback flywheel loop that was implemented but never called.

## What Was Done

### Task 1: Wire feedback collector and trend writer into executor.ts (TDD)

The feedback flywheel functions (`collectImplicitFeedback`, `writeFeedbackTrends`) were defined and tested in Phase 03-03 but were never called from production code. This plan wired them in.

**Changes to `app/worker/executor.ts`:**

1. Added two imports at the top:
   - `import { collectImplicitFeedback } from './feedback-collector.ts'`
   - `import { appendFeedback, writeFeedbackTrends } from '../server/services/feedback-store.ts'`

2. Added feedback collection block in the `finally` block of `executeRun()`, placed AFTER summary.yaml is read (so `summary.per_target` is populated) and BEFORE the IPC `run:completed`/`run:failed` message is dispatched:

   - Guard: `!timedOut && Object.keys(summary.per_target).length > 0`
   - Flattens all `actions` with `pr_url` across all targets into `actionsWithTargets[]`
   - Calls `collectImplicitFeedback(actionsWithTargets, appendFeedback)` only when there are PR-linked actions
   - Calls `writeFeedbackTrends(targetName, journalDir)` for each target using `ensureNwMemoryDir`
   - Outer `try/catch` ensures feedback errors are logged but never block run completion

**New test file `app/tests/worker/executor-feedback-wiring.test.ts`:**

9 static wiring verification tests using `Bun.file(EXECUTOR_PATH).text()` + regex:
- Import regex checks for all 3 functions
- Call count checks (must appear >=2 per function: import + call)
- Guard check: `!timedOut` precedes `collectImplicitFeedback` call
- try/catch wrapper check: `Post-run feedback collection error` string present
- Module resolution checks (imports resolve correctly)

### Task 2: Update REQUIREMENTS.md Phase 3 FEED-* completion status

Updated `.planning/REQUIREMENTS.md`:

**Checkbox section (Feedback):**
- FEED-01, FEED-02, FEED-04, FEED-06, FEED-07: `[ ]` → `[x]`
- FEED-03, FEED-05: remain `[ ]` (deferred to Phase 4: MCP tool + Linear)

**Traceability table:**
- FEED-01/02/04/06/07: Pending → Complete
- FEED-03/05: remain Pending

**Additional corrections:**
- FOUND-01: `[ ]` → `[x]` (Phase 1 completed this, checkbox was never updated)
- DASH-02: Pending → Complete (per-target context menu exists)
- DASH-05: Pending → Complete (Dashboard/Runs/Config navigation works)
- HIST-04: Pending → Complete (live view during execution exists)

## Test Results

- 163 tests pass (0 fail) across 29 files
- 0 regressions from existing 154+ tests
- 9 new wiring verification tests added

## Deviations from Plan

None - plan executed exactly as written. The static wiring test approach (Bun.file source read + regex) was the approach specified in the plan.

## Self-Check: PASSED

- FOUND: `app/tests/worker/executor-feedback-wiring.test.ts`
- FOUND: `.planning/phases/03-flywheel-core/03-05-SUMMARY.md`
- FOUND commit `8df0af2`: test(03-05) RED tests
- FOUND commit `e18db36`: feat(03-05) GREEN implementation
- FOUND commit `825f51e`: docs(03-05) REQUIREMENTS.md updates
- 163 tests pass, 0 fail
