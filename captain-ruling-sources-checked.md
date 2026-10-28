---
title: A Captain ruling recorded from a peer's relayed words is refused by a check FO already runs
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:captain-ruling-sources-checked:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:captain-ruling-sources-checked-backlog-1
              briefing:
                id: briefing:captain-ruling-sources-checked:backlog:attempt-1:revision-1
                digest: sha256:c84dde7cc43e154da060c0b6083fa27ed32494d0046f129f457674091e43c6d4
                room-ref: ./captain-ruling-sources-checked/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:captain-ruling-sources-checked:backlog:1
                briefing: briefing:captain-ruling-sources-checked:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-28T05:38:57.95005Z"
                decision: approve
                reason: The Captain 「准」 (chat, 2026-10-28), answering FO's joint batch-9 backlog presentation of five gates whose ask was 「決定：五張全准進入設計階段；要拿掉或換掉哪張，直接說。」; accepts FO's recommendation to enter ideation on the pilot profile.
              application:
                target-stage: ideation
                state: pending
---

## Scope

- Source: the Captain 「全准」 (chat, 2026-10-27), accepting FO's recommendation to move the structured Captain-source check out of peers-rules-name-each-host-binding into its own task, designed together with adr-required-statement.
- Bite: peers interview round 1 (fo-interviews-extension/peers-round-1.md): qnow recorded two peer-relayed rulings as the Captain's (agents-md-adr-pointer, product-analytics-posthog); ops-inbox recorded relayed quotes as "relayed" without reading the source.
- Input: the design in peers-rules-name-each-host-binding (section "Structured refusal at the existing check" and its ideation decision 2, at its 2026-10-27 head): a `## Captain sources` section, `design_surfaces.py check` refusing missing, unknown or peer-relay origins, and backfill of active tasks. FO's concern at the gate: every Captain ruling would need a structured entry and active tasks without readable originals would hold, against two bites in one adopter.
- Upstream first: adr-required-statement (another session; designs a `## Captain rulings` section for the same check), `scripts/design_surfaces.py`, `scripts/decision_ledger.py`.

## Non-goals

- Designing adr-required-statement (another session; coordinate only); checking rulings in archived tasks.

## Budget

- One package PR in `scripts/design_surfaces.py`; a backfill of active tasks only if the Captain accepts it at ideation.

## Stop condition

- The two qnow bites replay as refused and current active tasks pass or are listed by name. Return to the Captain if the design needs a structured entry for every Captain ruling (FO's concern at the 2026-10-27 gate).

## FO alignment

Alignment: needed before ideation; the scope of the check and any backfill are the Captain's.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
