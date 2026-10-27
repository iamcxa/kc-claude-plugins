---
title: A Captain amendment entry is refused when it sits outside ## Captain amendments, rewrites an earlier entry, or its Supersedes line carries FO prose instead of criterion ids
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「全准」 (chat, 2026-10-28), answering FO's batch-8 closing sitting, item 二 (open two package tasks so a check refuses what FO kept getting wrong).
- Bite: batch-8 observer reports (2026-10-28): amendment 2 written under ## Number guards (seed-check-requires-schema-fields) and a Feedback Cycles block parsed as an amendment (idle-hook-names-merged-tasks-without-learn); FO rewrote amendment 1's Supersedes line (read-adr-honors-adr-folder); FO's Supersedes summary dropped the accepted no-repeat words (idle-hook-names-merged-tasks-without-learn, which caused its AC-8 conflict); an accepted limit recorded as an amendment only after the observer flagged it (read-adr-honors-adr-folder). learn evaluations: each is an existing README rule FO did not follow.
- Upstream first: README ## Captain amendments, `scripts/design_surfaces.py` (`check_amendments`), `scripts/dispatch_records.py`.

## Non-goals

- Checking prose quality or whether a summary is faithful; only the structure the README already states.

## Budget

- One package PR; no new script.

## Stop condition

- The check refuses each bite in the replay and passes every current task file that follows the README.

## FO alignment

Alignment: needed before ideation; where the check runs is a package design choice.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
