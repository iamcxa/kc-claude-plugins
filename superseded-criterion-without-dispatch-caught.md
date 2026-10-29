---
title: A superseded criterion with no later dispatch is still caught
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:superseded-criterion-without-dispatch-caught:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:superseded-criterion-without-dispatch-caught-backlog-1
              briefing:
                id: briefing:superseded-criterion-without-dispatch-caught:backlog:attempt-1:revision-1
                digest: sha256:af1bb8385e43941ce189d271787971a948d3d80f20d8fa3b9058a2a80485edc1
                room-ref: ./superseded-criterion-without-dispatch-caught/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:superseded-criterion-without-dispatch-caught:backlog:1
                briefing: briefing:superseded-criterion-without-dispatch-caught:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-29T00:40:02.350315Z"
                decision: hold
                reason: The Captain 「同意這些內容」 (chat, 2026-10-29), answering FO's joint batch-10 backlog sitting whose ask was 「決定：六張全照建議（五張進設計，被取代條件那張先留在待辦）？要改哪張直接說。」; accepts FO's recommendation to hold in backlog until a real task archives with a superseded criterion still declared.
---

## Scope

- Source: validation of fo-written-lines-checked-before-dispatch (PR iamcxa/kc-claude-plugins#724, head b0b2cbf3), finding F4, Deferred risk: an amendment followed by no later dispatch can leave superseded criteria declared without a `design_surfaces.py` error. That PR makes a superseded criterion wait in place until a dispatch checklist names its amendment; if no dispatch follows, nothing names it.
- Observed: not observed in any task (validation, 2026-10-26).
- Bite: none yet; file only so the gap is not lost. Reopen when a task archives with a superseded criterion still declared.

- Added 2026-10-29: the Captain 「那就a吧」 (chat) chose FO's batch-10 theme, whose row listed 「被取代的驗收條件漏抓」. Batch 9 showed no archived task with a superseded criterion still declared; engineering-reviewer found criteria carrying withdrawn content that were never listed under Supersedes (a different gap, under captain-amendment-form-checked).

## Non-goals

- Criteria never listed under Supersedes (captain-amendment-form-checked owns that).

## Budget

- One package PR inside `scripts/design_surfaces.py`; no new script.

## Stop condition

- A replayed task that archives with a superseded criterion still declared and no later dispatch is refused; return to the Captain if no real task shows the gap.
## FO alignment

Alignment: needed before ideation; no bite yet.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
