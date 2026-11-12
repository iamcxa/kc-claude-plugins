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
- Trial (2026-11-13): admitted by the Captain's 「五張都准，授權代記設計關卡（建議）」 (host question dialog, 2026-11-13) as one of five tasks run by hand under the trial route rules: one worker builds a working probe during ideation and continues into implementation, a different worker validates, at most 3 build rounds counted by hand; stop for the Captain on an overturned premise, spent budget, two rounds without progress or a second validation rejection, a change of scope or criterion, or a component boundary or Prod trigger.

## Acceptance criteria

To be written at ideation.

## Budget
1 implementation and 2 validation cycles, in one package PR.

## Stop condition
- The recorded command, run from a state checkout root where a same-named directory sits beside the task file, no longer raises IsADirectoryError and checks the task file; a test covers the directory case.

## FO alignment

Alignment: not needed before ideation; the Captain confirmed filing it.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
