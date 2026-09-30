# 0004. Review rounds stop by rule and added comments are counted against a maximum

Date: 2026-09-30

## Status

Accepted

## Context

Two delivery PRs in an adopting project each took four rounds of an external
reviewer; in one the only P1 came in round one, and the Captain ruled the stop ad hoc;
a two-line P1 repair waited about 1h40 behind another task's worker in
the same stage; candidates reached validation at 12.6, 7.5 and 6.4 percent
added-comment ratio against a 5 percent target and each needed a trim round, and a
comment cited its task's own numbering. Read 2026-09-30 in the task's ideation,
from the adopter's task files and issues #521, #522 and #525. Spacedock 0.27.2
reads `concurrency` only for `status --next`; a feedback-reflow dispatch built
while another entity held the only slot. The Captain's baseline for added comments
is 3 percent, his target 5 percent.

## Decision

**Words:** 「核准」 — Captain, 2026-09-30, at the ideation gate of `review-cadence`

**Words, amendments approved with it:** the package defaults the comment-ratio maximum to 5 percent, overridable by the adopter's workflow README key or `--max`; the round rule applies to any external reviewer of the delivery (Codex on the PR, RoboRev or another), not Codex only. Recorded from the gate resolution of 2026-09-30.

**Options considered:**
- rounds 1 and 2 as today; from round 3 only a Material finding or a reviewer P1 starts a repair cycle and the rest become recorded follow-ups (chosen, N = 2)
- no rule, the Captain rules each PR — rejected: it cost repair cycles on two PRs
- cap at 3 rounds like `kc-pr-flow` self-review — rejected: that caps the author's own review, not an external reviewer's findings
- a repair lane keyed on the repair's size — rejected: size is unknown before dispatch; ownership of a worktree and an authorized assignment are known
- ship no comment-ratio default and let each adopter declare it — rejected by the Captain's amendment
- a five-percent default with an adopter key and a `--max` override (chosen)

A delivery PR's review rounds are counted by the first officer. A finding assessed
Material, or labelled P1 by the external reviewer, blocks in every round; a reviewer P1
is fixed and revalidated or waived by the Captain with the reason recorded. From the
third round a finding that is neither starts no repair cycle and becomes a follow-up in
the committed gate summary and a `Follow-up:` line in a task's Scope. A feedback-reflow
repair, its validation recheck and an authorized first-officer fix are dispatched at
once in the entity's own worktree; `concurrency` limits only what `status --next`
proposes (Spacedock 0.27.2; `scripts/test_sd_dispatch.py` builds a reflow dispatch while another entity holds the slot). `comment_ratio.py` exits 1 when added comments exceed the maximum (default 5
percent, `comment-ratio-max:` in the workflow README, `--max` for one run) with at least
20 code lines added, and when an added comment cites task numbering, review provenance,
a PR or issue number or a `file:line`, unless it names an ADR.

## Consequences

A real defect a reviewer labels below P1 and the first officer does not assess Material
is deferred to a follow-up from round 3. The round count, the lane and the follow-up
recording are prose the first officer applies; nothing mechanical enforces them, and
only an adopter's next delivery PR shows whether they hold. The citation scan finds its
named classes only, and a `#123` in a comment that is not an issue number is a false
positive. The 20-line floor is a choice, not a measurement. A reviewer that does not
label a P1 needs the first officer to map its blocking severity. Reopen if a follow-up
proves to have been a Material defect, or if Spacedock adds a slot check to the reflow
path.
