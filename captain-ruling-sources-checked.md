---
title: A Captain ruling recorded from a peer's relayed words is refused by a check FO already runs
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「全准」 (chat, 2026-10-27), accepting FO's recommendation to move the structured Captain-source check out of peers-rules-name-each-host-binding into its own task, designed together with adr-required-statement.
- Bite: peers interview round 1 (fo-interviews-extension/peers-round-1.md): qnow recorded two peer-relayed rulings as the Captain's (agents-md-adr-pointer, product-analytics-posthog); ops-inbox recorded relayed quotes as "relayed" without reading the source.
- Input: the design in peers-rules-name-each-host-binding (section "Structured refusal at the existing check" and its ideation decision 2, at its 2026-10-27 head): a `## Captain sources` section, `design_surfaces.py check` refusing missing, unknown or peer-relay origins, and backfill of active tasks. FO's concern at the gate: every Captain ruling would need a structured entry and active tasks without readable originals would hold, against two bites in one adopter.
- Upstream first: adr-required-statement (another session; designs a `## Captain rulings` section for the same check), `scripts/design_surfaces.py`, `scripts/decision_ledger.py`.

## FO alignment

Alignment: needed before ideation; the scope of the check and any backfill are the Captain's.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
