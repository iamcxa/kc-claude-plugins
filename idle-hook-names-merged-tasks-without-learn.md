---
title: The idle hook names an archived task with a merged PR and no learn job
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「可以，開 A-D」 (chat, 2026-10-26), answering 「需要你決定：下面 5 個套件缺口候選，要開哪幾張待辦？我建議開 A 到 D，E 先不開。」 after the learn backfill of 11 archived tasks (Captain 「補跑」, 2026-10-26).
- Bite: 11 archived tasks with merged PRs (#708, #709, #711, #713, #714, #716, #719, #720, #721, #722, #724; 2026-10-23 to 10-26) had observer reports but no learn job in `learning.py notices --all`; FO backfilled them on 2026-10-26. `observer_check.py` already prints `next: run kc-dev-flow-2:learn for <slug>` for an archived task, and `pr_watch.py` reacts to a watched PR turning MERGED, but FO merged these PRs directly and did not run `observer_check.py`, so nothing reminded it.
- Upstream first: `scripts/pr_watch.py` (`tasks`, the idle hook), `scripts/observer_check.py`, `extensions/learn/EXTENSION.md`, `scripts/learning.py notices --all`.

## FO alignment

Alignment: needed before ideation; where the check runs is a package design choice.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
