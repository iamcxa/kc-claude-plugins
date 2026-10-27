---
title: merge guard does not archive a learn-listed task before its observer report is committed
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「同意開 1 到 5，第 6 項併進「GPT 夥伴」提案」 (chat, 2026-10-27), answering FO's list of package-issue candidates (items 2 to 5 relayed by the relay FO, Paseo 1671c3a9, from its pair-once and room-specs-follow-web-part-select observer reports; item 1 relayed by the kc-ops-inbox FO, Paseo 46c2ebdf).
- Bite: relay pair-once (relay#442): `merge guard --verdict passed` archived the task before observer.md existed; it was committed after archive commit 64ac8c39. Same order here on fo-written-lines-checked-before-dispatch (#724, observer finding 2026-10-26: the sentinel was written before observer.md). `observer_check.py` names the step but nothing refuses the archive.
- Added 2026-10-27: a third bite, relayed by the kc-ops-inbox FO (Paseo 46c2ebdf, data): its task ops-metric-event-protocol (PR #727, merged d7eeeef2) ran the sentinel and archive before the observer report (its observer.md at state commit f25c224f6). Same relay: `spacedock state commit` refuses an archived slug, so an observer report written at archive needs a raw git commit.
- Upstream first: Spacedock `merge guard` (upstream), `scripts/observer_check.py`, `extensions/learn/EXTENSION.md`, the package mod's merge hook.

## FO alignment

Alignment: needed before ideation; where the check runs is a package design choice.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
