---
id: xtw8zj59fr97f1kwkhd9a4wy
title: "39 pre-existing banned selectors get grandfathered with no owner and no due date"
status: backlog
source: "EM ideation gate on e2e-runner-path-selector-enforcement, 2026-08-02"
product: e2e-pipeline
sprint:
started:
completed:
verdict:
worktree:
issue:
pr:
ledger_pr:
pr_artifact_v1:
ledger_artifact_v1:
mod-block:
design:
lane:
---

## Problem

[[e2e-runner-path-selector-enforcement]] chose a diff-scoped CI gate so that adopting it does
not demand an unrelated whole-file migration — the same reasoning the captain applied at #88.
The consequence is that carlove's existing findings are grandfathered indefinitely: measured
2026-08-02 with the shipped linter, **15** in `secha-office.yaml` and **24** in
`secha-app.yaml`, 39 in total, all `>> nth=` chords.

#88 grandfathered its debt too, but with a baseline file that byte-compares — an *inventory*
of what was accepted. Diff-scoping needs no baseline for blocking, which is why it was chosen,
but it also produces no inventory. Nothing then names how many findings were accepted, when,
or who owes their removal.

That is the same shape this workflow already refused elsewhere: a debt line with no owner and
no due date. This seed is the inventory.

Not urgent. `>> nth=` chords fail loudly rather than silently when exercised, and these have
sat without incident. What is being avoided is the number quietly growing while the gate
reports green because nobody touched those lines.
