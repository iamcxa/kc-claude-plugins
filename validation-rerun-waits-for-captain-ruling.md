---
title: A validation rerun is refused while the previous validation's Needs decision finding has no Captain ruling
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:validation-rerun-waits-for-captain-ruling:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:validation-rerun-waits-for-captain-ruling-backlog-1
              briefing:
                id: briefing:validation-rerun-waits-for-captain-ruling:backlog:attempt-1:revision-1
                digest: sha256:d36a5fb64dd9282e0c42919ae7a096cf8361cf8472b62eb565afb3a79b070341
                room-ref: ./validation-rerun-waits-for-captain-ruling/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:validation-rerun-waits-for-captain-ruling:backlog:1
                briefing: briefing:validation-rerun-waits-for-captain-ruling:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-29T00:39:50.417777Z"
                decision: approve
                reason: The Captain 「同意這些內容」 (chat, 2026-10-29), answering FO's joint batch-10 backlog sitting of six gates whose ask was 「決定：六張全照建議（五張進設計，被取代條件那張先留在待辦）？要改哪張直接說。」; accepts FO's recommendation to enter ideation on the pilot profile.
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: the Captain 「那就a吧」 (chat, 2026-10-29), choosing FO's batch-10 theme "checks for FO's repeated mistakes", whose row named this item: 「新：驗收結果需要你裁決時，我自己重跑驗收」.
- Bite: paseo-codex-dispatch-practice (#742, 2026-10-28): validation-1 returned F1 as Needs decision; FO ran validations 2 and 3 without a Captain ruling; his later approval covered only validation 4 (observer report, paseo-codex-dispatch-practice/observer.md). The README's review-finding disposition already routes a Needs decision to the Captain; nothing checks it before the next validation dispatch.
- Upstream first: README Review-finding disposition, `scripts/dispatch_records.py` (the check FO runs before each dispatch), `scripts/delivery_gate.py`.

## Non-goals

- Judging whether a finding is correctly classed as Needs decision; only that a ruling exists before a rerun.

## Budget

- One package PR inside an existing check; no new script.

## Stop condition

- The #742 sequence replays with validation-2's dispatch refused, and every current task whose reruns followed a ruling passes.

## FO alignment

Alignment: not needed before ideation: a check for a rule the README already states.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
