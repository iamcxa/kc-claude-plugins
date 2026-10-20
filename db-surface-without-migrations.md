---
title: A db task in a repository with no migration files passes the number guard, declared once by the adopter
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:db-surface-without-migrations:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:db-surface-without-migrations-backlog-1
              briefing:
                id: briefing:db-surface-without-migrations:backlog:attempt-1:revision-1
                digest: sha256:fda81c6b7519c20de7d3f14d7920bdbe76020cf4f046d1f059cc203b30a50520
                room-ref: ./db-surface-without-migrations/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:db-surface-without-migrations:backlog:1
                briefing: briefing:db-surface-without-migrations:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-20T04:56:38.496698Z"
                decision: approve
                reason: Captain approved the five batch-4 backlog gates presented together in chat (「按你建議」), answering FO's question put before it (quoted in the gate question); this briefing binds that question and answer after the fact
              application:
                target-stage: ideation
                state: consumed
started: 2026-10-20T04:57:48Z
---

## Scope

- Source: issue iamcxa/kc-claude-plugins#678 (filed 2026-10-19 at the Captain's request from the relay dev2 FO's learn candidates); batch 4 approved 2026-10-20 (「按你建議」).
- Bite: `number_guards.py check` raises `Misconfigured("task has Surfaces: db but no migrations-path is declared ...")` and exits 2 on a repository whose `db` surface has no migration files (subspace-relay: Netlify Blobs keys). The README makes exit 2 a hold, so the relay FO dispositioned it by hand in four validation rounds of own-comments-follow-account, and the observer recorded `can't tell`. `references/sd/workflow.md` also says "Without `migrations-path:` the migration rules are skipped", which contradicts the exit-2 path for a db task (triage 2026-10-20 on origin/main ad44f0cb).
- Consumer: every adopter FO whose db surface has no migration directory (relay today) and the observer reading that hold.
- Direction from the issue, to be measured at ideation: an explicit, observer-visible declaration (for example `migrations-path: none` with a reason) rather than a silent skip.
- Batch overlap: fo-batch-sittings touches the Number guards passage of the README (the reservation-timing conflict); order this task's implementation first.
- Non-goals: to be set at ideation.

## FO alignment

Alignment: not needed before ideation; the Captain approved batch 4.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
