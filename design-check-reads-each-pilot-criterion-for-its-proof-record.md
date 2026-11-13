---
title: The design check holds a Pilot design whose criterion lacks its proof record or a stated reason it cannot be run
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「先做一：把 Pilot 試作補完整，再做二：邊界合約先行」 (chat, 2026-11-13), answering FO's list of four directions, whose first read 「一、把 Pilot 試作補完整｜這版的兩條規則只靠文字：每條驗收條件要記齊、試作最多兩輪｜驗證時兩個測試 worker 一個漏記；顧問明說只有檢查程式擋得住｜兩張小任務，其中一張已在待辦」.
- Bite (validation of PR 864, 2026-11-13): the merged Pilot text asks an ideation worker to run each criterion's proof once and record command, exit and output path; one history-free test worker recorded them for 2 of its 3 criteria, a second for 4 of 4 after a one-sentence rewording, and the investigation could not decide from one run whether wording was the cause. The chief-engineer's read the same day: the requirement is prose only, the design check reads that criteria are declared and not that each carries the three fields, so completeness rests on the worker.
- Outcome: before the design gate, the existing design check refuses a Pilot design in which a criterion has neither a complete record (command, observed exit, retained output path) nor an entry under `Not provable now` naming that criterion and why.
- What exists: `design_surfaces.py check <task>`, run by FO before every ideation gate; the criterion form (bold `AC-N`, evidence clause, falsifier) and the `Not provable now` heading from ADR 0084.
- Open for the design: how a record is recognised without a new required syntax that old tasks fail; whether tasks approved before the change are exempt by date or by profile; what the check does for a criterion whose proof is a document reading and has no command.
- Non-goals: proving that a recorded command was really run or that its output is true; any change to POC or Prod; the round cap (task budget-form-counts-ideation-rounds-and-times-each-round carries it).

## Budget
1 implementation and 2 validation cycles, in one package PR.

## Stop condition
- A replay of the two test workers' designs from PR 864's validation is refused for the one with a missing record and passes the complete one, and no task approved before the change is refused. Return to the Captain if the check needs a new required line in every criterion.

## FO alignment

Alignment: not needed before ideation: his words admit the direction; the recognition rule is ruled at the design gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
