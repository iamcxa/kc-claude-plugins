---
title: The merge-ask record proves the delivery check ran before the question was presented
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
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
