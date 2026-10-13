---
title: dispatch_records.py passes a follow-up dispatch record that lacks the Package root line or points at another record's checklist
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:followup-dispatch-records-checked:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:followup-dispatch-records-checked-backlog-1
              briefing:
                id: briefing:followup-dispatch-records-checked:backlog:attempt-1:revision-1
                digest: sha256:4ce24e66d181a61aabaf5c19975ff732a066960c2a3901c992c7dda8d9d9fc6c
                room-ref: ./followup-dispatch-records-checked/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:followup-dispatch-records-checked:backlog:1
                briefing: briefing:followup-dispatch-records-checked:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-13T15:57:08.952637Z"
                decision: approve
                reason: 'Captain approved (「approve」): schedule as Pilot and enter ideation, first of the order 1, 3, 2.'
              application:
                target-stage: ideation
                state: consumed
---

Filed from a learn package-issue candidate the Captain approved on 2026-10-13 (「按建議1,3」), after the observer report on task `learn-delivery-follow-through` (PR #639) found follow-up dispatch records `implementation-3.md`, `-5.md` and `-7.md` with no `Package root:` line and a checklist that reads "Same checklist as implementation-N." The README Stages rules already require both parts on a follow-up message's record, and learn judged it no-change for that reason: the rule exists and was not followed.

## Scope

- The gap is enforcement: `dispatch_records.py` (origin/main 544d1743) reports "12 dispatch record(s) complete", exit 0, on `_archive/learn-delivery-follow-through`, including the three records above (checked 2026-10-13 with `git show origin/main:kc-dev-flow-2/scripts/dispatch_records.py` run against that directory).
- Candidate fix: the check fails a record without a `Package root:` line and a record whose checklist only points at another record. Whether follow-up records may point instead of copying is a design question for ideation.
- Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Alignment: not needed before ideation; the Captain approved filing it.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
