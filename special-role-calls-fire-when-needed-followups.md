---
title: special-role-calls-fire-when-needed follow-ups declined at the #682 delivery gate
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Declined by FO at the #682 delivery gate (head f4447396, 2026-10-20); reasons also in that gate summary.

- Deferred risk (validation F2): a review reply comment carries its own review id, so a task PR with author replies could fire the review-round count on one real reviewer round. Material when that happens; 0 replies in 82 inline comments across the 38 window PRs.
- Polish (F1): no test asserts the `--paginate --slurp` flags in `pr_watch.py` `review_rounds`; dropping both would undercount past 30 comments (no window PR has 30).
- Polish (F3): no synthetic test row with a literal `### Feedback Cycles` heading for AC-2; covered by the replay hint only.
- Polish (F5): an owed engineering-reviewer line lists every amendment number, so about a dozen amendments pass the 60-word bound the tests check up to six; the replay's captain-question-load "clears" row is vacuous in slice 1.
- Open decision: D5 stage 2 (rerun the prod security reviewer on Opus or Fable for #666's escaped heads plus controls, about 40 USD assumed), after stage 1 found 2 escapes on one PR (`security-evaluation-stage-1.md` in the archived task).
