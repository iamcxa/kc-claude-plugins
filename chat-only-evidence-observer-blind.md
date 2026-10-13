---
title: FO rules whose evidence lives only in chat leave the observer at can't tell
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Filed from a learn package-issue candidate the Captain approved on 2026-10-13 (「按建議1,3」). The observer reports on tasks `fo-record-checks` (PR #640) and `learn-delivery-follow-through` (PR #639) both marked the same FO rules `can't tell`, because the rules require FO to do something in front of the Captain but not to leave a record in state.

## Scope

- Rules read as `can't tell` in both reports: the validation step "presents every step in full beside its observed output"; "Before recommending delivery, FO confirms both goal sufficiency and minimal necessity"; Delivery authority "present the exact candidate and PR body before authorized push/create". In one report each: the head read before the merge ask, the backlog `design_surfaces.py check --seed` run, `pr_watch.py add`, and whether a gate ruling needs an ADR.
- Learn judged it no-change: the rules exist and attribution to an outcome is unknown. The package question is whether each rule should name the record FO leaves (for example a line in the committed gate summary), or be accepted as chat-only and dropped from the observer's checks.
- Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Alignment: not needed before ideation; the Captain approved filing it.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
