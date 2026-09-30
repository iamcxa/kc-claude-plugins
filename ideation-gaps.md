---
title: Ideation cannot start without FO alignment, reach its gate without acceptance criteria, lose a Captain amendment, or scatter ADR drafts
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Four ideation-stage gaps from qnow dogfooding (2026-09-26..30) that each cost a worker round, a hand rewrite at a gate, or a drifting ADR number.

## Scope

Captain 2026-09-30, on the FO's split of batch C: 「可以」 — this task (issues #517, #518, #519, #529) first; #520 (whole-journey release re-review) waits for his journey-map alignment work; the package release waits for batch C.
Evidence (qnow and this repo): `dispatch build --stamp` succeeded for an entity with no `## FO alignment` section and the worker then held on `design_surfaces.py check`; after an approved ideation gate the Captain changed the direction, the superseded acceptance criteria stayed in force for `status --read --ac-scan`, and the FO rewrote the acceptance script by hand; `gate prepare` accepted a pilot ideation report with no `## Acceptance criteria` section; one ideation worker committed a draft ADR to a branch in the shared checkout and later designs kept ADR drafts inline with drifting numbers. Since then `number_guards.py reserve` (PR #533) reserves ADR numbers per task, and in this repo's last two tasks the FO recorded Captain amendments only in the gate reason and dispatch checklists.
Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Needed at ideation: where the FO learns before spawning an ideation worker that the task lacks `## FO alignment`; where a missing `## Acceptance criteria` section is caught before an ideation gate opens; a supported way to record a Captain amendment that supersedes named acceptance criteria and that later stages, the acceptance script and `--ac-scan` respect; where ideation-time ADR drafts live and how their number relates to `number_guards.py reserve`.
Result: the FO delegates these questions to ideation, which decides each with its source and returns any ruling that needs the Captain.
Surfaces: none
Visible change: none
