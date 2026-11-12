---
title: pr_watch.py tasks prints record-PR next lines for tasks whose worktree is not on this machine
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:pr-watch-tasks-foreign-worktree:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:pr-watch-tasks-foreign-worktree-backlog-1
              briefing:
                id: briefing:pr-watch-tasks-foreign-worktree:backlog:attempt-1:revision-1
                digest: sha256:5783c0be460d444e9682a84792d956f027e99a56ec1d28917b381361e2972a80
                room-ref: ./pr-watch-tasks-foreign-worktree/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:pr-watch-tasks-foreign-worktree:backlog:1
                briefing: briefing:pr-watch-tasks-foreign-worktree:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-12T17:01:58.054817Z"
                decision: approve
                reason: The Captain chose 「五張都准，授權代記設計關卡（建議）」 (host question dialog, 2026-11-13), answering 「獨立審查說原本的合約不能直接跑，我已照它修正（設計關卡保留、Prod 不動、每張最多 3 輪實作）。要不要用下面五張小任務開始試跑，並授權我在第一輪沒踩到停止條件時，代你記錄設計關卡通過？五張：①做新東西前先查既有的（你的首要方向，預期第一輪後會停下來問你）②設計檢查腳本遇到同名資料夾會當掉 ③合併檢查不該要求已刪除的暫存路徑 ④沒啟用學習擴充的專案不該被叫去跑學習 ⑤PR 監看不該對別台機器的任務提示。預算每張：1 implementation and 2 validation cycles。」; accepts outcome, scope and Budget as seeded and the trial route rules.
              application:
                target-stage: ideation
                state: consumed
started: 2026-11-12T17:03:02Z
---

Filed on the Captain's 「開」 (chat, 2026-10-16), after FO's first run of the v0.23.0 lifecycle mod's idle step on this workflow.

## Scope

- Observed 2026-10-16, kc-dev-flow-2 0.23.0, `python3 <package>/scripts/pr_watch.py tasks <workflow dir>` on this workflow printed two `next:` lines: "record journey-server-host-pilot's PR with status --set journey-server-host-pilot pr=<owner/repo>#<N>; its worktree is not on this machine." and the same for pr-review-lite-value-pilot. Neither task is driven by the session that ran the mod (one is held at validation by another session, the other unchanged since 2026-09-22), and neither has a PR yet.
- The mod tells FO to do each `next:` line in order, so an FO that follows it may record a wrong PR on another session's task. Several FO sessions drive one workflow in adopters such as subspace-relay.
- Candidate fix: a task whose worktree is not on this machine is listed as a fact line, not a `next:` action; a test with such a task.
- Should land before subspace-relay syncs to the mod.
- Also seen 2026-10-16 on the same run: `next: run spacedock state commit amendment-form-check` while that task's implementation worker was still writing its report (the worker owns that commit), and `next: mark #649 ready if Delivery authority allows` before its validation had run. Both are `next:` lines an FO must not follow at that moment; whether they become facts too is for ideation.
- Non-goals: to be set at ideation.
- Trial (2026-11-13): admitted by the Captain's 「五張都准，授權代記設計關卡（建議）」 (host question dialog, 2026-11-13) as one of five tasks run by hand under the trial route rules: one worker builds a working probe during ideation and continues into implementation, a different worker validates, at most 3 build rounds counted by hand; stop for the Captain on an overturned premise, spent budget, two rounds without progress or a second validation rejection, a change of scope or criterion, or a component boundary or Prod trigger.

## Budget
1 implementation and 2 validation cycles, in one package PR.

## Stop condition
- A task whose worktree is not on this machine produces no `next:` line telling FO to record a PR; a test covers such a task. The two other `next:` lines seen on 2026-10-16 are decided in the design, not assumed in scope.

## FO alignment

Alignment: not needed before ideation: one observed defect with a candidate fix; the Captain filed it.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
