---
title: FO's idle check names each backlog task whose seed check fails before its gate is prepared
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain's 「開」 (chat, 2026-10-21) to FO's batch-4 close question 「D 要不要開成任務？」, on FO's proposal 「讓 FO 每次例行檢查時跑的 `pr_watch.py tasks`，順便列出種子檢查沒過的待辦任務，FO 開閘門前就會看到」.
- Bite: the README's Seed check ("before `gate prepare`, FO runs `design_surfaces.py check --seed <task>` and holds the gate until it exits 0") was skipped three times in batch 4: observer findings on commissioned-by-names-spacedock and fo-batch-sittings (replay exit 1, "'Visible change:' is not 'none' but 'Surfaces:' has no 'ui'"), and the dev2-poc task interrogation-replay-on-batch-3-poc.
- Shape asked for: `pr_watch.py tasks` prints one `next:` line naming each backlog task whose seed check fails; no new script. It reminds and does not stop `spacedock gate prepare`, which this package cannot change.
- Upstream first: Spacedock `gate prepare` (no hook for an adopter check), `design_surfaces.py check --seed`, the `pr_watch.py tasks` sitting line from fo-batch-sittings (ADR 0028).
- Non-goals: blocking `gate prepare`; candidates E and F of the same list.

## FO alignment

Alignment: not needed before ideation; the Captain chose the shape.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
