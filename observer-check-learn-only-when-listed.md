---
title: observer_check prints the learn steps only where the workflow README lists learn
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:observer-check-learn-only-when-listed:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:observer-check-learn-only-when-listed-backlog-1
              briefing:
                id: briefing:observer-check-learn-only-when-listed:backlog:attempt-1:revision-1
                digest: sha256:2e471176de0b419ffc5d393f3ba3755feef99997b9b34deea05f5ccaec0c84a1
                room-ref: ./observer-check-learn-only-when-listed/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:observer-check-learn-only-when-listed:backlog:1
                briefing: briefing:observer-check-learn-only-when-listed:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-12T17:01:48.112583Z"
                decision: approve
                reason: The Captain chose 「五張都准，授權代記設計關卡（建議）」 (host question dialog, 2026-11-13), answering 「獨立審查說原本的合約不能直接跑，我已照它修正（設計關卡保留、Prod 不動、每張最多 3 輪實作）。要不要用下面五張小任務開始試跑，並授權我在第一輪沒踩到停止條件時，代你記錄設計關卡通過？五張：①做新東西前先查既有的（你的首要方向，預期第一輪後會停下來問你）②設計檢查腳本遇到同名資料夾會當掉 ③合併檢查不該要求已刪除的暫存路徑 ④沒啟用學習擴充的專案不該被叫去跑學習 ⑤PR 監看不該對別台機器的任務提示。預算每張：1 implementation and 2 validation cycles。」; accepts outcome, scope and Budget as seeded and the trial route rules.
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: intake from the subspace-web/v0 dev2 FO (Paseo agent 295b873d, 2026-10-21), relaying the Captain's 「開給 dev2 ，可以先送給這個 fo  2e87a82e-a8a9-4e41-973a-7483aa46e39d」 (relayed, not a ruling in this session).
- Bite: subspace-v0's dev2 README has no `extensions:` and never mentions learn; `learning.py notices --all` there is empty. After archiving task first-publish-reads-right, `observer_check.py` still told FO to run learn and to send learn's notice.
- Verified 2026-10-21 in kc-dev-flow-2 0.27.0 `scripts/observer_check.py`: the `learn` step list ("next: run kc-dev-flow-2:learn for {slug}.", "next: send learn's notice, then the observer report unedited…") is appended whenever the task is archived, with no read of the README's `extensions:`; `extensions/learn/EXTENSION.md` says a repository uses learn "by listing `learn` under `extensions:`".
- Shape proposed by the relaying FO (its wording, not the Captain's): when the README does not list `learn`, print no learn steps, or say learn is not enabled here.
- Related: adoption-asks-which-extensions (adoption never asks which extensions to enable).
- Upstream first: `observer_check.py` and its tests; how other scripts already read `extensions:` (dispatch_records.py).
- Non-goals: to be set at ideation.
- Trial (2026-11-13): admitted by the Captain's 「五張都准，授權代記設計關卡（建議）」 (host question dialog, 2026-11-13) as one of five tasks run by hand under the trial route rules: one worker builds a working probe during ideation and continues into implementation, a different worker validates, at most 3 build rounds counted by hand; stop for the Captain on an overturned premise, spent budget, two rounds without progress or a second validation rejection, a change of scope or criterion, or a component boundary or Prod trigger.

## Budget
1 implementation and 2 validation cycles, in one package PR.

## Stop condition
- On a workflow README that does not list learn under `extensions:`, the script prints no learn step for an archived task; on one that lists it, the steps print as today.

## FO alignment

Alignment: not needed before ideation.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
