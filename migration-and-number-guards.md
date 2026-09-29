---
title: An applied migration is never edited, and parallel tasks never pick the same migration or ADR number
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:migration-and-number-guards:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:migration-and-number-guards-backlog-1
              briefing:
                id: briefing:migration-and-number-guards:backlog:attempt-1:revision-1
                digest: sha256:ef34424671bef98e8094e1614440348a9c83b4777ac1fac9f4eac2283820fa41
                room-ref: ./migration-and-number-guards/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:migration-and-number-guards:backlog:1
                briefing: briefing:migration-and-number-guards:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-29T23:28:15.323516Z"
                decision: approve
                reason: 'Captain 2026-09-30: 「可以」 to the FO''s dev2 fix batching, batch A first'
              application:
                target-stage: ideation
                state: consumed
---

Two adopter defects from qnow dogfooding (2026-09-29) that dev2 never checked: an unmerged migration edited in place after it reached a persistent database, and parallel tasks choosing the same migration and ADR numbers.

## Scope

Captain 2026-09-30, approving the FO's batching of the dev2 fixes: 「可以」 — batch A (guardrails) first. This task covers issues #524 and #523.
Evidence (qnow, 2026-09-21..29): qnow migration 0005 was edited by PR #1207 after production applied it (PR #1204), and every production deploy failed with "migration has been modified after being applied" for about a week unnoticed; the uat branch database stuck the same way when an unmerged 0012 was edited after a uat deploy; two unmerged tasks both created migration 0012; ADR numbers 0021–0028 were reassigned several times. Netlify's documentation: never edit an applied migration; revert and add a new one; the production branch cannot be reset, non-production branches can.
Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Needed at ideation: how a stage detects that a candidate changes a migration file that already exists on the base branch (an adopter-configured migrations path, checked in implementation and validation), what counts as "reached a shared environment" for an unmerged migration, and how the FO reserves the next migration and ADR number per task at dispatch and delivery re-checks it against the base branch.
Result: the FO delegates these questions to ideation, which decides each with its source and returns any ruling that needs the Captain.
Surfaces: none
Visible change: none
