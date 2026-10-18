---
title: The FO-write rules the observer keeps finding broken are checked by a script at the moment FO writes, not found days later at archive
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:fo-write-checks:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:fo-write-checks-backlog-1
              briefing:
                id: briefing:fo-write-checks:backlog:attempt-1:revision-1
                digest: sha256:1b87bc5fc0d24af8855070cd7ff9414049a99dbde3f9de9ba738aa1e36d544eb
                room-ref: ./fo-write-checks/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:fo-write-checks:backlog:1
                briefing: briefing:fo-write-checks:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-18T16:56:47.13191Z"
                decision: approve
                reason: Captain approved in chat (「批准這些作為第三批」) the five batch-3 backlog gates presented together, accepting the recommended profiles and the stated grouping and order
              application:
                target-stage: ideation
                state: consumed
started: 2026-10-18T16:57:29Z
---

Filed for batch 3 on the Captain's 「先走批次三規劃」 (chat, 2026-10-19), after FO reported at the batch-2 close that its own process mistakes repeat across tasks and should move from reminders into a script; the Captain enabled the state laws check on this repository the same day (「可以那就只開啟這個repo」).

## Scope

- Measured from the six batch-2 observer reports (2026-10-17 to 10-19): a decline in the gate summary with no reason, 4 of 6 tasks; the reserved `ADR: NNNN` line missing from the dispatch scope notes, 3 of 6; amendment-form breaks (amendment not named in the next dispatch's checklist, FO's own words in the `Design:` line, a Captain ruling recorded as a Feedback Cycle instead of an amendment), 3 of 6; a repair without a worker investigation phase, 1; a Material claim without the `value-ac[...]` field form, 1; a delivery gate presented while `adr_lint --require` exits 1, 1.
- Upstream first: what `laws_check.py` (L1, L2), `dispatch_records.py`, `delivery_gate.py`, `design_surfaces.py` and `observer_check.py` already check, and which of these rules one of them can absorb with no new FO words, so the check fires when FO writes (dispatch build, gate prepare, state push) rather than at archive.
- Bite: each class above, with the observer report that names it.
- Non-goals: to be set at ideation.

## FO alignment

Alignment: not needed before ideation; the Captain approved planning batch 3.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
