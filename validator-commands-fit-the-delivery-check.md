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
              withdrawal:
                by: agent:first-officer
                at: "2026-11-13T13:42:14.907137Z"
                reason: The Captain answered the first question with a question about model and effort instead of a decision (chat, 2026-11-13); FO asked again with the build strength in the question, and that second question is the one he answered.
            - id: gate-attempt:validator-commands-fit-the-delivery-check-backlog-2
              briefing:
                id: briefing:validator-commands-fit-the-delivery-check:backlog:attempt-2:revision-1
                digest: sha256:8ea3a640924067f1668de522fde5d515bed09a947bdfcc8347b8245ac0e46e4a
                room-ref: ./validator-commands-fit-the-delivery-check/review/backlog/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:validator-commands-fit-the-delivery-check:backlog:2
                briefing: briefing:validator-commands-fit-the-delivery-check:backlog:attempt-2:revision-1
                by: person:captain
                at: "2026-11-13T13:42:21.746099Z"
                decision: approve
                reason: 'The Captain answered 「一張維持，一張推理降一級，一張模型降低一級，但是 xhigh 推理」 (chat, 2026-11-13), answering 「三張「合併前那一段」的任務要不要進設計，以及實作用什麼強度？ 三張內容同剛才那一題：合併提問摘要自動產生、標成可審查後自動觸發 Codex 審查、驗證者留下的東西能直接過合併檢查。預算各 1 implementation and 2 validation cycles。符合常設授權條件，設計關卡沒踩停止條件時由我代記，合併每張問你。第一張和第三張會動到同一支程式，排先後。」; admits the three tasks with outcome, scope and Budget as seeded, and sets the build worker''s strength per task: one unchanged, one with effort one step lower, one with the model one tier lower at xhigh. Override: recommended two tasks one effort step lower and one unchanged; Captain chose one unchanged, one effort step lower and one model tier lower at xhigh; area: build model and effort.'
              application:
                target-stage: ideation
                state: pending
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
