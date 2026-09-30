# 0004. Review rounds stop by rule and added comments are counted against a maximum

Date: 2026-09-30

## Status

Accepted

## Context

Two delivery PRs in an adopting project each took four rounds of an external
reviewer; in one the only P1 came in round one, and the Captain ruled the stop ad hoc;
a two-line P1 repair took about 1h40 from the validation approval to its report (dispatch time not recorded) while
another task's worker held the same stage (the state history is consistent with
`concurrency: 1` being read as a hard cap; the cause is not proven); candidates reached validation at 12.6, 7.5 and 6.4
percent added-comment ratio against a 5 percent target and each needed a trim round, and a
comment cited its task's own numbering. Read 2026-09-30 in the task's ideation,
from the adopter's task files and issues #521, #522 and #525. Spacedock 0.27.2
reads `concurrency` only for `status --next`; a feedback-reflow dispatch built
while another entity held the only slot. The Captain's baseline for added comments
is 3 percent, his target 5 percent.

## Decision

**Words:** Captain, all 2026-09-30, in order (ideation gate `review-cadence`, then its validation gate):

- 「套件本身不設預設值 => 為何不要預設就是「基準 3%、目標 5%」？你有想到其他案例是要極端少註解或是明顯拉大閥門數量的嗎？」
- 「此外審查輪數目前應該沒有考慮搭配使用 roborev 的狀況對嗎？它應該也會有一樣的問題，每次審查都有機會找到狀況，要一併考慮，還是等整合用了遇到再說？」
- 「專案可以自己改，具體是怎麼改？改 adoptor 的 readme.md 嗎？」
- 「核准」, approving the design with two amendments: the package default is 5 percent, overridable by `comment-ratio-max:` or `--max`; the round rule (N = 2) applies to any external reviewer.
- 「退回補」 at the validation gate: four repairs, and the constructed false-positive classes of the citation scan declined as a known limit.

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
repair and an authorized first-officer fix are dispatched at once in the entity's own
worktree, and the validation recheck of either is dispatched after the repair or fix
has completed and committed its candidate; none waits for another entity's worker,
and `concurrency` limits only what `status --next`
proposes (Spacedock 0.27.2; `scripts/test_sd_dispatch.py` builds a reflow dispatch while another entity holds the slot). `comment_ratio.py` exits 1 when added comments exceed the maximum (default 5
percent, `comment-ratio-max:` in the workflow README, `--max` for one run) with at least
20 code lines added, and when an added comment cites task numbering, review provenance,
a PR or issue number or a `file:line`, unless it names an ADR.

## Consequences

A real defect a reviewer labels below P1 and the first officer does not assess Material
is deferred to a follow-up from round 3. The round count, the lane and the follow-up
recording are prose the first officer applies; nothing mechanical enforces them, and
only an adopter's next delivery PR shows whether they hold. The citation scan finds its
named classes only, and it also flags text that only looks like a citation: a `#333`
colour, `step #1`, a URL fragment, an asyncio "Task 3", "a code review of the parser",
"the Codex CLI". Measured on the last 150 commits of origin/main: 38 hits, 1 false
positive. The Captain declined a fix for these classes as a known limit. The
20-line floor is a choice, not a measurement. For a reviewer with no P1 label, its
highest severity level counts as P1 (`workflow.md` item 5, e.g. RoboRev). Reopen if a
follow-up proves to have been a Material defect, or if Spacedock adds a slot check to
the reflow path.

Amended 2026-10-01: the validation recheck is dispatched after the repair completes and commits, not at once with it (`workflow.md` Stages).
