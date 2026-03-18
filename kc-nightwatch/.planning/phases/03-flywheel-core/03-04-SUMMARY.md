---
phase: 03-flywheel-core
plan: 04
subsystem: ui
tags: [preact, htm, yaml, bun, assessment, baseline, indicator]

requires:
  - phase: 03-03
    provides: ActionCard component, FeedbackEntry store, PR collector, calibration formula

provides:
  - "Phase 0.5 (Indicator Baseline Measurement) in orchestrator skill"
  - "Phase 3.5 (Pre-Action Strategy Assessment) in orchestrator skill"
  - "Phase 4.5 (Post-Action Reflection) in orchestrator skill"
  - "Step 5.2.5 (Write summary.yaml) with full per-target structured output spec"
  - "Assessment section in Slack morning report"
  - "executor.ts reads summary.yaml to populate RunSummary.per_target"
  - "BaselineCard component with trend arrows (up/down/flat)"
  - "ActionCard Reflection section (assessment verdict)"
  - "Run detail: indicator baselines above action cards, Pre-Run Strategy + Post-Run Reflection text"

affects:
  - 04-mcp-linear

tech-stack:
  added: []
  patterns:
    - "summary.yaml as skill-to-executor structured handoff: skill writes Phase 5.2.5, executor reads in finally block"
    - "Only write legacy phases_completed if skill did not produce summary.yaml (non-destructive fallback)"
    - "BaselineCard always-visible (not collapsible) above action cards per CONTEXT.md design decision"

key-files:
  created:
    - app/frontend/components/baseline-card.ts
    - app/tests/worker/executor-summary.test.ts
    - app/tests/worker/assessment.test.ts
    - app/tests/worker/baseline.test.ts
  modified:
    - skills/kc-nightwatch/SKILL.md
    - app/worker/executor.ts
    - app/frontend/components/action-card.ts
    - app/frontend/pages/runs.ts

key-decisions:
  - "summary.yaml is the handoff contract between NW-Claude skill (writer) and dashboard executor (reader) — executor reads after run completes in finally block"
  - "Non-destructive fallback: executor only writes legacy phases_completed YAML if skill did not produce summary.yaml"
  - "BaselineCard always visible (not collapsible) per CONTEXT.md Indicator Baseline Display decision"
  - "Reflection section in ActionCard shows assessment verdict prose, not raw fields — matches CONTEXT.md assessment display decision"

patterns-established:
  - "Skill-to-dashboard handoff via summary.yaml: NW-Claude skill writes structured YAML in Phase 5.2.5; executor.ts reads it in finally block after log processing completes"
  - "Trend arrow semantics: improving=var(--success) up-arrow, degrading=var(--error) down-arrow, stable=var(--muted) right-arrow; aria-label for accessibility"

requirements-completed:
  - ASSESS-01
  - ASSESS-02
  - ASSESS-03
  - ASSESS-04
  - MEAS-01
  - MEAS-02
  - MEAS-03

duration: 15min
completed: 2026-03-18
---

# Phase 3 Plan 04: Self-Assessment + Measurement Summary

**NW skill gains Phase 0.5/3.5/4.5 assessment data production; executor reads summary.yaml to populate RunSummary.per_target; BaselineCard with trend arrows and ActionCard Reflection section complete the display layer**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-03-18T10:51Z
- **Completed:** 2026-03-18T11:06Z
- **Tasks:** 2 auto tasks + 1 checkpoint (auto-approved, auto_advance=true)
- **Files modified:** 7 files, 3 test files created

## Accomplishments

- Orchestrator skill now instructs NW-Claude to measure indicator baselines (Phase 0.5), write pre-action strategy (Phase 3.5), write post-action reflection (Phase 4.5), and include assessment in Slack report
- executor.ts reads summary.yaml after run completes and populates RunSummary.per_target — closing the data flow from skill to dashboard
- BaselineCard component renders indicator baselines with trend arrows (improving=green up, degrading=red down, stable=gray right) with aria-label accessibility
- ActionCard now has explicit "Reflection" section showing assessment verdict as readable prose
- runs.ts integrates BaselineCard above action cards, and Pre-Run Strategy + Post-Run Reflection at target level
- 14 new tests (5 executor-summary + 4 baseline + 5 assessment), full suite: 154 tests passing

## Task Commits

Each task was committed atomically:

1. **Task 1: Orchestrator skill phases 0.5/3.5/4.5 + executor summary.yaml parsing** - `72cf285` (feat)
2. **Task 2: BaselineCard + ActionCard reflection + runs.ts assessment integration** - `be25ef7` (feat)

## Files Created/Modified

- `skills/kc-nightwatch/SKILL.md` - Added Phase 0.5, 3.5, 4.5, Step 5.2.5, assessment in Slack report
- `app/worker/executor.ts` - Reads summary.yaml post-run to populate RunSummary.per_target; non-destructive legacy fallback
- `app/frontend/components/baseline-card.ts` - New: BaselineCard with trend arrows, always visible, aria-label
- `app/frontend/components/action-card.ts` - Added Reflection section (assessment verdict prose) after Strategy
- `app/frontend/pages/runs.ts` - Added BaselineCard, Pre-Run Strategy, Post-Run Reflection sections above action cards
- `app/tests/worker/executor-summary.test.ts` - New: 5 tests for summary.yaml YAML parsing
- `app/tests/worker/assessment.test.ts` - New: 5 tests for assessment field contracts
- `app/tests/worker/baseline.test.ts` - New: 4 tests for IndicatorBaseline type and trend arrow mapping

## Decisions Made

- summary.yaml as the skill-to-executor handoff contract: NW-Claude skill writes it in Phase 5.2.5, executor reads it in the `finally` block after log processing. Simple file-based handoff, no IPC change needed.
- Non-destructive fallback: executor only writes legacy `phases_completed` YAML if skill did not produce summary.yaml, so existing runs without the new skill phases still work.
- BaselineCard is always visible (not collapsible) — matches CONTEXT.md decision that baselines provide context for all action cards below.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 3 Flywheel Core is now complete (all 4 plans: Chat, Config Editor, Feedback, Self-Assessment)
- Phase 4 (MCP + Linear integration) can begin — feedback data and assessment data are in place for MCP tool exposure
- Human verification step (Task 3) was auto-approved per auto_advance=true config

---
*Phase: 03-flywheel-core*
*Completed: 2026-03-18*
