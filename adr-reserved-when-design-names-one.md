---
title: An implementation dispatch for a task whose design calls for an ADR is refused until an ADR number is reserved in ## Number guards
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:adr-reserved-when-design-names-one:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:adr-reserved-when-design-names-one-backlog-1
              briefing:
                id: briefing:adr-reserved-when-design-names-one:backlog:attempt-1:revision-1
                digest: sha256:54eb1a6854e50fa913931776a3125fcae222a0eeebabecd91f45c7e5bf00ff95
                room-ref: ./adr-reserved-when-design-names-one/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:adr-reserved-when-design-names-one:backlog:1
                briefing: briefing:adr-reserved-when-design-names-one:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-29T00:39:44.625775Z"
                decision: approve
                reason: The Captain 「同意這些內容」 (chat, 2026-10-29), answering FO's joint batch-10 backlog sitting of six gates whose ask was 「決定：六張全照建議（五張進設計，被取代條件那張先留在待辦）？要改哪張直接說。」; accepts FO's recommendation to enter ideation on the pilot profile.
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: the Captain 「全准」 (chat, 2026-10-28), answering FO's batch-8 closing sitting, item 二 (open two package tasks so a check refuses what FO kept getting wrong).
- Bite: seed-check-requires-schema-fields (#740, 2026-10-28): its design records the ruling as an ADR, the first implementation dispatch carried no number, and the worker had to ask FO; codex-reader-same-head-unresolved (#728, 2026-10-27): an enduring ruling shipped without an ADR, fixed later by #732. dispatch-carries-reserved-adr-number was closed because the existing check only covers a number already reserved.
- Upstream first: `scripts/dispatch_records.py` (`check_task_facts`), `scripts/number_guards.py`, README Number guards.

## Non-goals

- Checking prose quality or whether a summary is faithful; only the structure the README already states.

## Budget

- One package PR; no new script.

## Stop condition

- The check refuses each bite in the replay and passes every current task file that follows the README.

## FO alignment

Alignment: needed before ideation; where the check runs is a package design choice.
Result: aligned at backlog: the Captain 「同意這些內容」 (chat, 2026-10-29) to FO's batch-10 backlog sitting, which asked 「決定：六張全照建議（五張進設計，被取代條件那張先留在待辦）？要改哪張直接說。」, approved the outcome and bounds in this file. Where the check runs is a package design choice ideation proposes and the ideation gate rules.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
