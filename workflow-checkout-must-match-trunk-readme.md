---
title: FO cannot dispatch from a workflow checkout whose README is behind the trunk's
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:workflow-checkout-must-match-trunk-readme:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:workflow-checkout-must-match-trunk-readme-backlog-1
              briefing:
                id: briefing:workflow-checkout-must-match-trunk-readme:backlog:attempt-1:revision-1
                digest: sha256:d6001df6e2e7560bd301674e05d448b7d2a266fa2ffd1b9a6b1c487624db131e
                room-ref: ./workflow-checkout-must-match-trunk-readme/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:workflow-checkout-must-match-trunk-readme:backlog:1
                briefing: briefing:workflow-checkout-must-match-trunk-readme:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-13T07:17:04.046205Z"
                decision: approve
                reason: 'Captain 2026-10-13: 「准」 to the backlog gate question "Schedule now as Pilot and enter ideation, in the fix order 1 workflow-checkout-must-match-trunk-readme, 2 observer-before-merge-guard, 3 worker-completion-goes-to-main (all three designed now; implementation in that order)?", after 「1-3 回報，且立即排修，順序該怎麼列？」; profile pilot selected.'
              application:
                target-stage: ideation
                state: consumed
started: 2026-10-13T07:17:36Z
---

On 2026-10-13 FO drove task `journey-map-dev2-contract` through backlog, ideation, implementation and validation from a workflow checkout detached at a 2026-10-08 commit whose `docs/dev2/README.md` was 397 lines behind the 0.21.0 sync on origin/main (e2524e93). Four dispatches (ideation-1, ideation-3, implementation-1, validation-1) ran on the stale rules; two rules only the newer README carries were missed (dispatch records under `<task>/dispatch/`, the `package_version.py` hold). Observer report on that task, violations 3 and 4. `package_version.py` compares the loaded package with the README it is given, so a stale README passes; nothing compares the README with the trunk's.

## Captain's words

Captain 2026-10-13, in chat, after the learn result listed this as package-issue candidate 3: 「1-3 回報，且立即排修」

## Scope

- A check FO runs before a dispatch that fails when the workflow checkout's README differs from the trunk's README, with the remedy named.
- Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Alignment: not needed before ideation; the Captain ruled to report and fix now.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
