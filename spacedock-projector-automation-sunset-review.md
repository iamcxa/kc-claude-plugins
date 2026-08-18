---
id: pmh2t9zpz4ayz9qqm2550x8s
title: Replace scheduled Spacedock projection with an attended manual trigger
status: backlog
source: Captain decision after 73 consecutive scheduled reconcile failures, 2026-08-18
product: kc-dev-flow
sprint:
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
design: required
lane:
---

Scheduled reconciliation is disabled at the GitHub host. Replace the installed
timer with a manual-only workflow before re-enabling it. Evaluate an attended
prompt after a successful state commit as a later convenience, but do not add a
timer, automatic state-push trigger, repository dispatch, or daemon until a
named missed-freshness incident proves plain manual dispatch insufficient.

## Acceptance criteria

### AC-1 — Manual reconciliation remains deliberate and convergent

Remove every `schedule` trigger while retaining `workflow_dispatch` and the
single deterministic reconcile path. Before the host workflow is re-enabled,
repair the live Project schema through attended setup; then one manual dispatch
must reconcile the exact state revision and an identical second dispatch must
report zero mutations.

Verified by: workflow routing evidence, live schema readback, one successful
manual reconcile receipt, and one identical zero-mutation receipt. Falsified
by: any scheduled run remaining reachable, manual dispatch bypassing the same
fail-closed checks, or re-enabling the workflow before schema readiness.

## Authority

Kent authorized the host-level disable and the manual-only target on 2026-08-18.
This task grants no sprint admission, code-worktree ownership, Project schema
mutation, workflow re-enable, or new trigger authority. Coordinate with the
active `spacedock-project-status-updates` holder because it currently owns
overlapping workflow and installer files.
