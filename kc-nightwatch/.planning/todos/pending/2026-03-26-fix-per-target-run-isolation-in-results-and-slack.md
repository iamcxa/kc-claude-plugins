---
created: 2026-03-26T08:36:35.582Z
title: Fix per-target run isolation in results and Slack
area: worker
files:
  - app/server/services/run-store.ts
  - app/server/routes/health-api.ts
  - app/server/worker/executor.ts
---

## Problem

When running a single target (e.g., just `kc-pr-flow`), the run results output and Slack notification include data for ALL targets instead of only the target that was run. This defeats the purpose of per-target scheduling — different targets on different schedules should produce isolated results.

Two areas affected:
1. **Run results output** — the summary/output at run completion shows all targets' data
2. **Slack notification** — the nightwatch Slack report includes all targets regardless of which target the run was for

## Solution

Trace the run execution pipeline from trigger → executor → result aggregation → Slack notification. The target filter (`run.target`) must be propagated through every stage:

1. Check how `run.target` (which can be a specific target name or `'__all__'`) is used in the executor and result summarizer
2. Ensure result aggregation only includes data for the specific `run.target`, not all targets
3. Ensure Slack notification template filters to the run's target
4. `'__all__'` should continue to include all targets (existing behavior for scheduled full runs)
