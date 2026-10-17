# 0023. FO merges a PR only in a change class the Captain granted on its recorded judgment

Date: 2026-10-17

## Status

Accepted

## Context

The Captain asked (chat, 2026-10-16): 「我想新增一張票，設計一個 codex 的 PR 守門員，它的任務是確保 P R 可以合併……只要例如 PR 超過 95% 沒問題，那就讓它帶我授權 FO 合併 PR，相應的但是也要讓它負責提出我需要注意的點……這件事的目的是，減低 FO 自己合併 PR 的意外，以及減低我每次都要肉眼 review PR 的負擔」. ADR 0011 says merge is "never delegated at any level"; ADR 0009 already allows automatic merge per unlocked class, never for rule changes. Counted at ideation, 2026-10-17, over the 30 archived dev2 tasks and 400 merged PRs of this repository: no unauthorised FO merge; two undisclosed merges at a head other than the validated one (2026-10-13, before the head check landed); five merge-adjacent mistakes between 2026-09-05 and 2026-09-11; a median of 36 minutes from validation briefing to merge on 20 PRs.

## Decision

**Words:** 「那就照建議」 — Captain, 2026-10-17, chat, approving the six batch-2 ideation gates after asking FO to restate this task's D1 reasoning

**Asked:** the task file's `## Unresolved decisions`: D1, whether a model judge is built now (recommended: the rule arm and the record-based points now, the model arm as a later task); D3, the bar and the label (recommended: a class qualifies at a one-sided 95% lower bound of at least 0.95 on its granted arm's record, which is 59 clean records with no failure; clean means merged at the judged head with no change asked after the judgment and no revert in 14 days; each grant is its own ADR in that repository, and one failure removes it).

**Options considered:**
- merge granted per class on the recorded judgment, pinned to the validated head (chosen)
- one grant for all PRs at a stated model confidence of 95%
- no delegation: the points list and the deterministic holds only

**Recommended:** merge granted per class on the recorded judgment.

This supersedes the sentence of ADR 0011 "Authority, gate approval, merge, outward-facing actions, irreversible changes and money are never delegated at any level" for merge only, and only as follows. FO merges a task's PR itself only when `delivery_gate.py check` prints the merge line: the deterministic checks pass, the change class is listed in the README's `merge-grants:` by its own Captain ADR on `delivery_gate.py calibrate` evidence, no point is printed, and the merge is `gh pr merge --match-head-commit <validated candidate>`. The classes fixed as never eligible (a prod task, a `db` surface, a release PR, and any path an agent loads as instructions or that decides a review, gate or grant) are never granted. A failure in a granted class stops FO's merges in it at once, because `check` reads the class's records; FO tells the Captain and proposes removing the README entry. Every other part of ADR 0011's sentence stands.

## Consequences

Nothing merges by FO until a class qualifies and the Captain grants it in its own ADR. A class takes from weeks to months to reach 59 records at the measured pace, and `other` may never. The label is a proxy: it does not see a fix-forward that does not revert, and amendments carry a date only, so a same-day amendment is not seen. Reopen if a granted class ships a defect the label missed, or if a model arm is built and its answers drift from the record.
