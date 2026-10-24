# 0033. A release walk is operated by reviewers on different models and ruled by the design director on one model per walk

Date: 2026-10-23

## Status

Accepted

## Context

Two hand walks of an adopter's releases (2026-10-09 and 2026-10-10) found problems no single task's validation saw, and a hand-run picky-user review on another product (2026-10-23) found two models independently naming the same top blocker an earlier task had deferred. Nothing owns a deferred finding: `- F<N> Deferred risk:` and `- F<N> Polish:` bullets, `declined:` and `Needs decision:` items and `Built screen finding` lines sit in validation Stage Reports, and no script lists them by release. ADR 0030 records that a release-level operated review belongs to the release walk, and ADR 0031 records the two schemas it meets kc-journey-map at. Two bounded searches of origin/main on 2026-10-23 (`git grep -n -i -E 'picky|release walk|release_ruling|works-but-unusable|usability'` over five plugins, and `git grep -n -i -E 'Deferred risk|Polish'` over `kc-dev-flow-2/scripts`) found no producer or consumer of a reviewer walk or ruling. A measured prototype of the deferred list on a sibling adopter's state branch gave 0 to 37 items per release.

## Decision

**Words:** 「好」 — Captain, 2026-10-23, chat, Amendment 2 of `release-walk-picky-reviewers-and-director`, answering 「要我照這個方向改嗎？」 after the recommendation that the design director use one model per walk, opus when any task the walk covers was designed on opus and sonnet otherwise, with the per-item escalation removed; 「可以先用同模型。我在想這裡其實應該要用類似 ext 做法，我之前提過的，等於該 ext 會啟用不同模型的支援能力，這樣比較能排除問題」 — Captain, 2026-10-23, chat, answering the question of Claude-only reviewers now and other providers later; 「准」 — Captain, 2026-10-23, ideation gate of the same task, digest 9d4c90c8, which also approved the per-item escalation that Amendment 2 withdrew.

**Options considered:**
- An extension `release-acceptance` runs a walk with at least two operating reviewers on distinct personas and distinct Claude models (or a declared single-model fallback), a smoke check first, the deferred findings fed to reviewers and director, and a table of at most three backlog tasks from design-director pass 3; pass 3 runs on one model per walk, which `director-model` prints: opus when any task of the release ran its ideation on opus (any ideation dispatch record naming it, live or archived), else sonnet; the report records that model and `check --tier final` refuses a different one; the report keeps top-level `stories[]` (chosen)
- Pass 3 on sonnet, with each item moved to opus when its owning task was designed on opus, the reviewers disagree, or sonnet ruled it unverified, a backlog task or a decision (the Captain's earlier ruling D2; not chosen after measurement: on one fixture the fourth condition listed 5 of 5 items in two sonnet runs, so the opus pass reported 358k and 294k tokens against 293k for an opus control over every item, and the maintenance of four conditions bought nothing)
- Pass 3 on sonnet for every walk (recommended by FO at ideation with a flip to be decided by a live run; not chosen, the Captain wants the director to follow the design model)
- Pass 3 on opus for every walk (not chosen: a walk whose tasks were all designed on sonnet pays for opus)
- A proof-of-concept task for a reviewer on a non-Claude provider inside this task (recommended by FO; not chosen, the Captain wants other providers through an extension that enables multi-model support, backlog task `gpt-partner-extension-proposal`)
- A pull request carrying the record (see ADR 0034)

**Recommended:** the first option, one director model per walk, as FO recommended when the Captain withdrew the per-item escalation.

A release is walked after its last story. Reviewers write JSON reports in the acceptance task's `walk/` folder, the director rules each merged complaint and each deferred finding on the one model `director-model` names, and `release_acceptance.py` derives owners, consolidation and `clean`; it decides nothing, the Captain accepts. A second run of the same extension after the fix tasks land is a re-walk: each original reviewer, with the same id, model and persona, marks its own complaints `fixed`, `partly-fixed`, `deferred` to a named release or `will-not-fix` with a reason, and may add new ones (Captain, 2026-10-23: 「按你建議」); `record.md` opens with one row per complaint, its task, status and reason. The enforcement points are the extension's tests: owners and routes, the director model and its refusal, the refusals for equal personas or models, a missing smoke, an unruled deferred item, and a re-walk whose prior digest or reviewer row differs.

## Consequences

A blind spot two Claude models share is not tested. That a declared model is the model that ran, that two models differ in fact, and that the director is right are not checked; the report's `director.model` is what the worker declared, compared with what the task records say, not proof of what ran. A walk is ruled on opus whenever any one task of the release was designed on opus, even if most were not. A task with no ideation record or no `Model:` line counts as not opus, and `director-model` prints a note naming it. Reviewer and ruling files are JSON, not YAML, because package scripts are standard-library only and model output carrying unquoted colons already failed YAML parsing in the design review reports. The extension adds one CI step. A story with a task and a later bug task counts two owners and routes to `review-release`. Reopen when a reviewer on another provider is added (a `release-acceptance/v1` bump) or when a real walk shows the director's model changed a ruling the Captain would have decided the other way.
