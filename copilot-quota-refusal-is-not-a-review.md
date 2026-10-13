---
title: The copilot extension reads a quota-limit refusal as "Copilot not run", never as an answered review, and FO's merge ask names it unread
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:copilot-quota-refusal-is-not-a-review:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:copilot-quota-refusal-is-not-a-review-backlog-1
              briefing:
                id: briefing:copilot-quota-refusal-is-not-a-review:backlog:attempt-1:revision-1
                digest: sha256:9766c3e0940f18f3725c5b5e55fcf2f62d1430747aa870036f9e32ce88d8761a
                room-ref: ./copilot-quota-refusal-is-not-a-review/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:copilot-quota-refusal-is-not-a-review:backlog:1
                briefing: briefing:copilot-quota-refusal-is-not-a-review:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-13T06:56:03.975306Z"
                decision: approve
                reason: 'Captain 2026-10-13: 「是」 to the backlog gate question "Schedule this task now as Pilot and enter ideation", after asking 「Copilot 的 task是否可以先排？因為顯然會接下來一直遇到此問題」; profile pilot selected.'
              application:
                target-stage: ideation
                state: consumed
started: 2026-10-13T06:56:42Z
---

On 2026-10-13 FO requested Copilot on iamcxa/kc-claude-plugins #627 and #628 (task `journey-map-dev2-contract`). Six seconds later Copilot left a COMMENTED review on each: "Copilot was unable to review this pull request because the user who requested the review has reached their quota limit." `python3 <package>/extensions/copilot/copilot_review.py iamcxa/kc-claude-plugins 627` printed `answered on 32db12730: "no heading", 0 line comment(s); evidence=review:5499757433` and exited 0 (the same for #628, review:5499757731). Exit 0 is the reader's "answered" result, so a quota refusal reads like a review of the head with no findings unless FO reads the body.

## Captain's words

Captain 2026-10-13, in chat, after FO reported the quota refusal and asked whether to merge #627 without Copilot: 「不等 Copilot，也要修復它額度不足時的應對方式」

## Scope

- The reader and FO's handling when Copilot refuses for quota: it must not count as a round or as a clean read; it is reported as `copilot not run: <reason>`, as `## Extensions` already requires for a listed extension that cannot run.
- What FO does next when the second reviewer cannot run (the Captain ruled this time: do not wait).
- Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Alignment: not needed before ideation; the Captain's two rulings fix the direction (do not wait for Copilot; repair the quota handling, scheduled now as Pilot). Open for ideation, not a Captain question: whether other non-review Copilot answers (an error, a "cannot review" text in another language) share the fix.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
