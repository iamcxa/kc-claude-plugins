---
id:
title: Tonight's method-against-no-method cell, both readings and both final tables are on the private working repository's remote, with the raw runs left on the laptop
status: backlog
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree:
pr:
---

The day's main result, two readings of whether an agent given the method does better than one given the task in plain words, exists on one machine only: its cell, grader changes, readings and final tables were committed after the push that carried the earlier code, and live on a laptop-only branch beside the raw runs.

## Scope

- Source: the reform session's ruling under the Captain's standing grant to the second dev2 FO (Paseo 26215d96, message 94ecfb61, 2026-11-14): "tonight's method-against-no-method cell, both readings and both final tables go to the private remote by the same allowlist-and-scan route, raw runs stay on the laptop. Keep it small". Admission is recorded by FO under that grant.
- Outcome: the private working repository's remote main carries the method-against-no-method cells of both readings (reading documents, cell and answer files, synthetic fixtures), the runner as it stands at the final tables' commit, the table-rule fixture script and proofs the readings cite, and both readings' final tables; it carries no raw run output, run list, collected transcript, blind packet or key. The range scans at zero in every identifier class and for token shapes before the push; FO pushes; FO checks a fresh clone.
- The deliverable is named here only as the private working repository and pinned by commit SHA; nothing from a run or a case is written to this state branch.
- bite: the result has no backup (reform session, message 94ecfb61).
- consumer: the reform session and the Captain reading the two tables; whoever continues the instrument.
Non-goals: carrying any raw run output; changing any grader, reading or table; the seed files' pre-existing identifier lines.
Budget: 1 implementation and 1 validation cycles
Stop condition: a carried file cannot be made clean without changing a table's content; a non-zero scan before the push; a suspected key.

## Acceptance criteria

**AC-1**: On a fresh clone of the remote main after the push, both readings' documents and final tables are present, every cell's `selfcheck` exits 0, and each table regenerates or is shown byte-identical to the laptop branch's committed table.
Verified by: a fresh clone's listing and `selfcheck` exit codes, and a digest comparison of each carried table with the laptop branch's file at the final tables' commit.

**AC-2**: The pushed range adds no raw run output and scans at zero in every identifier class and for token shapes.
Verified by: the scan's counts over exactly the pushed range and the changed-path listing.

## FO alignment

Alignment: not needed before implementation: the outcome is the reform session's sentence; the backlog gate records it under the grant.
Release review: not needed: maintenance of a private measurement repository.
