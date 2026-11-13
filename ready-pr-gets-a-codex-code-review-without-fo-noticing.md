---
title: A PR marked ready gets its Codex code review without FO noticing a security-only pass by hand
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
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
              withdrawal:
                by: agent:first-officer
                at: "2026-11-13T13:42:01.503467Z"
                reason: The Captain answered the first question with a question about model and effort instead of a decision (chat, 2026-11-13); FO asked again with the build strength in the question, and that second question is the one he answered.
            - id: gate-attempt:ready-pr-gets-a-codex-code-review-without-fo-noticing-backlog-2
              briefing:
                id: briefing:ready-pr-gets-a-codex-code-review-without-fo-noticing:backlog:attempt-2:revision-1
                digest: sha256:2d5e803415b5053ec61bc21c8892c0ebd26c7ee9419e19cb563744f8ae4ac881
                room-ref: ./ready-pr-gets-a-codex-code-review-without-fo-noticing/review/backlog/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:ready-pr-gets-a-codex-code-review-without-fo-noticing:backlog:2
                briefing: briefing:ready-pr-gets-a-codex-code-review-without-fo-noticing:backlog:attempt-2:revision-1
                by: person:captain
                at: "2026-11-13T13:42:08.597392Z"
                decision: approve
                reason: 'The Captain answered 「一張維持，一張推理降一級，一張模型降低一級，但是 xhigh 推理」 (chat, 2026-11-13), answering 「三張「合併前那一段」的任務要不要進設計，以及實作用什麼強度？ 三張內容同剛才那一題：合併提問摘要自動產生、標成可審查後自動觸發 Codex 審查、驗證者留下的東西能直接過合併檢查。預算各 1 implementation and 2 validation cycles。符合常設授權條件，設計關卡沒踩停止條件時由我代記，合併每張問你。第一張和第三張會動到同一支程式，排先後。」; admits the three tasks with outcome, scope and Budget as seeded, and sets the build worker''s strength per task: one unchanged, one with effort one step lower, one with the model one tier lower at xhigh. Override: recommended two tasks one effort step lower and one unchanged; Captain chose one unchanged, one effort step lower and one model tier lower at xhigh; area: build model and effort.'
              application:
                target-stage: ideation
                state: consumed
started: 2026-11-13T13:42:51Z
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
