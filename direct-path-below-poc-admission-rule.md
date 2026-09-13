---
title: "A direct path below poc-exploration: the FO edits a small, test-neutral change itself, admitted by a check on the work, not on the FO's estimate"
status: backlog
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: ship-cloud-wrapper-r3
sprint-readiness: defer
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: f6srtd3vkbsn4txjmecw653c
---

Captain (relayed by the subspace-relay session quebec-v1-47, 2026-09-13): "poc profile 應該不只是做
poc，等於是一條最短路徑把不需要多做事的事情做完，或是應該多一條是 direct path 讓 FO 可以直接改很小的內容."
Measured case: a terminal reader's pre-publish consent screen ran 23 rows at 80 columns, the
Captain wanted 15. The FO chose `pilot-product-slice`, walked backlog gate → ideation dispatch →
ideation gate, produced a where-it-touches table, a reverse-recovery audit, stop numbers and a
pre-mortem; the Captain called it overkill, granted a direct edit, and the change (four sentences
reworded, one paragraph deleted, one path moved into a doc) landed in one pass at exactly 15 rows
with the suite green. Even the cheapest rung today, `poc-exploration`, dispatches a worker,
walks a validation gate and terminalizes through the merge ceremony.

The hazard: a direct path is one grant away from a hole in the flow — what makes it cheap (no
worker, no gate) is what makes it abusable. Admission must be checkable from the work, never from
the FO's size estimate. Candidate admission checks (none verified): a declared surface (docs and
user-facing strings only, never a code path a test exercises); a hard upper bound on changed lines
that refuses rather than warns; the existing suite must pass unchanged, so anything needing a new
test is by definition not on this path. Known cost of the case: the 15 rows have no guard and
grew back once before (subspace-v0#37 cut 26→23 with a guard test, PR closed unmerged, screen back
at 23) — an argument for a tight bound, not for no path.

## Accepted outcome

A POC that decides the admission check before any route exists: take the last twenty merged
changes across this repository, subspace-v0 and subspace-relay, classify each by the three
candidate checks, and report how many the direct path would have admitted, how many of those
later needed a guard test, and whether any admitted change touched a tested code path. From that
evidence, recommend one admission rule (or none) to the Captain with its false-admit count.

## Non-goals

* Building the route before the admission rule is chosen.
* Any Linear read or write.

## Acceptance criteria

* **AC-1** A table of ≥20 real merged changes with the three checks applied per change, produced by a script that reads only git history and test-file diffs (no judgement calls).
* **AC-2** For each candidate rule: admitted count, later-guarded count, tested-path-touched count, with the commits named.
* **AC-3** A one-page recommendation naming the rule, its refusal message, and what it would have refused in the consent-screen case.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: poc-exploration
  recommended: poc-exploration
  route: [build, prove]
  basis: The Captain wants a shortest path; the risk is a hole in the flow; the falsifier is a measured admission rule that admits nothing needing a guard test.
  obligations:
    architecture: [Admission checkable from the work; no FO estimate]
    implementation: [History classifier script; evidence table; recommendation]
    testing: [AC-1..AC-3 on real history]
  scope_boundary: No new route yet; no Linear.
  semantics_unchanged: false
  poc_decision: whether kc-dev-flow gets a direct path and which admission rule guards it
  poc_falsifier: every candidate rule admits at least one change that later needed a guard test or touched a tested path
  poc_budget: one worker, one PR (evidence only)
  poc_stop_when: AC-1..AC-3 delivered
  poc_artifact: disposable
  poc_safety_boundary: read-only over git history; no route or contract change
  poc_decision_ready_minutes: 15
```
