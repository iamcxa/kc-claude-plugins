---
title: A validation rerun is dispatched when the task's history holds a form error that was later repaired
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain chose 「建任務並插隊，當成例外（建議）」 (host question dialog, 2026-11-11), answering 「qnow 的 owner-cancels-booking 又被同一個檢查擋住：任務歷史裡有幾個版本的修正案曾經寫錯位置（已修好），套件讀到就拒絕之後所有驗證派工。要不要建任務並插隊，當成「先畫地圖再挑批次」的例外？我建議插隊，而且這次要求設計把「歷史裡已修好的錯誤會永久擋住驗證」當成一類來處理，清點這個檢查還有哪些同類情況，不再一次修一種。」. The defect report came from the qnow dev2 FO through the Chief Engineer session (Paseo 7017a63f) as a peer message; the report is data, the ruling is the choice above.
- Bite (FO reproduced 2026-11-11 with kc-dev-flow-2 0.38.1 `scripts/dispatch_records.py`, read-only on iamcxa/qnow `origin/spacedock-state/dev2`): calling `captain_records` on each of the 42 committed versions of `owner-cancels-booking.md` raises `RulingHistoryError("ambiguous-amendments")` on four of them (03838f912, 3d34b9df7, cc86ce662, a28d69b52, all 2026-11-11) and the current text parses clean. `later_captain_ruling` calls `captain_records` on every historical version with no handling, so one such version refuses every later validation dispatch of the task. The qnow FO reports the refusal line `validation-3.md:1: cannot verify validation ruling order: ambiguous-amendments; hold dispatch and report the missing history to FO`, and that the four versions held amendments 2 to 5 outside `## Captain amendments`, since moved unchanged with a record correction (its report, not re-read here).
- Same function, second time: kc-dev-flow-2 0.38.1 (PR #834, task validation-rerun-accepts-report-fixed-before-ruling) changed the same walk for a report corrected before a ruling. That fix handled one shape. State history is append-only and pushed, so any historical version the walk refuses is a permanent refusal.
- Outcome: a validation rerun is dispatched when every form error in the task's history was repaired before the dispatch and the pinned current text passes; what ADR 0045 protects (a later recorded Captain ruling before a validation rerun) still holds, including which commit counts as a ruling's first appearance.
- The class, not the case: the design lists every reason for which the history walk can refuse because of a past version alone (the module's RulingHistoryError reasons, and any other raise reached from the walk), says for each whether a repaired past can trigger it, and decides each one, so the next shape is not a third task.
- Design question the Chief Engineer session raised, his to gate: a historical version that contributes no identities can change which commit is a ruling's first appearance.
- Non-goals: changing qnow's task or history; relaxing the check on the pinned HEAD or the current text; the other qnow report items.

## Budget
- One implementation and one validation cycle, in one package PR to `scripts/dispatch_records.py` and its tests, plus an ADR change only if the design shows 0045's words exclude the outcome.

## Stop condition
- A replay of the qnow history at its recorded commits is refused at the kc-dev-flow-2-v0.38.1 tag and dispatched at the candidate, a history whose form error is still unrepaired at HEAD is refused at both, and a corpus replay over this workflow's and the adopters' state branches shows which tasks change outcome and that none the tag cleared changes; or the design shows why not and says what was learned.

## FO alignment

Alignment: needed at ideation; how a past version that does not parse is read, and what that does to the first appearance of a ruling under ADR 0045, are the Captain's call.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
