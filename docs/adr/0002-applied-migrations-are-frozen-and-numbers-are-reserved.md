# 0002. An applied migration is frozen and each task holds its own migration and ADR number

Date: 2026-09-30

## Status

Accepted

## Context

An adopting project ran kc-dev-flow-2 tasks against a database that checksums each migration file (Netlify Database, "Migration modified after being applied": never edit an applied migration; revert and add a new one). Observed 2026-09-21 to 2026-09-29: a comment-only trim of an already-applied migration made every production deploy fail for about a week unnoticed; a migration edited after a deploy to a non-production shared branch database left that database stuck; two unmerged tasks each created migration 0012; ADR numbers were reassigned several times.

On `main` at `b753d344` (read 2026-09-30), nothing in the package compared a candidate's migration files with the base branch, and nothing stopped two tasks from picking one number. `adr_lint.py` sees duplicate ADR numbers inside one tree only. Spacedock 0.27.2 has no migration or number concept.

## Decision

**Words:** 「准」 — Captain, 2026-09-30, at the ideation gate; the gate record adds that a migration already applied at a non-production shared environment is renumbered by resetting that database branch through Netlify's database-branch reset API instead of a compensating migration.

**Options considered:**
- a stdlib `number_guards.py` with `check` and `reserve`, a `## Number guards` workflow section and two optional workflow-README keys (`migrations-path:`, `adr-path:`)
- prose in the FO mod as carlove's plan-based immutability check does — rejected; a plan check misses an unplanned edit, and prose is not tested
- a check on the meaning of the SQL change — rejected; the checksum covers every byte, so a comment trim breaks a deploy
- a compensating migration for the renumber of an applied file — rejected by the Captain; reset the non-production branch database instead, documented, no wrapper built

A candidate that modifies or deletes a migration file present at its merge-base with the base branch, or present in a commit recorded as `Applied at: <environment> <sha>`, fails `check`; the fix is a new migration. The First Officer reserves a migration and an ADR number per task before implementation with `reserve`, and `check` reruns at implementation exit, at validation and against the fetched base tip before merge.

## Consequences

An edit to an applied migration now fails at three call sites instead of at a production deploy. Not covered: a deploy nobody recorded as `Applied at:`, migrations not named `NNNN_name.sql`, snapshot and journal files, and timestamp-numbered adopters. Whether the FO runs `reserve` at dispatch is an instruction that validation reads back from the task's `## Number guards` lines. Reopen if an unrecorded deploy breaks an environment, or if a task needs more than one number per kind.
