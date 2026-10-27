---
title: A dispatch record for a task holding a reserved ADR number is refused without its Number guards line
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「同意開 1 到 5，第 6 項併進「GPT 夥伴」提案」 (chat, 2026-10-27), answering FO's list of package-issue candidates (items 2 to 5 relayed by the relay FO, Paseo 1671c3a9, from its pair-once and room-specs-follow-web-part-select observer reports; item 1 relayed by the kc-ops-inbox FO, Paseo 46c2ebdf).
- Bite: relay pair-once implementation-1: its scope notes lacked 'ADR: 0069' though the task held that number, and `dispatch_records.py --names` passed it.
- Upstream first: `scripts/dispatch_records.py`, `scripts/number_guards.py`, the README's Number guards.

## FO alignment

Alignment: needed before ideation; where the check runs is a package design choice.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
