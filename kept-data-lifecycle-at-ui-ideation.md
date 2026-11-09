---
title: Pilot ui ideation states the lifecycle of data kept across screens or sign-in
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:kept-data-lifecycle-at-ui-ideation:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:kept-data-lifecycle-at-ui-ideation-backlog-1
              briefing:
                id: briefing:kept-data-lifecycle-at-ui-ideation:backlog:attempt-1:revision-1
                digest: sha256:ed90aac6650f772a26d37c2cae82034cd5b2c2364e8e9cde0905d6203551fe7c
                room-ref: ./kept-data-lifecycle-at-ui-ideation/review/backlog/briefing-1
---

## Scope

- Source: the Captain 「准」 (chat, 2026-11-09, given in both the qnow dev2 FO session and this one), answering the qnow dev2 FO's question 「准不准他們照下面的條件去做？」, which put P1-P3 of /tmp/qnow-case/proposal.md and p1-revised.md (FO scratch, 2026-11-09) with their ship conditions.
- Bite: qnow task owner-vehicle-kept-after-name: 5 repair passes, 3 Material validations and 7 dispatches on one Symptom. Adopted 0.35.0 `role_triggers.py <state> <slug> --rev <state commit>` (run by the qnow dev2 FO, 2026-11-09) already owed a chief-engineer call (3 implementation dispatches on one symptom) and an engineering-reviewer call (replacing amendments 1-6) at state ee29b0a8 before implementation-4, and again at 27f04824 and 03829bf0 before implementations 5 and 6; FO never ran it and recorded neither a call nor a decline. Amendments 4 and 6 created data kept across screens and across sign-in with more than one writer, including a late async writer; no ideation text asked where that data starts, every way it ends, and who writes it.
- Change: the pilot ui ideation route requires, for data kept across screens or sign-in, its start, every end and every writer (late async writers included); the design director hands it to the engineering reviewer when it names more than one writer.
- Expected signal for the replay: the nine stand-in checks the qnow engineering reviewer's report lists under `## FO alignment` of owner-vehicle-kept-after-name.
- Non-goals: non-ui routes; a new reviewer role.

## Budget
- One package PR; workflow word budget unchanged unless the design names a raise.

## Stop condition
- Behaviour replay of ideation at amendments 4 and 6, current wording vs revised, 3 runs each: count the nine expected checks each design names. Ships only if the revised wording beats the current; otherwise this task closes with the table.
- Results go to the qnow dev2 FO for its Captain report.

## FO alignment

Alignment: not needed; the Captain approved the direction and ship condition.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
