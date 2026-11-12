---
title: design_surfaces.py check <task> crashes when a same-named task directory sits beside the task file
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:design-surfaces-task-dir-crash:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:design-surfaces-task-dir-crash-backlog-1
              briefing:
                id: briefing:design-surfaces-task-dir-crash:backlog:attempt-1:revision-1
                digest: sha256:5fd3d071be50b4b72b9178559fd58dc9ef467da5a0d99826887575d556fd8e60
                room-ref: ./design-surfaces-task-dir-crash/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:design-surfaces-task-dir-crash:backlog:1
                briefing: briefing:design-surfaces-task-dir-crash:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-12T17:01:18.104672Z"
                decision: approve
                reason: The Captain chose 「五張都准，授權代記設計關卡（建議）」 (host question dialog, 2026-11-13), answering 「獨立審查說原本的合約不能直接跑，我已照它修正（設計關卡保留、Prod 不動、每張最多 3 輪實作）。要不要用下面五張小任務開始試跑，並授權我在第一輪沒踩到停止條件時，代你記錄設計關卡通過？五張：①做新東西前先查既有的（你的首要方向，預期第一輪後會停下來問你）②設計檢查腳本遇到同名資料夾會當掉 ③合併檢查不該要求已刪除的暫存路徑 ④沒啟用學習擴充的專案不該被叫去跑學習 ⑤PR 監看不該對別台機器的任務提示。預算每張：1 implementation and 2 validation cycles。」; accepts outcome, scope and Budget as seeded and the trial route rules.
              application:
                target-stage: ideation
                state: consumed
started: 2026-11-12T17:02:31Z
---

Filed from a package issue reported by the spacedock-dev/subspace-relay First Officer (found by its implementation worker on 2026-10-13); the Captain confirmed filing on 2026-10-14 (「確認」 to "should FO file relay #1 and #4?").

## Scope

- Reproduced 2026-10-14 on kc-dev-flow-2 0.22.1: from the state checkout root, `python3 <package>/scripts/design_surfaces.py check followup-dispatch-records-checked` raises `IsADirectoryError: [Errno 21] Is a directory: 'followup-dispatch-records-checked'`; the same command with `followup-dispatch-records-checked.md` works. Every task with dispatch records has a `<task>/` directory beside `<task>.md`, and the workflow README tells FO and workers to run `design_surfaces.py check <task>` and `check --seed <task>`.
- Candidate fix: resolve `<task>` to `<task>.md` when the argument is a directory or has no suffix, or fail with a usage message; a test for the directory case.
- Non-goals: to be set at ideation.
- Trial (2026-11-13): admitted by the Captain's 「五張都准，授權代記設計關卡（建議）」 (host question dialog, 2026-11-13) as one of five tasks run by hand under the trial route rules: one worker builds a working probe during ideation and continues into implementation, a different worker validates, at most 3 build rounds counted by hand; stop for the Captain on an overturned premise, spent budget, two rounds without progress or a second validation rejection, a change of scope or criterion, or a component boundary or Prod trigger.

## Acceptance criteria

To be written at ideation.

## Budget
1 implementation and 2 validation cycles, in one package PR.

## Stop condition
- The recorded command, run from a state checkout root where a same-named directory sits beside the task file, no longer raises IsADirectoryError and checks the task file; a test covers the directory case.

## FO alignment

Alignment: not needed before ideation; the Captain confirmed filing it.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
