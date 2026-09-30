---
title: A delivery PR's review rounds stop by rule, a small fix does not queue behind a long task, and comment ratio has a threshold
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Three review-cadence defects from qnow dogfooding (2026-09-28..29) that each cost extra full cycles or hours of waiting.

## Scope

Captain 2026-09-30, approving the FO's batching of the dev2 fixes: 「可以」 — batch B (review cadence) after batch A; 2026-09-30: 「等Ｃ做完…繼續 B」 — the package release waits for batch C. This task covers issues #521, #522 and #525.
Evidence (qnow): #1243 and #1245 each went through four Codex rounds with a P1 only in round one, and the Captain ruled the stop ad hoc ("最後一輪，之後沒有 P1 就合併"); a two-line P1 fix waited several hours in the implementation queue behind a 68-file task, and a two-minute recheck waited behind a long browser validation; candidates reached validation at 12.6%, 7.5% and 6.4% added-comment ratio against a 5% target, each needing a trim round, and a comment cited the task's own ideation numbering.
Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Needed at ideation: the stopping rule for review rounds on a delivery PR (what always blocks, what becomes a follow-up after how many rounds, and where the follow-up is recorded); how a small rework avoids waiting behind a long task in the same stage, and whether that needs Spacedock or only the package; the comment-ratio threshold, where it is enforced, and the rule for what a comment may cite.
Result: the FO delegates these questions to ideation, which decides each with its source and returns any ruling that needs the Captain.
Surfaces: none
Visible change: none
