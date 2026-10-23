# Intake: release preparation, from the kc-paseo-plugins dev2 FO (2026-10-21)

Relayed by Paseo agent 8b2c2fc2, quoting the Captain there (relayed, not a ruling in this session): 「我期望看到切片地圖有出現，我才能就你的審查結果再看一次，我未必會細看，但這這個就像是 ADR 一樣會成為開發歷程的紀錄，讓下一個 agent 有所本，那問題就是，這兩個機制是否應該再統合一下，我感覺有點重疊但又不完全一樣？」 and 「原則上我希望你跑一次審問流程，然後把經驗與你的建議整個丟給 dev2 FO 讓它思考與設計怎樣做」.

## What ran (paseo-project-env r1.5, four stories, kc-journey-map 1.7.0)
- review-release (triggered by the dev2 README backlog Release review signal 4): map check, path walk table, slice check, task split. Output existed only in chat; no durable record, no canvas page. The task's `Release review: <journey>/<release> at <commit>` line points at a map commit, not at the review.
- interrogate right after: 27 new questions, each classed fact/gap/ruling/deferred; nine left open. Durable (YAML, iamcxa/kc-paseo-plugins#13). `journey-handoff.mjs` refuses the release while any is open.

## Overlap and difference
- Both re-checked existing answers against code and found the same three stale answers.
- Only review-release found: a stale status card, status/evidence drift (r1 stories still `gap` after merge), an undated ruling, path holes (a step with no story, an actor whose context the product cannot know), and the task split.
- Only interrogation found: the nine opens, 27 facts/gaps, two ruling citations.
- Order mattered: review-release ran first, so its task split rests on answers interrogation later added nine open questions to.

## Method gaps the interrogation worker logged
1. A question counts as answered if it has any `answer`/`doc`, regardless of `status`.
2. The method assumes a human sorts questions; a dispatched run has none.
3. No class for "design detail the task's own ideation will settle"; it must be `open` (blocks handoff) or answered.
4. A new gap has no release to name, and nothing says what to write instead.
5. Nothing specifies the status card's `as_of`, or that `doc:` must be a URL; the canvas rejected relative `doc:` paths, so this map's journey-board pages had never rendered until 16 links were rewritten.
6. The progress view reads task state only, so an accepted release shows "pending delivery acceptance" even with the Captain's acceptance in the map's `ruling:` list.
7. The open-question placeholder that blocks fold (task journey-fold-answers-open-placeholders) has the same root as 3.

## The relaying FO's recommendation
1. One "prepare a release" flow in a fixed order: interrogate first, then walk and slice check, then task split; review-release re-checks only answers changed since the last interrogation.
2. A durable release-review record, ADR-like, beside the journey (e.g. `docs/journey/<product>/reviews/<release>.md`) holding the walk table, slice verdict, task split, map commit and code commit; the dev2 `Release review:` line points at it.
3. Canvas is part of the output: the flow redraws that release's journey-board page; fix or relax the `doc:` URL requirement.
4. A question class for "settled in the task's ideation" that does not block handoff but must be resolved before that task's ideation gate.
5. Progress reads release acceptance from the map, or acceptance is recorded where progress reads.

Evidence named: run artifacts in /tmp/r15-interrogate/run/ on the Captain's MacBook (local only); map diff iamcxa/kc-paseo-plugins#13.
