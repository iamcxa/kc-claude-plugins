---
title: The Number guards passage of the workflow README shrinks to what number_guards.py cannot tell its reader
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:number-guards-readme-shrink:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:number-guards-readme-shrink-backlog-1
              briefing:
                id: briefing:number-guards-readme-shrink:backlog:attempt-1:revision-1
                digest: sha256:12b30dc0c3e9ea1e4d878894053b72844eea50863fc36c9673d6876daef9ffcd
                room-ref: ./number-guards-readme-shrink/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:number-guards-readme-shrink:backlog:1
                briefing: briefing:number-guards-readme-shrink:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-18T16:57:03.744159Z"
                decision: approve
                reason: Captain approved in chat (「批准這些作為第三批」) the five batch-3 backlog gates presented together, accepting the recommended profiles and the stated grouping and order
              application:
                target-stage: ideation
                state: consumed
started: 2026-10-18T16:57:47Z
---

Filed under D4 of workflow-budget-ratchet, approved by the Captain on 2026-10-17 (「那就照建議」 to the batch-2 ideation gates, whose question said approving accepts D4: "Number guards becomes a follow-up task").

## Scope

- Measured by workflow-budget-ratchet's ideation on 0.24.0: the Number guards passage of `kc-dev-flow-2/references/sd/workflow.md` is 745 words, 13.6% of the README, the largest single candidate for the ratchet's shrink rule; its script messages were not read there.
- Apply the ratchet's rule: read each `kc-dev-flow-2/scripts/number_guards.py` failure message first; a rule the script enforces and whose message tells the reader what to do shrinks to one pointer sentence; the budget falls by the words removed in the same change.
- Bite to confirm at ideation: the observer's count of number-guard violations (an ADR number reserved after the first implementation dispatch happened twice, on prod-security-review-gates 2026-10-16/17).

## FO alignment

Alignment: not needed before ideation; the Captain approved filing it as a follow-up of workflow-budget-ratchet D4.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
