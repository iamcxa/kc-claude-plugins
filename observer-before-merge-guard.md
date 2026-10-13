---
title: The learn extension's observer runs before merge guard archives a task, or the archive is held
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:observer-before-merge-guard:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:observer-before-merge-guard-backlog-1
              briefing:
                id: briefing:observer-before-merge-guard:backlog:attempt-1:revision-1
                digest: sha256:ac07b8820cdcf8a74d62e0239d938c6ca261f9b91f28880ed293774f9627d3ce
                room-ref: ./observer-before-merge-guard/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:observer-before-merge-guard:backlog:1
                briefing: briefing:observer-before-merge-guard:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-13T07:17:09.539504Z"
                decision: approve
                reason: 'Captain 2026-10-13: 「准」 to the backlog gate question "Schedule now as Pilot and enter ideation, in the fix order 1 workflow-checkout-must-match-trunk-readme, 2 observer-before-merge-guard, 3 worker-completion-goes-to-main (all three designed now; implementation in that order)?", after 「1-3 回報，且立即排修，順序該怎麼列？」; profile pilot selected.'
              application:
                target-stage: ideation
                state: consumed
started: 2026-10-13T07:17:39Z
---

The learn extension's FO step requires dispatching `kc-dev-flow-2:observer` and committing `<task>/observer.md` before `merge guard`, because an archived task's state is publish-only. On 2026-10-13 FO ran `merge guard --verdict passed` on `journey-map-dev2-contract` without it; the observer ran afterwards and its report could not be saved into the task. The learn evaluation (job 92da235b) recorded this as a rule that exists and was not followed; nothing blocks `merge guard` when `observer.md` is absent.

## Captain's words

Captain 2026-10-13, in chat, after the learn result listed this as package-issue candidate 1: 「1-3 回報，且立即排修」

## Scope

- Make a missing `observer.md` stop the archive path, or make it impossible to reach `merge guard` without the observer step, with the remedy named.
- Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Alignment: not needed before ideation; the Captain ruled to report and fix now.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
