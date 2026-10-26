---
title: A repair dispatch for a review finding asks the worker to list and fix the finding's sibling sites
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「可以，開 A-D」 (chat, 2026-10-26), answering 「需要你決定：下面 5 個套件缺口候選，要開哪幾張待辦？我建議開 A 到 D，E 先不開。」 after the learn backfill of 11 archived tasks (Captain 「補跑」, 2026-10-26).
- Bite: learn jobs cb9bfddb (#708: Codex round 1 named one too-wide lookup in design_surfaces.py check_built_screen, cycle 3 fixed only it, round 2 P1 found three siblings) and 5d9d5316 (#714: Codex rounds 1 to 3 each found another input the `clean` predicate did not read). root learning.md already has 'List every input before promising a verdict survives later history' (a finding of that class extends the whole list), so the gap is that the repair dispatch does not ask for it; the Captain declined a second learning entry for the same practice (「那就不要加」, 2026-10-26).
- Upstream first: the README's FO steps: review findings and its fix-authorization dispatch checklist, `scripts/dispatch_records.py`, implementation principles, root learning.md.

## FO alignment

Alignment: needed before ideation; where the check runs is a package design choice.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
