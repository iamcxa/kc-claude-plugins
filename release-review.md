---
title: A release is re-reviewed as one whole journey before its tasks are split, and a slice stays small enough to review
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

A release gains tasks one at a time and nothing checks that together they still form one complete journey; batch C part 2 of the dev2 fixes.

## Scope

Captain 2026-09-30: 「有部分關係，你稍後可以找那個 peer ，有一個新的提議是 cl 認為每個切片只能有五件事，你可以跟他交換這個問題的細節，並且看看是否可以把這個規則跟 520 結合，那個 peer 就可以專心處理 relay + spacedock review 的旅程問題。我們來解決 520 問題。」 This task covers issue #520 and the proposed "a slice holds at most five things" rule.
Evidence (qnow, 2026-09-29, issue #520): over two days the Captain ruled eight-plus tasks into one release, each filed and designed on its own scope; the journey map's release stayed at its five stories of 2026-09-23 and the shop journey had none; cross-task holes surfaced only at Captain UAT (no brand context in the owner app, no signed-in identity in the office, no task that takes a real shop live on production). On 2026-09-30 the Captain then re-cut qnow's go-live slices from a whole-journey analysis before any dev2 fix.
Five-things rule: details pending from the peer session that proposed it; the FO adds them here before ideation is dispatched.
Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Needed at ideation: at which signals a release is re-reviewed as a whole journey (a task admitted into a release, a Captain scope ruling, a UAT failure that crosses tasks, before a batch enters implementation) and what the re-review produces; whether tasks carry `journey`, `journey-release` and `journey-story` so kc-journey-progress can compute completion; what "a slice holds at most five things" counts, where it is checked and what happens above five; which parts belong to kc-dev-flow-2 and which to kc-journey-map.
Result: the FO delegates these questions to ideation, which decides each with its source and returns any ruling that needs the Captain.
Surfaces: none
Visible change: none
