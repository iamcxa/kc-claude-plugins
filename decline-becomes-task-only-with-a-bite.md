---
title: A declined review finding becomes a backlog task only when it has a bite and a consumer; otherwise its reason in the gate summary is the whole record
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

The README's review-finding rule that files every round-3 decline as a new backlog task is replaced: a declined finding keeps its bracketed reason in the gate summary, and becomes a task only when it meets the same bite-and-consumer bar as any other backlog task, or when a later round or task hits it again.

## Scope

- Source: the Captain 「可以，但是該怎樣紀錄合理的followup」 (chat, 2026-11-05), answering 「這張擱置，改開「刪掉第三輪婉拒要開待辦」的小任務，好嗎？」, at the batch 14 ideation gate of gate-summary-names-each-decline (held).
- Bite: of 20 archived follow-up tasks filed from declined findings in this workflow, 2 were built (followup-dispatch-records-checked, read-adr-reporting-rule-followup; each named an observed failure in real records) and 18 were closed together on 2026-10-20 (「照建議關掉 19 張。」), most as already done on main by other work; 11 more sit in backlog untouched since 2026-10-13 to 2026-10-23 (FO count over `_archive/*` and the backlog, 2026-11-05). Observers recorded 3 violations of the file-a-task rule in batches 12 and 13 (9 across all archives).
- Proposed bar (FO's answer to his question, for this task's backlog gate): a declined finding stays as `Declined: <finding> [<reason>]` in the gate summary (held since 2026-10-19 by delivery_gate.py); it becomes a task when (a) it names an observed failure, not a hypothetical one, and who is hurt, (b) a later review round or another task hits the same finding again (the README already names reuse of an existing task on a repeat), or (c) the Captain asks.
- Upstream first: README FO steps: review findings, step 5; delivery_gate.py decline parsing (bracket rule, count join); the observer's check of step 5.
- Non-goals: the three holds designed in gate-summary-names-each-decline; retiring the 11 open follow-up tasks (a separate question for the Captain).

## Budget
- One package PR; the workflow word budget does not rise.

## Stop condition
- README step 5 no longer requires a new backlog task for every round-3 decline and states the bar above; the observer no longer reports a decline without a task as a violation when its reason is written; a replay of the 3 batch 12 and 13 violations reads as compliant.

## FO alignment

Alignment: needed at backlog; the bar is his to accept.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
