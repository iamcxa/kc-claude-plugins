# 0077. A task budget counts cycles and past it the question returns to the Captain

Date: 2026-11-11

## Status

Accepted

## Context

The relay task comment-sent-when-added-relay ran six implementation cycles under
"One cycle per stage." Its recorded implementation-2 at `42317d0c` preceded the
four-repair-pass chief-engineer event at `d85ce152`. The approved design's replay
found that the reload recovery was already in the accepted criteria: another
finding-ownership rule would have accepted those repairs too. The Captain folded
the first-principles task into the budget task, keeping prior-art research separate.

## Decision

**Words:** 「照建議核准（建議）」 — Captain, host question dialog, 2026-11-11,
ideation gate attempt 2 of budget-overrun-holds-and-findings-meet-non-goals.

**Asked:** 「決定：要不要核准「預算是什麼」（已併入第一性原理）的設計並開始實作。我建議照設計的建議核准：預算改用可數的輪數寫，新任務必須用這個寫法；每次實作與驗證派工顯示預算和已花幾輪，第一次超過就停下來，由我帶著三個「值不值得」的問題的答案來問你；同樣三題在每份設計裡必答，檢查會擋缺漏；原本的退一步提醒對這類任務取消，不另外加重大發現的規則。核准即接受這三項；它的代價是你會被問得比現在多。」

The prior amendments were 「重寫，並把兩張原則任務拉進這批」 and
「前兩張合併，查現成做法獨立（建議）」, both host question dialogs on 2026-11-11;
their verbatim bound questions remain in the task's Captain amendments 1 and 2.

**Options considered:**
- Hold at the first implementation or validation cycle past the countable bound;
  require fixed cycle forms on new seeds; force the same worth questions at
  ideation and the hold, replacing the advisory reminder for countable budgets
  (chosen: D1, D2 and D3).
- Print spent cycles without holding, or hold at cycle three: the first lets the
  budget go unread; the second permits an extra unapproved cycle.
- Parse free budget prose, or add a separate Material-finding event: the former
  depends on phrases; the latter misses scope that already grew at ideation.

**Recommended:** D1, D2 and D3 as the ideation gate recommended and the Captain approved.

**Protects:**
- `kc-dev-flow-2/scripts/role_triggers.py` — fixed bounds, amendment authority, budget hold and advisory suppression
- `kc-dev-flow-2/scripts/dispatch_stage.py` — saved Budget header and forwarded budget output
- `kc-dev-flow-2/scripts/design_surfaces.py` — countable seed bound and Worth questions section

A budget states how many worker cycles the Captain considers worth the outcome.
New seeds use `N cycles per stage` or `N implementation and M validation cycles`,
with digits or English one to ten. Implementation and validation show the budget
and highest plain dispatch number per stage, including the pending dispatch.
The first overrun holds until a Captain amendment's `Budget:` value covers it;
that value must occur verbatim in that entry's `Asked:` or `Captain:` line.
A stop, known limit or split produces no further dispatch. A task whose first
saved stage record has no Budget header is exempt from the budget hold. Other
budget prose remains visible but uncounted.

Each ideation design answers, per scope part: which Captain words it serves,
what breaks without it, and which single premise would make it unneeded with a
cheap test now. The budget hold brings those answers back to the Captain.
For countable budgets the advisory step-back reminder is removed; existing
chief-engineer and engineering-reviewer events and clearing rules remain.
Their shared question text becomes the worth questions. No separate Material
finding rule or self-answered record is added. This amends ADR 0026's reminder.

## Consequences

New budgets require a deliberate bound and can return more questions to the
Captain. Checks establish a section and verbatim bound, not the truth or value
of an answer. Days, lines of code and ideation cycles are not counted. Adopters
receive the behavior when they update the package and workflow; old records
remain exempt. Reopen if a supported dispatch route fails to show spent cycles
or if countable fixed forms cannot express an approved outcome's bound.
