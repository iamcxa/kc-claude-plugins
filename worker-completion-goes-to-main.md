---
title: A dispatched worker sends its completion message to main, not to the unregistered team-lead
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:worker-completion-goes-to-main:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:worker-completion-goes-to-main-backlog-1
              briefing:
                id: briefing:worker-completion-goes-to-main:backlog:attempt-1:revision-1
                digest: sha256:d4372a8d995a58c48d223e54183fb9593d49e577e9cfdaa35b8813016e275674
                room-ref: ./worker-completion-goes-to-main/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:worker-completion-goes-to-main:backlog:1
                briefing: briefing:worker-completion-goes-to-main:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-13T07:17:15.098932Z"
                decision: approve
                reason: 'Captain 2026-10-13: 「准」 to the backlog gate question "Schedule now as Pilot and enter ideation, in the fix order 1 workflow-checkout-must-match-trunk-readme, 2 observer-before-merge-guard, 3 worker-completion-goes-to-main (all three designed now; implementation in that order)?", after 「1-3 回報，且立即排修，順序該怎麼列？」; profile pilot selected.'
              application:
                target-stage: ideation
                state: pending
---

Spacedock's dispatch completion block tells the worker to send `SendMessage(to="team-lead")`; under Claude Code dispatch that name is not registered (spacedock-dev/spacedock #523 and #608, both open on 2026-10-13). The adopter README's Dispatch facts already say to message `main`. On 2026-10-13 the first implementation worker of `journey-map-dev2-contract` still tried `team-lead` first and fell back to its final message; workers whose scope notes carried the explicit line "Send your completion message to `main`" sent to `main`. The root is upstream Spacedock; this task owns only the kc-dev-flow-2 side.

## Captain's words

Captain 2026-10-13, in chat, after the learn result listed this as package-issue candidate 2: 「1-3 回報，且立即排修」

## Scope

- The kc-dev-flow-2 side of the fix (for example, FO's dispatch scope notes always carry the `main` line) and whether to add this evidence to spacedock-dev/spacedock #523 or #608, which is an outward-facing comment for the Captain.
- Non-goals: changing Spacedock.

## Acceptance criteria

To be written at ideation.

## FO alignment

Alignment: not needed before ideation; the Captain ruled to report and fix now.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
