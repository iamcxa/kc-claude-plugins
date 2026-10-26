---
title: The delivery check refuses a `copilot not run` line without the printed quote and a retry offer
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「可以，開 A-D」 (chat, 2026-10-26), answering 「需要你決定：下面 5 個套件缺口候選，要開哪幾張待辦？我建議開 A 到 D，E 先不開。」 after the learn backfill of 11 archived tasks (Captain 「補跑」, 2026-10-26).
- Bite: observer report on fo-written-lines-checked-before-dispatch (#724, 2026-10-26): the merge ask said only 'not run (quota)', against `extensions/copilot/EXTENSION.md` ('with the printed quote, and offers a retry'); FO had recorded the same rule in its own notes after the fo-write-checks observer caught it on 2026-10-19, and still missed it.
- Upstream first: `scripts/delivery_gate.py` (`check`, `question`), `extensions/copilot/EXTENSION.md`, `extensions/copilot/copilot_review.py` exit 5 output.

## FO alignment

Alignment: needed before ideation; where the check runs is a package design choice.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
