---
title: Ideation cannot start without FO alignment, reach its gate without acceptance criteria, lose a Captain amendment, or scatter ADR drafts
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:ideation-gaps:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:ideation-gaps-backlog-1
              briefing:
                id: briefing:ideation-gaps:backlog:attempt-1:revision-1
                digest: sha256:fbe74a0bac085b447c809aaa05c821d96c03387f9c852d2efbdde42e4b1e5705
                room-ref: ./ideation-gaps/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:ideation-gaps:backlog:1
                briefing: briefing:ideation-gaps:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-30T08:32:40.061687Z"
                decision: approve
                reason: 'Captain 2026-09-30: 「可以」 to the FO''s split of batch C, this part first'
              application:
                target-stage: ideation
                state: consumed
started: 2026-09-30T08:33:02Z
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
