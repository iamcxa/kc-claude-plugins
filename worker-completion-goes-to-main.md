---
title: A dispatched worker sends its completion message to main, not to the unregistered team-lead
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
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
