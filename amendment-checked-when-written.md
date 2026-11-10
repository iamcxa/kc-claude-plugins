---
title: A Captain amendment and its criterion moves are checked when they are written
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:amendment-checked-when-written:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:amendment-checked-when-written-backlog-1
              briefing:
                id: briefing:amendment-checked-when-written:backlog:attempt-1:revision-1
                digest: sha256:17cac53f2cf9b87b8e7dcfa96b76ccd0403e813e5c7e2223edf1bc2b7f0c4345
                room-ref: ./amendment-checked-when-written/review/backlog/briefing-1
---

## Scope

- Source: the Captain 「驗證不讀 PR 審查意見（建議）, 特別角色派工紀錄手寫（建議）, 改驗收條件沒當下檢查（建議）, 合併檢查時間點看不出（建議）」 (host question dialog, 2026-11-08), answering 「批次 17 觀察者找到的問題，哪些要開成 kc-dev-flow-2 套件問題單（排進下一批的待辦）？建議四張都開，每張都真的發生過。」
- Bite: the batch 17 observer for worker-browser-checks-use-paseo-browser recorded that FO rewrote AC-1, AC-2 and AC-4 in place under reused ids (state a113aa3e9); design_surfaces.py caught it only when the implementation worker ran it.
- Non-goals: changing Spacedock; adopter AGENTS.md files.

## Budget
- One package PR; workflow word budget unchanged unless the design names a raise for the Captain.

## Stop condition
- Committing a task whose amendment reuses an id or lacks the 'Amended by Captain, amendment N' marker is refused or flagged at that commit, with a falsifier.

## FO alignment

Alignment: not needed; the Captain chose to file it from the batch 17 observer findings.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
