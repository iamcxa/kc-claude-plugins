---
title: A declined review finding becomes a backlog task only when it has a bite and a consumer; otherwise its reason in the gate summary is the whole record
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:decline-becomes-task-only-with-a-bite:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:decline-becomes-task-only-with-a-bite-backlog-1
              briefing:
                id: briefing:decline-becomes-task-only-with-a-bite:backlog:attempt-1:revision-1
                digest: sha256:310bad8e688ad065c098e7762a9285b784159492db852aa00ef21ba8d5c340f8
                room-ref: ./decline-becomes-task-only-with-a-bite/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:decline-becomes-task-only-with-a-bite:backlog:1
                briefing: briefing:decline-becomes-task-only-with-a-bite:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-06T14:29:09.46397Z"
                decision: approve
                reason: 'The Captain chose 「核准（建議）」 (host question dialog, 2026-11-06), answering 「決定：第 16 批這五張（跳過的 CI 不擋、Codex 只貼安全摘要時提醒、交付檢查的相對路徑、ADR 編號跨流程預留、婉拒只在出過事時開任務）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構想嗎？核准即接受「婉拒只在出過事時開任務」任務裡寫的標準（指出真的錯並說得出誰受害、再次出現、或你要求）。要改哪張直接說。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: consumed
---

The README's review-finding rule that files every round-3 decline as a new backlog task is replaced: a declined finding keeps its bracketed reason in the gate summary, and becomes a task only when it meets the same bite-and-consumer bar as any other backlog task, or when a later round or task hits it again.

## Scope

- Source: the Captain 「可以，但是該怎樣紀錄合理的followup」 (chat, 2026-11-05), answering 「這張擱置，改開「刪掉第三輪婉拒要開待辦」的小任務，好嗎？」, at the batch 14 ideation gate of gate-summary-names-each-decline (held).
- Bite: of 20 archived follow-up tasks filed from declined findings in this workflow, 2 were built (followup-dispatch-records-checked, read-adr-reporting-rule-followup; each named an observed failure in real records) and 18 were closed together on 2026-10-20 (「照建議關掉 19 張。」), most as already done on main by other work; 11 more sit in backlog untouched since 2026-10-13 to 2026-10-23 (FO count over `_archive/*` and the backlog, 2026-11-05). Observers recorded 3 violations of the file-a-task rule in batches 12 and 13 (9 across all archives).
- Proposed bar (FO's answer to his question, for this task's backlog gate): a declined finding stays as `Declined: <finding> [<reason>]` in the gate summary (held since 2026-10-19 by delivery_gate.py); it becomes a task when (a) it names an observed failure, not a hypothetical one, and who is hurt, (b) a later review round or another task hits the same finding again (the README already names reuse of an existing task on a repeat), or (c) the Captain asks.
- Upstream first: README FO steps: review findings, step 5; delivery_gate.py decline parsing (bracket rule, count join); the observer's check of step 5.
- Non-goals: the three holds designed in gate-summary-names-each-decline; retiring the 11 open follow-up tasks (a separate question for the Captain).

- Batch 16: the Captain 「可以，就這樣」 (chat, 2026-11-06), answering 「這批做 2、3、4、5、9 這 5 張，可以嗎？」, which named this task.

## Budget
- One package PR; the workflow word budget does not rise.

## Stop condition
- README step 5 no longer requires a new backlog task for every round-3 decline and states the bar above; the observer no longer reports a decline without a task as a violation when its reason is written; a replay of the 3 batch 12 and 13 violations reads as compliant.

## FO alignment

Alignment: needed at backlog; the bar is his to accept.
Result: aligned at backlog: Batch 16 backlog gate, the Captain 「核准（建議）」 (host question dialog, 2026-11-06), answering 「決定：第 16 批這五張（跳過的 CI 不擋、Codex 只貼安全摘要時提醒、交付檢查的相對路徑、ADR 編號跨流程預留、婉拒只在出過事時開任務）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構想嗎？核准即接受「婉拒只在出過事時開任務」任務裡寫的標準（指出真的錯並說得出誰受害、再次出現、或你要求）。要改哪張直接說。」, approved the outcome and bounds in this file.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
