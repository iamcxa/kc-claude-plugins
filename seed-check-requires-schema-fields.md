---
title: The seed check refuses a task missing its schema's required fields
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「同意開 1 到 5，第 6 項併進「GPT 夥伴」提案」 (chat, 2026-10-27), answering FO's list of package-issue candidates (items 2 to 5 relayed by the relay FO, Paseo 1671c3a9, from its pair-once and room-specs-follow-web-part-select observer reports; item 1 relayed by the kc-ops-inbox FO, Paseo 46c2ebdf).
- Bite: relay room-specs-follow-web-part-select had no budget, no stop condition and no `id:`, yet `design_surfaces.py check --seed` passed (relay FO's report).
- Upstream first: `scripts/design_surfaces.py` (`check --seed`), the workflow README schema, Spacedock `new`.

## FO alignment

Alignment: needed before ideation; where the check runs is a package design choice.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
