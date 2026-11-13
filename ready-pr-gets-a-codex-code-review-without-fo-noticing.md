---
title: A PR marked ready gets its Codex code review without FO noticing a security-only pass by hand
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:ready-pr-gets-a-codex-code-review-without-fo-noticing:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:ready-pr-gets-a-codex-code-review-without-fo-noticing-backlog-1
              briefing:
                id: briefing:ready-pr-gets-a-codex-code-review-without-fo-noticing:backlog:attempt-1:revision-1
                digest: sha256:86f5ecfa7e4c86ae717d90246f83f5b9d57be182e55d8f8cff001e90558d85fb
                room-ref: ./ready-pr-gets-a-codex-code-review-without-fo-noticing/review/backlog/briefing-1
---

## Scope

- Source: the Captain 「3. 要」 (chat, 2026-11-13), answering FO's item 3: 「下一輪顧問試跑要不要現在開始準備，以及是否把「合併前這一段」的三個摩擦點各開一張任務。」 Evidence: the route trial of 2026-11-13, FO's hand-kept log and result (worker stages took 15 to 30 minutes; validated to merge ask took 85 to 120 minutes on three tasks).
- Bite: on 2026-11-13 Codex answered three of four ready PRs with a security-only pass; the reader already prints the next line telling FO to comment once, but nothing ran it until FO looked, and FO's wait loop held two ready PRs about 40 minutes behind the third.
- Upstream first, open for the design: what the delivery check, the validation skill text and the listed extensions already do for this, and whether a smaller change to one of them is enough.
- Non-goals: to be set at ideation.

## Budget
1 implementation and 2 validation cycles, in one package PR.

## Stop condition
- In a replay of the four recorded PR states, the security-only ones get exactly one trigger and none gets two, with no FO step between ready and the trigger.

## FO alignment

Alignment: not needed before ideation: an observed friction with counts; the mechanism is compared in the design.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
