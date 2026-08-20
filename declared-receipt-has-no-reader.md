---
id: q0z8h3xny0qxv0r5srter8tj
title: Conditional-reference receipt and trigger declarations are read by nothing
status: backlog
source: adopter field report on kc-dev-flow 3.0.0, filed as issue #256 (2026-08-19); confirmed on origin/main and the current branch before filing
product: kc-dev-flow
sprint:
started:
completed:
verdict:
worktree:
issue: 256
pr:
mod-block:
---

## Problem

Every stage contract in `kc-dev-flow/references/profiles/**` declares a
`kc-dev-flow-conditional-references/v1` block whose entries carry `path`,
`trigger`, and `receipt`. `scripts/profile-contract-loader.py`
(`check_conditional_references`) reads only `path`, and fails closed when the
named file is not vendored. `trigger` and `receipt` are consumed by nothing —
not the loader, not a skill, not a script. A stage can therefore complete having
produced no `reverse_recovery`, `journey_slices`, or `project_context` receipt
and the route still reports success. The asymmetry is the defect: the same block
enforces one field rigorously and ignores the other two, so a field that names an
obligation reads as a guarantee while providing none.

Confirmed present at `kc-dev-flow-v3.0.0`, on `origin/main`, and on the current
branch: 9 contracts declare receipts; the loader's only entry read is
`entry["path"]`.

## Work profile receipt

## Accepted outcome and non-goals

## Acceptance evidence

## Measurement
