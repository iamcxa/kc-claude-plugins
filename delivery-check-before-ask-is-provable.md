---
title: The merge-ask record proves the delivery check ran before the question was presented
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:delivery-check-before-ask-is-provable:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:delivery-check-before-ask-is-provable-backlog-1
              briefing:
                id: briefing:delivery-check-before-ask-is-provable:backlog:attempt-1:revision-1
                digest: sha256:973beb8a677426dcd56bd3e3df4910207d10319e6d04dd19ac1fc708fb8c933a
                room-ref: ./delivery-check-before-ask-is-provable/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:delivery-check-before-ask-is-provable:backlog:1
                briefing: briefing:delivery-check-before-ask-is-provable:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-09T04:57:45.448796Z"
                decision: approve
                reason: 'The Captain chose 「核准（建議）」 (host question dialog, 2026-11-09), answering 「決定：第 18 批這四張（驗證回答 Captain 能不能合併並因此主動讀完審查意見、合併檢查不再把網址和資料區塊當成檔案和指令、合併提問紀錄能證明檢查在提問前跑、數字寫明是哪次執行算出來的並涵蓋 learn 證據）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構想嗎？建議核准。核准即接受四張任務檔現在寫下的內容；要改哪張直接說。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: consumed
started: 2026-11-09T04:59:10Z
---

## Scope

- Source: the Captain 「驗證不讀 PR 審查意見（建議）, 特別角色派工紀錄手寫（建議）, 改驗收條件沒當下檢查（建議）, 合併檢查時間點看不出（建議）」 (host question dialog, 2026-11-08), answering 「批次 17 觀察者找到的問題，哪些要開成 kc-dev-flow-2 套件問題單（排進下一批的待辦）？建議四張都開，每張都真的發生過。」
- Bite: all five batch 17 observers reported can't tell for 'delivery_gate.py check before the merge ask': each merge/ask-N.json postdates its briefing commit, so state cannot show the order.
- Non-goals: changing Spacedock; adopter AGENTS.md files.

## Budget
- One package PR; workflow word budget unchanged unless the design names a raise for the Captain.

## Stop condition
- An observer can tell from state alone whether the delivery check ran before the question was presented, with a falsifier.

## FO alignment

Alignment: not needed; the Captain chose to file it from the batch 17 observer findings.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
