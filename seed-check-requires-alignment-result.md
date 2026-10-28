---
title: The seed check refuses a task whose FO alignment says needed and records no Result line
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: FO's own miss, filed by FO with no Captain ruling yet; the Captain rules it at the next backlog sitting.
- Bite: batch 9 (2026-10-28): three ideation workers (batch-reaches-each-gate-together, captain-ruling-sources-checked, reused-worker-dispatch-leaves-a-record) held at their first step because `## FO alignment` said "needed" with no `Result:` line, costing three dispatches; the same miss on adr-protected-path-guard (2026-10-23). Each time `design_surfaces.py check --seed` (0.32.1) passed the task: it printed "seed fields and FO alignment recorded" for all five batch-9 seeds before the Result lines existed.
- Upstream first: `scripts/design_surfaces.py` (`check --seed`), `skills/ideation/principles.md` (the stop rule the workers applied), the workflow README FO alignment section.

## Non-goals

- Judging whether a Result line's content is a real alignment; only that it exists when alignment is recorded as needed before the stage being dispatched.

## Budget

- One package PR in `scripts/design_surfaces.py` and its tests; no new script.

## Stop condition

- The three batch-9 seeds as committed before their Result lines replay as refused, and every current task that records a Result passes.

## FO alignment

Alignment: not needed before ideation: a check for a rule the ideation principles already state.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
