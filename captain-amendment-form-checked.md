---
title: A Captain amendment entry is refused when it sits outside ## Captain amendments, rewrites an earlier entry, or its Supersedes line carries FO prose instead of criterion ids
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:captain-amendment-form-checked:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:captain-amendment-form-checked-backlog-1
              briefing:
                id: briefing:captain-amendment-form-checked:backlog:attempt-1:revision-1
                digest: sha256:0d28352a2e367af68e41b57cc25afc15c83855242cbd0ac6279f82e038ac2f01
                room-ref: ./captain-amendment-form-checked/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:captain-amendment-form-checked:backlog:1
                briefing: briefing:captain-amendment-form-checked:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-29T00:39:38.835331Z"
                decision: approve
                reason: The Captain 「同意這些內容」 (chat, 2026-10-29), answering FO's joint batch-10 backlog sitting of six gates whose ask was 「決定：六張全照建議（五張進設計，被取代條件那張先留在待辦）？要改哪張直接說。」; accepts FO's recommendation to enter ideation on the pilot profile.
              application:
                target-stage: ideation
                state: pending
---

## Scope

- Source: the Captain 「全准」 (chat, 2026-10-28), answering FO's batch-8 closing sitting, item 二 (open two package tasks so a check refuses what FO kept getting wrong).
- Bite: batch-8 observer reports (2026-10-28): amendment 2 written under ## Number guards (seed-check-requires-schema-fields) and a Feedback Cycles block parsed as an amendment (idle-hook-names-merged-tasks-without-learn); FO rewrote amendment 1's Supersedes line (read-adr-honors-adr-folder); FO's Supersedes summary dropped the accepted no-repeat words (idle-hook-names-merged-tasks-without-learn, which caused its AC-8 conflict); an accepted limit recorded as an amendment only after the observer flagged it (read-adr-honors-adr-folder). learn evaluations: each is an existing README rule FO did not follow.
- Upstream first: README ## Captain amendments, `scripts/design_surfaces.py` (`check_amendments`), `scripts/dispatch_records.py`.

- Added 2026-10-29, batch-9 bites: FO edited appended amendment 1 entries after writing them (reused-worker-dispatch-leaves-a-record and fo-interviews-extension observer reports, 2026-10-28/29); FO's Design: quotes, copied up to the next blank line, swept in neighbouring bullets the Captain kept (reused-worker: the --coverage bullets; fo-interviews: four bullets) and dropped an opening fence (batch-reaches-each-gate-together); engineering-reviewer found criteria still carrying withdrawn content not listed under Supersedes (batch-reaches AC-5 to AC-7, reused-worker AC-7).
## Non-goals

- Checking prose quality or whether a summary is faithful; only the structure the README already states.

## Budget

- One package PR; no new script.

## Stop condition

- The check refuses each bite in the replay and passes every current task file that follows the README.

## FO alignment

Alignment: needed before ideation; where the check runs is a package design choice.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
