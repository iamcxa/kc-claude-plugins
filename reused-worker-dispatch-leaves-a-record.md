---
title: A follow-up dispatch to a reused worker leaves a dispatch record before it is sent
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:reused-worker-dispatch-leaves-a-record:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:reused-worker-dispatch-leaves-a-record-backlog-1
              briefing:
                id: briefing:reused-worker-dispatch-leaves-a-record:backlog:attempt-1:revision-1
                digest: sha256:9682249dd49b43628e358a80e2df2fc1ef8b35a3a5f9dd97772029e8cf766227
                room-ref: ./reused-worker-dispatch-leaves-a-record/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:reused-worker-dispatch-leaves-a-record:backlog:1
                briefing: briefing:reused-worker-dispatch-leaves-a-record:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-28T05:38:45.589286Z"
                decision: approve
                reason: The Captain 「准」 (chat, 2026-10-28), answering FO's joint batch-9 backlog presentation of five gates whose ask was 「決定：五張全准進入設計階段；要拿掉或換掉哪張，直接說。」; accepts FO's recommendation to enter ideation on the pilot profile.
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: the Captain 「照建議」 (chat, 2026-10-27), answering FO's batch-7 retrospective list (items a to d).
- Bite: kc-ops-inbox task ops-metric-event-protocol (PR #727, two rejected validation cycles; its observer report at state commit f25c224f6, relayed by its FO 2026-10-27): no dispatch records for the implementation or validation dispatches sent to reused workers, and the misses that followed (no delivery_gate question before validation briefings 1 and 2, no Override line, polish items left out of FO declines) all sat on that path, where no `dispatch build --stamp` runs and nothing prompts the record. The README already says a follow-up message to a worker FO resumes is a dispatch.
- Upstream first: the README's Stages (follow-up dispatch rule), `scripts/dispatch_records.py`, `scripts/pr_watch.py tasks`, Spacedock `dispatch build`.

## Non-goals

- A change to Spacedock `dispatch build`; recording messages that are not dispatches (a question answered, a status read).

## Budget

- One package PR; extend `scripts/dispatch_records.py`, no new script.

## Stop condition

- The ops-metric-event-protocol path replays as caught (a reused-worker follow-up with no record is named before the next gate) and every current task with records still passes. Return to the Captain if the record can only be enforced inside Spacedock.

## FO alignment

Alignment: needed before ideation; where the check or rule lives is a package design choice.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
