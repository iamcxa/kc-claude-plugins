---
title: A validation report's recorded commands pass the delivery check without a rewrite
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:validator-commands-fit-the-delivery-check:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:validator-commands-fit-the-delivery-check-backlog-1
              briefing:
                id: briefing:validator-commands-fit-the-delivery-check:backlog:attempt-1:revision-1
                digest: sha256:288f023b60dc235976f0c8d8332ebb7908c15f28934f09f9e4debe03f834d997
                room-ref: ./validator-commands-fit-the-delivery-check/review/backlog/briefing-1
---

## Scope

- Source: the Captain 「3. 要」 (chat, 2026-11-13), answering FO's item 3: 「下一輪顧問試跑要不要現在開始準備，以及是否把「合併前這一段」的三個摩擦點各開一張任務。」 Evidence: the route trial of 2026-11-13, FO's hand-kept log and result (worker stages took 15 to 30 minutes; validated to merge ask took 85 to 120 minutes on three tasks).
- Bite: three times in two days a validator's record held or misled the merge ask: an acceptance command pointing at scratch the validator then removed (2026-11-12), an acceptance command whose recorded arguments FO had to reproduce exactly (2026-11-12), and a log of rerun commands in a shell fence that the Captain-steps reader counted as nine unrecorded steps (2026-11-13, PR 861); each cost a follow-up message or a rerun.
- Upstream first, open for the design: what the delivery check, the validation skill text and the listed extensions already do for this, and whether a smaller change to one of them is enough.
- Non-goals: to be set at ideation.

## Budget
1 implementation and 2 validation cycles, in one package PR.

## Stop condition
- A validation report written from the candidate text passes the Captain-steps check on its first run in a replay of the three recorded cases.

## FO alignment

Alignment: not needed before ideation: an observed friction with counts; the mechanism is compared in the design.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
