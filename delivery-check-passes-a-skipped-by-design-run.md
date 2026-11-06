---
title: delivery_gate.py check does not hold on a workflow run skipped by design
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

`delivery_gate.py check` treats a workflow run that its own conditions skip on purpose as no hold, while still holding a failed, pending or unexpectedly skipped required check.

## Scope

- Source: the Captain 「開」 (chat, 2026-11-06), answering 「要開這 4 張嗎？」 after fo-feedback round 005 (.notes/fo-feedback/round-005.md, closed 2026-11-06).
- Bite: qnow: check held #1338 on a by-design skipped "Release Gate" run, and the Captain waived it (「豁免release gate跳過，合併1338」); the qnow FO reports it holds every feature PR (round 005, operator report, not re-run here).
- Upstream first: kc-dev-flow-2 scripts/delivery_gate.py check ("a workflow run on the head is not completed and successful (a skipped run included)").
- Non-goals: changing which checks are required.

## Budget
- One package PR; the workflow word budget does not rise unless the design names a raise for the Captain.

## Stop condition
- A replay of the #1338 check passes the skipped Release Gate run; a required check that fails or stays pending still holds.

## FO alignment

Alignment: needed at ideation; the design choice is his to accept.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
