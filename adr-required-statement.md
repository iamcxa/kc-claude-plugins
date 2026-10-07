---
title: A product ruling cannot reach the terminal gate without its ADR going unnoticed
status: backlog
variant: kc-dev-flow-2
profile: pilot
merge: pr
gates:
    version: 1
    records:
        - id: gate:adr-required-statement:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:adr-required-statement-backlog-1
              briefing:
                id: briefing:adr-required-statement:backlog:attempt-1:revision-1
                digest: sha256:8a925c22da40c37234b8d7ded48b97bba9bc03c489dba0d092448ddd3154b48b
                room-ref: ./adr-required-statement/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:adr-required-statement:backlog:1
                briefing: briefing:adr-required-statement:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-07T14:17:26.037406Z"
                decision: approve
                reason: 'Captain 2026-10-07: 「核准 adr-required-statement，以 Pilot 進入設計」 — confirms the request relayed by dhaka-32'
              application:
                target-stage: ideation
                state: pending
---

`references/sd/workflow.md` § Decision records requires an ADR for a ruling "settled at a gate, in a worker report, or mid-stage feedback" that later work must respect, and validation runs `adr_lint.py docs/adr --require <numbers>` only for the numbers the implementation report names. A ruling stated when the task is created (in FO alignment, before backlog) is not named by the trigger, and a report that names no ADR gives validation nothing to check, so a missing record passes silently.

## Scope

Relayed by the peer session dhaka-32 on 2026-10-07, quoting the Captain's approval to file it upstream 「要，交給上游修」 (not yet confirmed by the Captain in this session). Case: subspace-web dev2-poc task `subspace-tab-icon` (state branch spacedock-state/dev2-poc): the Captain's request 「目前 web 的 fav icon 是 spacedock 的，但我想要改成 spacedock-design 內的 subspace icon 請你排進去做」 (2026-10-05) reversed an earlier product choice (2026-09-24); both gates were approved and subspace-web#101 shipped with no ADR; the ADR was written afterwards as subspace-web#103.
Direction relayed as the Captain's (shape is the worker's to design): the implementation report states which ADRs it added, or `none` with a reason, and an absent statement fails validation; the FO alignment section marks whether the Captain's words set a product rule. Accepted cost (relayed): one more required line per task, POC included.
Non-goals: back-filling ADRs in adopters; changing the ADR template.

## Acceptance criteria

To be written at ideation.

## FO alignment

Release review: not needed: package process defect, no journey story.
Needed at ideation: no Captain alignment before ideation; ideation checks the change against the POC derivation (poc_readme.py) and every adopter-synced surface, and returns any change to what a POC task owes.
Surfaces: none
Visible change: none
