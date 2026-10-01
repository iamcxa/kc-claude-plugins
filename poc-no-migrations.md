---
title: A POC task adds or edits no migration file, and POC delivery checks the migrations directory is unchanged
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:poc-no-migrations:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:poc-no-migrations-backlog-1
              briefing:
                id: briefing:poc-no-migrations:backlog:attempt-1:revision-1
                digest: sha256:e389818b33a780a92218611ad1159a107a101bd23466415e2870916cf2e0c86a
                room-ref: ./poc-no-migrations/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:poc-no-migrations:backlog:1
                briefing: briefing:poc-no-migrations:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-01T05:16:53.369004Z"
                decision: approve
                reason: 'Captain 2026-10-01: 「ok」 — POC touches no migration file; a task needing one is promoted to pilot; POC delivery checks the migrations directory is unchanged'
              application:
                target-stage: ideation
                state: consumed
started: 2026-10-01T05:17:00Z
---

The POC route never activates number guards (it records no `Surfaces:`), so a POC migration would get no reserved number and no freeze; the Captain ruled that a POC does not touch migrations at all.

## Scope

Captain 2026-10-01: 「ok」 to the FO's proposal: a POC task adds and edits no migration file; a task that needs a database change is promoted to pilot; POC delivery runs the existing number-guards check plus a check that the migrations directory is unchanged. Same ruling waives the external reviewer's round-4 P1 on qnow PR #1248 ("Activate number guards for POC database work", on the derived `docs/dev2-poc/README.md`) for that sync PR, reason recorded: the gap predates the sync (the POC README had no number guards before it either), so merging does not widen it; this task closes it in the package.
Evidence: kc-dev-flow-2 0.10.3 `references/sd/workflow.md` `## Number guards` applies "when the task's `Surfaces:` includes `db`, or its design lands an ADR"; `Surfaces:` is recorded only on the five-stage route; the POC route derived by `poc_readme.py` has no ideation stage.
Non-goals: full number guards on the POC route; any Spacedock change.

## Acceptance criteria

To be written at ideation.

## FO alignment

Needed at ideation: where the POC rule lives (the template text that `poc_readme.py derive` keeps for the POC route, and the stage that delivers a POC); how the "migrations directory unchanged" check runs (an existing `number_guards.py` mode, a flag, or a few lines) with `migrations-path:` from the README; what happens when it fails (the task is promoted to pilot, not repaired in place); tests with a falsifier.
Result: the FO delegates these questions to ideation, which decides each with its source and returns any ruling that needs the Captain.
Surfaces: none
Visible change: none
