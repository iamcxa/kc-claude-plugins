---
id:
title: The private working repository's second laptop cell passes its selfcheck on a fresh clone and says which entries it could not check
status: backlog
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree:
pr:
gates:
    version: 1
    records:
        - id: gate:private-cell-selfcheck-passes-on-a-fresh-clone-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:private-cell-selfcheck-passes-on-a-fresh-clone-poc-backlog-1
              briefing:
                id: briefing:private-cell-selfcheck-passes-on-a-fresh-clone-poc:backlog:attempt-1:revision-1
                digest: sha256:d60d609f5b565d908092d85bb63baf775817973bdd48819fbc7e1119c62fb6ac
                room-ref: ./private-cell-selfcheck-passes-on-a-fresh-clone-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:private-cell-selfcheck-passes-on-a-fresh-clone-poc:backlog:1
                briefing: briefing:private-cell-selfcheck-passes-on-a-fresh-clone-poc:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-11-14T11:32:29.518367Z"
                decision: approve
                reason: Ordered by the reform session under the Captain's grant as the first step after the two-hour scope; small, private-repository maintenance; no public merge or outward action.
                conn:
                    quote: 改革工作階段（Paseo 代理 26215d96，就是開你出來的那一個）可以替我給你工作範圍。它給的範圍內，進場、設計、預算、結案這些關卡你不必停下來等我，記為「依艦長授權」，一路做到它指定的終點。
                    source: the Captain, chat with the second dev2 FO, 2026-11-14; scope 2 as continued by the reform session, Paseo messages c998ccf1-0e7d-4197-9636-a25f2818c562 and c271575d-82b3-4a1b-a945-c7df85cea4da
              application:
                target-stage: implementation
                state: pending
---

The clean branch pushed to the private working repository's remote on 2026-11-14 carries a cell whose `selfcheck` exits 1 on a fresh clone: nine of its fixture entries point at raw laptop outputs that are deliberately not carried. A check that fails on a fresh clone is a trap for whoever clones it next.

## Scope

- Source: the reform session's rulings under the Captain's standing grant to the second dev2 FO (Paseo 26215d96, messages c998ccf1 and c271575d, 2026-11-14): "carry a variant whose selfcheck exits 0 on the remote copy and SAYS which entries it could not check and why (printed, not skipped in silence), re-scan, push", first in the order after the two-hour scope. Admission is recorded by FO under that grant.
- Outcome: on a fresh clone of the private working repository's remote main, every cell's `selfcheck` exits 0; for the second laptop cell it prints, by name and count, the entries it could not check and why (their raw outputs stay on the laptop), and it still fails when a carried fixture's grade is wrong. On the laptop, where the raw outputs exist, the same cell still checks all of its entries.
- The deliverable is in the private working repository, named here only as that and pinned by commit SHA; nothing from a run or a case is written to this state branch. Before the push the range is scanned for the identifier classes and token shapes and reads zero; FO pushes.
- bite: a fresh clone's `selfcheck` exit 1 (FO and worker observation, 2026-11-14, reported to the reform session before the push).
- consumer: whoever next clones the private working repository, the reform session first.
Non-goals: carrying any raw run output to the remote; changing any grader, reading or committed table; the seed files' pre-existing identifier lines (recorded separately as a blocker for any public release).
Budget: 1 implementation and 1 validation cycles
Stop condition: the variant cannot exit 0 without hiding a real fixture failure; a non-zero scan before the push; a suspected key.

## Acceptance criteria

**AC-1**: On a fresh clone of the remote main after the push, `selfcheck` exits 0 for every cell and prints which entries of the second laptop cell were not checked and why; with one carried fixture's expected grade altered in a scratch copy it exits 1.
Verified by: the validator's own fresh clone, the three commands' exit codes and the printed count; the mutation run in scratch.

**AC-2**: The pushed range adds no raw run output and scans at zero in every identifier class and for token shapes.
Verified by: the scan's counts over exactly the pushed range and a listing of the changed paths, re-run by the validator.

## FO alignment

Alignment: not needed before implementation: the outcome is the reform session's sentence; the backlog gate records it under the grant.
Release review: not needed: maintenance of a private measurement repository.
