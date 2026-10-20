---
title: observer_check.py refuses an observer report that predates later task changes
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Declined under the round-3 rule from the third external review round (Codex) of iamcxa/kc-claude-plugins PR #632 (head 40c714a6, review:5501097974), 2026-10-13, task `observer-before-merge-guard`. The finding is not P1 or Material, so it did not start a repair cycle there; it is filed here with its decline reason, per `## FO steps: review findings` step 5.

## Scope

- Finding 1 (Codex P2, `scripts/observer_check.py` around line 65): after a task passes the check and `merge guard --rework` routes it back, later implementation and validation commits leave the old `observer.md` in place; the check accepts it, so the next delivery can archive with a report that omits the rework cycle. Candidate fix: require the report to be newer than the task's later state changes, or invalidate it when rework begins. Decline reason: `merge guard --rework` after an observer run has not happened in this workflow; the stale report is still committed and visible to the Captain beside learn's notice, so the miss is an incomplete read, not a skipped one.
- Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Alignment: not needed before ideation; the finding and decline reason above are the scope.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none

## Closed

Closed by the Captain 2026-10-20 (「照建議關掉 19 張。」) on FO's follow-up triage against origin/main ad44f0cb: stale-report-after-rework trigger never observed in 27 observer reports.
