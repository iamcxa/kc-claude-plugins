# 10. A round-three declined finding becomes its own backlog task

Date: 2026-10-11

## Status

Accepted

## Context

ADR 0004 sent a finding declined from the third external-review round into a task's
Scope as a `Follow-up:` line. In an adopting project on 2026-10-07 a receiving task built
such a line and broke an accepted no-duplicate-booking contract; validation caught it and
a repair cycle reverted it (issue #563). Replays of that case on 2026-10-11 found the
receiving worker's own judgment did not reliably stop it: the previous package built it
in 0 of 1 runs, the first batch-2 wording in 2 of 2, and a tightened wording in 1 of 2.

## Decision

**Words:** 「E」 — Captain, 2026-10-11, choosing option E of six put to him after the replays

**Options considered:**
- E: file every round-three declined finding as its own backlog task, never into an open task's Scope (chosen)
- A: add no rule and rely on validation to catch a wrong build
- B: keep the tightened wording that left the decision to the receiving worker
- C: have FO name the rulings, criteria and journey goals a moved line touches
- D: treat a moved line as not scope until FO marks it `Adopted:`
- F: close round-three declines without carrying them anywhere

**Recommended:** E — the FO's recommendation in that question

From the third round, a finding that is neither Material nor a reviewer P1 starts no
repair cycle: FO declines it in the committed gate summary and files it with
`spacedock new` as a new backlog task whose body carries the finding and the decline
reason. It never enters an open task's Scope. The terminal gate lists each such task.

## Consequences

A behaviour change carried by a declined finding reaches the Captain at the new task's
gates instead of entering another task's build unseen. The cost is one small backlog
task per such finding. A `Follow-up:` line still in a Scope is not accepted scope by
itself. First applied 2026-10-11 on PRs #593 and #594 (tasks
`codex-review-round3-followups` and `pr-watch-round3-followups`). Reopen if these tasks
pile up unscheduled.
