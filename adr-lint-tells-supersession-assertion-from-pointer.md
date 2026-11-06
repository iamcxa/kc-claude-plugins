---
title: The ADR lint pointer scan tells a supersession assertion from a pointer
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

`adr_lint.py` no longer reports a file an ADR protects as "points at ADR N, Superseded by M" when the only citation is a test asserting that N's Status reads "Superseded by M".

## Scope

- Source: FO, from a bite in batch 16 (2026-11-07); no Captain words yet; the backlog gate is his.
- Bite: decline-becomes-task-only-with-a-bite implementation, worker report (Paseo ba392d9b, 2026-11-07): ADR 0064 lists `kc-dev-flow-2/scripts/test_sd_dispatch.py` under Protects; the required `adr_lint.py docs/adr --since ba055b8a7 --require 0064` then fails on that file's assertion `"## Status\n\nSuperseded by 0050" in (ROOT.parent / "docs/adr/0047-…").read_text()`, because `check_pointers` counts every `docs/adr/NNNN` string in a protected file as a pointer. The worker could only pass by splitting the path literal (dispatch record implementation-1-message-3), which hides the citation from the scan rather than fixing it.
- Upstream first: `check_pointers` in `kc-dev-flow-2/scripts/adr_lint.py`; its tests.
- Non-goals: changing which files an ADR may protect; the split path in test_sd_dispatch.py may stay or be reverted by this task.

## Budget
- One package PR touching adr_lint.py and its tests; workflow word budget unchanged.

## Stop condition
- A fixture whose protected file asserts a superseded ADR's Status passes the lint, and a fixture whose protected file cites a superseded ADR as its authority still fails.

## FO alignment

Alignment: not needed; a lint false positive with one observed bite.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
