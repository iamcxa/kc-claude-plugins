---
title: FO's idle check names each backlog task whose seed check fails before its gate is prepared
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:idle-names-failing-seeds:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:idle-names-failing-seeds-backlog-1
              briefing:
                id: briefing:idle-names-failing-seeds:backlog:attempt-1:revision-1
                digest: sha256:7c87384f34520e309482b27e2f4e058013380194f7803458e4c9202129d212ec
                room-ref: ./idle-names-failing-seeds/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:idle-names-failing-seeds:backlog:1
                briefing: briefing:idle-names-failing-seeds:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-21T07:28:54.464776Z"
                decision: approve
                reason: Captain 「繼續」 (chat, 2026-10-21), answering FO's question 「這 5 張都批准進入設計嗎？」 for the five batch-5 backlog gates presented together; approves entering ideation under the pilot profile, as recommended.
              application:
                target-stage: ideation
                state: consumed
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
