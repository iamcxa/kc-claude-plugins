---
title: Special-role dispatch records are written by the package dispatch script
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:special-role-dispatch-records-built-by-script:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:special-role-dispatch-records-built-by-script-backlog-1
              briefing:
                id: briefing:special-role-dispatch-records-built-by-script:backlog:attempt-1:revision-1
                digest: sha256:d7ebcd15eea1d4a7bc3c69a6ea725ed24e54d7c5aac3e2c9bcc5d7aa128923f7
                room-ref: ./special-role-dispatch-records-built-by-script/review/backlog/briefing-1
---

## Scope

- Source: the Captain 「驗證不讀 PR 審查意見（建議）, 特別角色派工紀錄手寫（建議）, 改驗收條件沒當下檢查（建議）, 合併檢查時間點看不出（建議）」 (host question dialog, 2026-11-08), answering 「批次 17 觀察者找到的問題，哪些要開成 kc-dev-flow-2 套件問題單（排進下一批的待辦）？建議四張都開，每張都真的發生過。」
- Bite: the batch 17 observer for worker-browser-checks-use-paseo-browser recorded a violation: FO hand-wrote dispatch/engineering-reviewer-1.md without the record fields; dispatch_records.py exited 1 on it until validation-2 reported it (state commits a113aa3e9, cc856a639).
- Non-goals: changing Spacedock; adopter AGENTS.md files.

## Budget
- One package PR; workflow word budget unchanged unless the design names a raise for the Captain.

## Stop condition
- An engineering-reviewer or chief-engineer dispatch made through the package writes a complete record before the agent starts, with a falsifier.

## FO alignment

Alignment: not needed; the Captain chose to file it from the batch 17 observer findings.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
