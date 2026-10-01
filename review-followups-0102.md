---
title: Review follow-ups from the 0.10.2 adopter sync
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Follow-ups declined from a repair cycle under the review-round rule (round 3 of the external review of qnow PR #1248, commit 39bf550, 2026-10-01); each waits for the Captain to schedule it.

## Scope

Captain 2026-10-01: 「修完再合併」 — the round-3 P1 is fixed in `patch-0103`; the round-3 P2s are recorded here as follow-ups, not repaired in that cycle.
Follow-up: `references/sd/workflow.md` FO recovery step writes `status --workflow-dir <dir> --read <task> --stage <stage> --checklist` without the `spacedock` executable; write `spacedock status ...` (reviewer P2).
Follow-up: `## Number guards` applies when "its design lands an ADR"; an ADR first required by a ruling in an implementation report, a validation report or mid-stage feedback gets no reserved number; apply the guard whenever the task lands an ADR, and reserve when the need appears (reviewer P2).
Declined, not a follow-up: the round-3 comment asking to clear release fields when a task leaves a release; 0.10.2 already states it (`journey= journey-release= journey-story= journey-required-tasks= journey-mapping-complete=` with `status --set`), so the comment is a false positive.
Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Needed at ideation: whether both follow-ups land as one patch and when, once the Captain schedules this task.
Result: the FO delegates these questions to ideation, which decides each with its source and returns any ruling that needs the Captain.
Surfaces: none
Visible change: none
