---
title: A task's design director runs on the model its ideation worker ran on
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「可以」 (chat, 2026-10-23), answering FO's question on release-walk-picky-reviewers-and-director D2, whose first point was: each task's design director, at ideation (passes 1a, 1b) and validation (passes 2a, 2b), follows that task's ideation worker model (opus when the ideation ran on opus, else sonnet); his words before it: 「一個版本是指什麼？我的理解是，一個任務一開始評估用 opus 做設計時，那它的設計總監就會是 opus」.
- What exists: kc-dev-flow-2 agents/design-director.md declares sonnet (#708, merged 0701aa8d); dispatch records carry a `Model:` line; the README's model rule (ideation sonnet by default, opus when a decision is hard to reverse).
- Shape to design: where the model is read and passed (the ideation and validation instructions that dispatch the director, a dispatch model override, or the agent file), and a check that the director ran on the task's ideation model.
- Non-goals: the release walk's pass 3 rule (release-walk-picky-reviewers-and-director).

## FO alignment

Alignment: not needed before ideation; the rule is his, stated above.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
