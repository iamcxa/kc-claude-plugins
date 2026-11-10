---
title: A workflow run skipped by its own conditions does not hold the merge check
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the qnow dev2 FO, sent with the Captain's approval 「送出」 (2026-11-10).
- Bite: `delivery_gate.py check --pr iamcxa/qnow#1348` (run 2026-11-10 ~00:30 UTC) printed `1 of 2 workflow runs on this head are not finished and successful: 'Release Gate'` and held; that run (actions run 42657892764, event pull_request) is completed with conclusion skipped, every job skipped by its own `if:` because it applies only to release-please PRs. The PR merged after the Captain ruled on the printed output.
- Package fact to start from (kc-dev-flow-2 0.36.0 delivery_gate.py docstring, read 2026-11-10): "a completed skipped run settles when the required-check list is non-empty"; the qnow case should be checked against that clause first (an empty required-check list may be the cause).
- Suggested direction (qnow FO, not a ruling): count a completed run with conclusion skipped (and maybe neutral) as settled for the run-level check.
- Non-goals: treating a pending, failed or cancelled run as settled.

## Budget
- One package PR to delivery_gate.py and its tests.

## Stop condition
- The qnow #1348 shape passes the run-level check, while a pending or failed run on the head still holds.

## FO alignment

Alignment: needed at ideation; whether a whole-workflow skip settles without required checks is the Captain's call.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
