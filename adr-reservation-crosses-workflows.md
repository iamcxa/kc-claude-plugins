---
title: An ADR number reserved by one workflow's task is seen by every workflow that writes ADRs to the same repository
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

`number_guards.py` refuses a new ADR number that another workflow's live task has already reserved in the same repository, so two FOs sharing a repository cannot both land the same number.

## Scope

- Source: the Captain 「開」 (chat, 2026-11-06), answering FO's batch 14 retrospective ask 「Should I open these two backlog tasks?」, whose first item was this cross-workflow reservation gap.
- Bite: gate-presentation-asks-one-thing-plainly reserved ADR 0060 in this workflow (dispatch 2026-11-05); kc-journey-map #789 (a7c0bdbe0, merged 2026-11-05 23:31 +0800) landed docs/adr/0060 and 0061 from the journey-map private-host workflow; `number_guards.py check --base a7c0bdbe0` then failed R5 on #788, which cost one renumber round (0060 to 0062) and a second validation (FO read of origin/main docs/adr and the #788 worker report, 2026-11-06).
- Upstream first: kc-dev-flow-2 `number_guards.py` (R4/R5, `reserve`), the README's Number guards, ADR-reservation rules; Spacedock has no cross-workflow lock.
- Non-goals: renumbering any landed ADR.

## Budget
- One package PR; the workflow word budget does not rise unless the design names a raise for the Captain.

## Stop condition
- A replay where a second workflow reserves or lands a number another workflow's live task holds is refused before its dispatch or merge ask, and a free number passes.

## FO alignment

Alignment: needed at ideation; where the shared reservation lives is a package design choice for him to accept.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
