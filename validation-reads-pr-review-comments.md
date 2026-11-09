---
title: Validation answers whether the Captain can merge the PR, so it reads every review comment at its head unprompted
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:validation-reads-pr-review-comments:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:validation-reads-pr-review-comments-backlog-1
              briefing:
                id: briefing:validation-reads-pr-review-comments:backlog:attempt-1:revision-1
                digest: sha256:b3fcb4f81dc95178b54aff527f54955265853d3fedb986ba562155e31f9c00a5
                room-ref: ./validation-reads-pr-review-comments/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:validation-reads-pr-review-comments:backlog:1
                briefing: briefing:validation-reads-pr-review-comments:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-09T04:57:33.377666Z"
                decision: approve
                reason: 'The Captain chose 「核准（建議）」 (host question dialog, 2026-11-09), answering 「決定：第 18 批這四張（驗證回答 Captain 能不能合併並因此主動讀完審查意見、合併檢查不再把網址和資料區塊當成檔案和指令、合併提問紀錄能證明檢查在提問前跑、數字寫明是哪次執行算出來的並涵蓋 learn 證據）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構想嗎？建議核准。核准即接受四張任務檔現在寫下的內容；要改哪張直接說。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: pending
---

## Scope

- Framing: the Captain 「可以改寫」 (chat, 2026-11-09), answering FO's 「我的建議：第 18 批照原本的五張做，但把第 2 張「驗證必須讀過 PR 意見」改成「驗證回答能不能合併」來寫，這就是第一次實測第 2 種想法。下一批再做「交給工具寫」那一組。這樣到第 19 批結束時，就能用觀察者的違規數字比較，看錯誤有沒有真的變少。」 and 「你決定第 18 批第 2 張要不要改寫」. The validation stage owns the question "can the Captain merge this PR at this head?" rather than a checklist; reading every review comment then follows from the question, not from a new rule.
- Source: the Captain 「驗證不讀 PR 審查意見（建議）, 特別角色派工紀錄手寫（建議）, 改驗收條件沒當下檢查（建議）, 合併檢查時間點看不出（建議）」 (host question dialog, 2026-11-08), answering 「批次 17 觀察者找到的問題，哪些要開成 kc-dev-flow-2 套件問題單（排進下一批的待辦）？建議四張都開，每張都真的發生過。」
- Bite: PR #812 validation-3 passed at 778367add while Codex review comment 4505793059 (P2, posted 09:54Z the same day) stood unread; FO found it at the gate and a fourth repair and validation round followed (batch 17 archive, dispatch-build-writes-the-dispatch-record).
- Non-goals: changing Spacedock; adopter AGENTS.md files.

## Budget
- One package PR; workflow word budget unchanged unless the design names a raise for the Captain.

## Stop condition
- The validation skill states the merge-readiness question, and a replay of the #812 validation-3 situation (an unaddressed review comment on the PR at the candidate head, no instruction to read comments) finds the comment more often with the reframed skill than with the current one, counted per host.

## FO alignment

Alignment: not needed; the Captain chose to file it from the batch 17 observer findings.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
