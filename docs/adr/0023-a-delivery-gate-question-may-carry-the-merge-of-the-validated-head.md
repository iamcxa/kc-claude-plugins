# 0023. A delivery gate question may carry the merge of the validated head

Date: 2026-10-19

## Status

Accepted

## Context

Measured on batch 2 (2026-10-17 to 10-19): the Captain gave FO 22 answers to 63 asks; 5 were merge asks outside a gate message and 4 were procedural, one of them a worktree cleanup. 20 of the 22 accepted FO's recommendation as stated, but several came with a question of his first, so acceptance is not evidence for delegating. A written rule could settle at most 2 of the 22: the standalone merge ask of a task PR and the removal of its clean worktree. The other 20 stay his under ADR 0011, README step 4, ADR 0009, his own rulings or the permission check. `delivery_gate.py check` already holds the merge on head, CI, draft, base and file list.

## Decision

**Words:** 「照建議」 — Captain, 2026-10-19, chat, approving the four batch-3 ideation gates presented together. The captain-question-load gate question read: "Approve the design and enter implementation as Pilot? Approving accepts D1 (land a Delivery authority sentence that lets a delivery gate question carry the merge of the validated head and the cleanup of its worktree, with 'unless he says he merges' as the opt-out, plus delivery_gate.py's last line saying 'merge this head if the approved question named the merge, else ask', and an ADR that his approval of such a question is his answer), D2 (learning PRs and the Release PR are still asked one at a time), and FO's implementation order below." When the implementation worker's edit of the Delivery authority wording was refused by the permission check, he added, in chat, 「授權修改 Delivery authority 合併措辭，照 D1 設計。但我要你明確跟我說，當我同意/核准驗證關卡時，等於授權你也合併 PR，除非我有顧慮暫時不合併。但這裡必須要硬前提，ＰＲ 必須是 ready 狀態，合理嗎？」 (Captain amendment 1 in the task file).

**Options considered:**
- D1 land one Delivery authority sentence and the new text of the last `next:` line of `delivery_gate.py`: when FO's delivery gate question names the merge of the head `delivery_gate.py check` passes and the removal of its clean, pushed worktree, his approval of that question is his answer to both asks, unless he says he merges himself (chosen); keep asking for the merge and the cleanup one at a time — not chosen, it leaves 22 answers at 22
- D2 learning PRs and the Release PR stay one ask each, no stacking (chosen, ADR 0009); a class grant for them — not chosen here, the route is the `merge-grant-need-poc` task and ADR 0009's per-class unlock

**Recommended:** D1 and D2, as the task design stated and the Captain accepted.

The README sentence is net zero words (the cut sentence defines "green", which `pr_watch.py` and `delivery_gate.py` already enforce). The `ASK` line prints text only: the script reads no question and decides nothing, so the one-bit grant (the approved question said so) stays with FO and the README. ADR 0011's never-delegated list is unchanged because he is still asked, in the delivery question.

## Consequences

One standalone merge ask and the worktree cleanup ask are removed for a task whose delivery question named them. The merge still waits for `delivery_gate.py check` to exit 0, and the Captain's hard precondition, a PR that is ready and not a draft, is already a hold there (a draft PR exits 1). Worse: a quick approval is no longer followed by a pause before FO merges, so a Material change he would have caught at a second ask has one fewer chance; the head, CI and base checks still run. If FO omits the sentence from the question, the rule fails safe: he is asked again, as today. Nothing checks that a merged PR's approved question named the merge; that check would belong to `fo-write-checks`. The last `next:` line grows from 7 to 25 words at the merge ask. Reopen if a merge lands on an approval whose question did not name it, or if batch 3 still shows a standalone merge ask for a task whose question carried the sentence.
