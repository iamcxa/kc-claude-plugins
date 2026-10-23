# 0033. A release walk is operated by reviewers on different models and ruled by the design director, with contested items moved to opus

Date: 2026-10-23

## Status

Accepted

## Context

Two hand walks of an adopter's releases (2026-10-09 and 2026-10-10) found problems no single task's validation saw, and a hand-run picky-user review on another product (2026-10-23) found two models independently naming the same top blocker an earlier task had deferred. Nothing owns a deferred finding: `- F<N> Deferred risk:` and `- F<N> Polish:` bullets, `declined:` and `Needs decision:` items and `Built screen finding` lines sit in validation Stage Reports, and no script lists them by release. ADR 0030 records that a release-level operated review belongs to the release walk, and ADR 0031 records the two schemas it meets kc-journey-map at. Two bounded searches of origin/main on 2026-10-23 (`git grep -n -i -E 'picky|release walk|release_ruling|works-but-unusable|usability'` over five plugins, and `git grep -n -i -E 'Deferred risk|Polish'` over `kc-dev-flow-2/scripts`) found no producer or consumer of a reviewer walk or ruling. A measured prototype of the deferred list on a sibling adopter's state branch gave 0 to 37 items per release.

## Decision

**Words:** 「可以先用同模型。我在想這裡其實應該要用類似 ext 做法，我之前提過的，等於該 ext 會啟用不同模型的支援能力，這樣比較能排除問題」 — Captain, 2026-10-23, chat, answering the question of Claude-only reviewers now and other providers later; 「可以」 — Captain, 2026-10-23, chat, answering 「D2 照這樣做（驗收按任務的設計模型加三個條件，第 1 條另開任務改 #708），可以嗎？」 after 「一個版本是指什麼？我的理解是，一個任務一開始評估用 opus 做設計時，那它的設計總監就會是 opus」; 「准」 — Captain, 2026-10-23, ideation gate of `release-walk-picky-reviewers-and-director`, digest 9d4c90c8.

**Options considered:**
- An extension `release-acceptance` runs a walk with at least two operating reviewers on distinct personas and distinct Claude models (or a declared single-model fallback), a smoke check first, the deferred findings fed to reviewers and director, and a table of at most three backlog tasks from design-director pass 3; pass 3 starts on sonnet and an item moves to opus when the owning task's ideation ran on opus, the reviewers disagree on it, or sonnet ruled it `unverified`, a backlog task or a decision; the report keeps top-level `stories[]` (chosen)
- Director pass 3 on sonnet for every item, with a flip to opus decided by one live run (recommended by FO; not chosen, the Captain wanted the model to follow the design model per item)
- Director pass 3 on opus for every item (not chosen: a second opus run over every item for a subset that differs)
- A proof-of-concept task for a reviewer on a non-Claude provider inside this task (recommended by FO; not chosen, the Captain wants other providers through an extension that enables multi-model support, backlog task `gpt-partner-extension-proposal`)
- A pull request carrying the record (see ADR 0034)

**Recommended:** the second option, director on sonnet with a flip decided by the live run, and a proof-of-concept task for a non-Claude reviewer; the Captain chose per-item escalation and an extension for other providers.

A release is walked after its last story. Reviewers write JSON reports in the acceptance task's `walk/` folder, the director rules each merged complaint and each deferred finding, and `release_acceptance.py` derives owners, consolidation, escalation and `clean`; it decides nothing, the Captain accepts. A second run of the same extension after the fix tasks land is a re-walk: each original reviewer, with the same id, model and persona, marks its own complaints `fixed`, `partly-fixed`, `deferred` to a named release or `will-not-fix` with a reason, and may add new ones (Captain, 2026-10-23: 「按你建議」); `record.md` opens with one row per complaint, its task, status and reason. The enforcement points are the extension's tests: owners and routes, the four escalation conditions, the refusals for equal personas or models, a missing smoke, an unruled deferred item, and a re-walk whose prior digest or reviewer row differs.

## Consequences

A blind spot two Claude models share is not tested. That a declared model is the model that ran, that two models differ in fact, and that the director is right are not checked. Reviewer and ruling files are JSON, not YAML, because package scripts are standard-library only and model output carrying unquoted colons already failed YAML parsing in the design review reports. The extension adds one CI step; the cost per pull request was not measured. A story with a task and a later bug task counts two owners and routes to `review-release`. One live run on a synthetic fixture (two sonnet runs, one opus control over every item, 2026-10-23) listed 5 of 5 items and 2 of 3 deferred findings for opus in both sonnet runs, because the fourth condition catches every item sonnet turned into a backlog task or a decision; the opus pass over them reported 358k and 294k tokens against 293k for the opus control over everything, so on that fixture the escalation saved nothing. Reopen when a reviewer on another provider is added (a `release-acceptance/v1` bump) or when a walk shows an item opus would rule differently that no condition escalated.
