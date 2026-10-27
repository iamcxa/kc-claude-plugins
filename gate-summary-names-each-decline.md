---
title: A gate summary that declines findings names each finding and its reason
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「同意開 1 到 5，第 6 項併進「GPT 夥伴」提案」 (chat, 2026-10-27), answering FO's list of package-issue candidates (items 2 to 5 relayed by the relay FO, Paseo 1671c3a9, from its pair-once and room-specs-follow-web-part-select observer reports; item 1 relayed by the kc-ops-inbox FO, Paseo 46c2ebdf).
- Bite: relay pair-once validation-1: the gate summary said 'security 2 LOW declined' without naming the findings or a reason; `gate prepare` accepted it, and `delivery_gate.py` checks only text starting with 'Declined:' (relay FO's reading).
- Upstream first: `scripts/delivery_gate.py` decline parsing, `scripts/design_surfaces.py`, the README's FO steps: review findings step 2.

## FO alignment

Alignment: needed before ideation; where the check runs is a package design choice.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
