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

**Words, Captain amendment 3:** 「加總次數和停止句，分鐘另談（建議）」 (host question dialog, 2026-11-11); before it he asked 「現在預算會長得像這樣，對嗎？『240 累計代理分鐘、最多 5 次派工，含一輪修正。並行代理各自計入，人工與平台等待另記；任一上限到達，就保留成果、回報剩餘工作並停止加碼。』」 (host question dialog, 2026-11-11)

**Asked:** 「預算的寫法要不要照你的例子擴大？目前核准的設計只認「每階段幾輪」兩種寫法，實作工人已在做。我建議：這一張先加上「派工總次數上限」這種寫法，並把「到上限就保留成果、回報剩餘工作並停止加碼」當成停下來時的預設結果；「累計代理分鐘」因為現在沒有可靠的時間來源，另外記成一張要先查證的任務，不塞進這張。」

**Words, Captain amendment 4:** 「兩處都同意（建議）」 (host question dialog, 2026-11-11)

**Asked:** 「「預算」這張任務的實作停在兩處等更正，要不要都同意？一、第七項驗收條件把三個值不值得的問題寫成放進「待辦關卡」，更正為你核准的「設計關卡」，待辦關卡只呈現預算。二、允許多改兩個設計沒列的測試檔（pr_watch 和 delivery_gate 的測試），只更新 4 處還在比對舊版退一步提醒文字的預期值，產品程式不動。我建議兩處都同意。」

**Words, Captain amendment 5:** 「只算修正的訊息（建議）」 (host question dialog, 2026-11-11)

**Asked:** 「預算的「派工總次數上限」裡，我在同一個階段追加給工人的訊息要怎麼算？我建議：只有要工人回去修東西的訊息（紀錄上有寫問題名稱的）算一次派工，回答工人提問或轉達你裁示的訊息不算。以「發版鋪開」為例，這樣是 7 次；每則都算是 11 次，都不算是 2 次。」

**Options considered:**
- Hold at the first implementation or validation cycle past the countable bound;
  require fixed cycle forms on new seeds; force the same worth questions at
  ideation and the hold, replacing the advisory reminder for countable budgets
  (chosen: D1, D2 and D3).
- Print spent cycles without holding, or hold at cycle three: the first lets the
  budget go unread; the second permits an extra unapproved cycle.
- Parse free budget prose, or add a separate Material-finding event: the former
  depends on phrases; the latter misses scope that already grew at ideation.

**Recommended:** D1, D2 and D3 as the ideation gate recommended, plus the total-dispatch form, default hold outcome and gate/test corrections in Captain amendments 3 and 4, and the named-symptom message rule in amendment 5.

**Protects:**
- `kc-dev-flow-2/scripts/role_triggers.py` — fixed bounds, amendment authority, budget hold and advisory suppression
- `kc-dev-flow-2/scripts/dispatch_stage.py` — saved Budget header and forwarded budget output
- `kc-dev-flow-2/scripts/design_surfaces.py` — countable seed bound and Worth questions section

A budget states how many worker cycles the Captain considers worth the outcome.
New seeds use `N cycles per stage` or `N implementation and M validation cycles`,
with digits or English one to ten. The total-dispatch form is `at most N dispatches total` (singular `dispatch` too), or `最多 N 次派工` with digits. An explicit numeric agent-minutes clause may precede the countable part, separated by a comma or semicolon (Chinese punctuation too); minutes are printed as uncounted. Implementation and validation show the budget
and highest plain dispatch number per stage, including the pending dispatch.
The total-dispatch cap counts the saved ideation, implementation and validation stage records once. A follow-up message counts when its out-of-fence header names a symptom; normalized none, empty or absent headers do not name one and do not count. Body lines and fenced examples do not supply a header. Special-role records are excluded. `budget_dispatches` owns this counting rule; the pending overlay replaces an existing record of the same name, avoiding double counting. The first overrun holds until a Captain amendment's `Budget:` value covers it;
that value must occur verbatim in that entry's `Asked:` or `Captain:` line.
The default hold outcome is to keep the results, report the remaining work and stop adding, unless the Captain replaces it. A stop, known limit or split produces no further dispatch. A task whose first
saved stage record has no Budget header is exempt from the budget hold. Other
budget prose remains visible but uncounted.

Each ideation design answers, per scope part: which Captain words it serves,
what breaks without it, and which single premise would make it unneeded with a
cheap test now. The ideation gate shows those answers; backlog shows the Budget. The budget hold brings the answers back to the Captain.
For countable budgets the advisory step-back reminder is removed; existing
chief-engineer and engineering-reviewer events and clearing rules remain.
Their shared question text becomes the worth questions. No separate Material
finding rule or self-answered record is added. This amends ADR 0026's reminder.

## Consequences

New budgets require a deliberate bound and can return more questions to the
Captain. Checks establish a section and verbatim bound, not the truth or value
of an answer. Agent minutes, days and lines of code are not counted; the original per-stage forms count implementation and validation cycles. Adopters
receive the behavior when they update the package and workflow; old records
remain exempt. Reopen if a supported dispatch route fails to show spent cycles
or if countable fixed forms cannot express an approved outcome's bound.
