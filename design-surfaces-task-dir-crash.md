---
title: design_surfaces.py check <task> crashes when a same-named task directory sits beside the task file
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

Filed from a package issue reported by the spacedock-dev/subspace-relay First Officer (found by its implementation worker on 2026-10-13); the Captain confirmed filing on 2026-10-14 (「確認」 to "should FO file relay #1 and #4?").

## Scope

- Reproduced 2026-10-14 on kc-dev-flow-2 0.22.1: from the state checkout root, `python3 <package>/scripts/design_surfaces.py check followup-dispatch-records-checked` raises `IsADirectoryError: [Errno 21] Is a directory: 'followup-dispatch-records-checked'`; the same command with `followup-dispatch-records-checked.md` works. Every task with dispatch records has a `<task>/` directory beside `<task>.md`, and the workflow README tells FO and workers to run `design_surfaces.py check <task>` and `check --seed <task>`.
- Candidate fix: resolve `<task>` to `<task>.md` when the argument is a directory or has no suffix, or fail with a usage message; a test for the directory case.
- Non-goals: to be set at ideation.

## Acceptance criteria

To be written at ideation.

## FO alignment

Alignment: not needed before ideation; the Captain confirmed filing it.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
