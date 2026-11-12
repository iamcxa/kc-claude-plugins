---
title: The merge check does not demand paths a validation report names as removed scratch
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:delivery-gate-s4-skips-removed-scratch:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:delivery-gate-s4-skips-removed-scratch-backlog-1
              briefing:
                id: briefing:delivery-gate-s4-skips-removed-scratch:backlog:attempt-1:revision-1
                digest: sha256:dffe6f989ba6fbb0df866814f05cfd60e70bad098a6f0d15faa3e783f75f38b5
                room-ref: ./delivery-gate-s4-skips-removed-scratch/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:delivery-gate-s4-skips-removed-scratch:backlog:1
                briefing: briefing:delivery-gate-s4-skips-removed-scratch:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-12T17:01:38.316509Z"
                decision: approve
                reason: The Captain chose 「五張都准，授權代記設計關卡（建議）」 (host question dialog, 2026-11-13), answering 「獨立審查說原本的合約不能直接跑，我已照它修正（設計關卡保留、Prod 不動、每張最多 3 輪實作）。要不要用下面五張小任務開始試跑，並授權我在第一輪沒踩到停止條件時，代你記錄設計關卡通過？五張：①做新東西前先查既有的（你的首要方向，預期第一輪後會停下來問你）②設計檢查腳本遇到同名資料夾會當掉 ③合併檢查不該要求已刪除的暫存路徑 ④沒啟用學習擴充的專案不該被叫去跑學習 ⑤PR 監看不該對別台機器的任務提示。預算每張：1 implementation and 2 validation cycles。」; accepts outcome, scope and Budget as seeded and the trial route rules.
              application:
                target-stage: ideation
                state: consumed
started: 2026-11-12T17:03:37Z
---

## Scope

- Source: the qnow dev2 FO, sent with the Captain's approval 「送出」 (2026-11-10), and FO's own case in batch 19 (a validation report citing evidence under a /tmp folder that macOS may clear).
- Bite: on qnow owner-vehicle-kept-after-name (adopted 0.35.0 scripts, run 2026-11-09 ~15:40 UTC), `delivery_gate.py question` and `check` printed `Captain steps record fails: message S4: missing path /tmp/ovk-val4-wt` and held, because inspect_steps runs the absolute-path existence check (S4) over the gate text plus the latest validation report, and the report's cleanup bullet says the validator removed that scratch worktree as told; `delivery_gate.py steps` on the record itself exited 0. The only pass is recreating the folder, which games the check. State: qnow spacedock-state/dev2 at 5e3a5110, `_archive/owner-vehicle-kept-after-name.md` last validation report and `owner-vehicle-kept-after-name/delivery-gate-text.md`.
- Suggested direction (qnow FO, not a ruling): exclude paths the report states were removed, or scope S4 to the gate text and the steps record.
- Non-goals: dropping S4 for the gate text or the steps record.
- Trial (2026-11-13): admitted by the Captain's 「五張都准，授權代記設計關卡（建議）」 (host question dialog, 2026-11-13) as one of five tasks run by hand under the trial route rules: one worker builds a working probe during ideation and continues into implementation, a different worker validates, at most 3 build rounds counted by hand; stop for the Captain on an overturned premise, spent budget, two rounds without progress or a second validation rejection, a change of scope or criterion, or a component boundary or Prod trigger.

## Budget
1 implementation and 2 validation cycles, in one package PR to delivery_gate.py and its tests.

## Stop condition
- The qnow input above passes S4 while a missing path the Captain is asked to run still holds.

## FO alignment

Alignment: needed at ideation; which paths S4 reads is the Captain's call.
Result: the Captain admitted this task into the route trial with 「五張都准，授權代記設計關卡（建議）」 (host question dialog, 2026-11-13); he has not yet ruled which paths the check reads, so FO does not record this task's ideation gate under the grant: the probe's result and the options go to him at that gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
