---
title: A gate is prepared only when the role calls and review rounds the README requires are recorded where it says
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:gate-requires-recorded-reviews:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:gate-requires-recorded-reviews-backlog-1
              briefing:
                id: briefing:gate-requires-recorded-reviews:backlog:attempt-1:revision-1
                digest: sha256:238d2f348cf94a1996245ac7ba22e28cad351f01dc71a2df927acf522a0bb867
                room-ref: ./gate-requires-recorded-reviews/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:gate-requires-recorded-reviews:backlog:1
                briefing: briefing:gate-requires-recorded-reviews:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-29T00:39:56.455786Z"
                decision: approve
                reason: The Captain 「同意這些內容」 (chat, 2026-10-29), answering FO's joint batch-10 backlog sitting of six gates whose ask was 「決定：六張全照建議（五張進設計，被取代條件那張先留在待辦）？要改哪張直接說。」; accepts FO's recommendation to enter ideation on the pilot profile.
              application:
                target-stage: ideation
                state: pending
---

## Scope

- Source: the Captain 「那就a吧」 (chat, 2026-10-29), choosing FO's batch-10 theme "checks for FO's repeated mistakes", built from batch 9's observer violations.
- Bite: batch-reaches-each-gate-together (observer, 2026-10-28): the two chief-engineer batch reviews were not recorded as `Reviewer:` lines under ## FO alignment (FO saved them in a side folder); fo-interviews-extension (observer, 2026-10-29): the committed gate summary of the approved validation gate carried no external-review rounds and no second-reviewer outcome (they reached only the later merge-ask text checked by delivery_gate.py).
- Upstream first: README (Reviewer line under ## FO alignment, the second-reviewer and external-round lines), `scripts/delivery_gate.py` (checks the merge ask text, not the gate summary), `scripts/role_triggers.py`, Spacedock `gate prepare`.

## Non-goals

- Deciding which reviews are owed (role_triggers.py and the README do that); checking review content.

## Budget

- One package PR inside an existing check; no new script.

## Stop condition

- Both bites replay as refused before gate preparation, and every current task that recorded its calls passes.

## FO alignment

Alignment: not needed before ideation: a check for rules the README already states.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
