---
id:
title: One command prints five numbers for a task from its state records, and the table for today's tasks
status: backlog
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree:
pr:
---

Today's reform work produced its numbers by hand, in a log. The package already holds a script that computes most of them from state records; no command prints them as one table per task.

## Scope

- Source: the reform session's scope 3 under the Captain's standing grant to the second dev2 FO (Paseo 26215d96, message 6dd41248, 2026-11-14); it reports that the Captain approved the order with "Go ahead with the plan." in its own conversation (relayed, not a ruling here). Admission is recorded by FO under the grant.
- Outcome: one command in the extracted package that prints, for one task from its state records, five numbers: minutes from dispatch to the first Captain-facing report, dispatches per stage, whether a criterion changed after design approval, questions put to the Captain, and total minutes split into machine time and waiting. It reuses the package's existing timeline script and does not rebuild it. First output: the table for the tasks the second dev2 FO ran on 2026-11-14.
- A number that cannot be computed from records that exist prints "not recorded" and is listed; no new record is invented.
- Where the work lands: the private working repository that holds the extracted package, named here only as that and pinned by commit SHA; commits and a merge there are inside the grant. The table for today's tasks reads the public state branches of this repository and holds no private name.
- consumer: the reform session and the Captain reading how a task went; bite: the five numbers for today's tasks exist only in a hand-kept log.
Non-goals: a dashboard; a gate that reads the numbers; new records.
Budget: 1 implementation and 1 validation cycles
Stop condition: one hour from dispatch; at half of that, one check whether the work still serves the stated goal; the existing script cannot give a number without a new record: print "not recorded" and move on.

## Acceptance criteria

**AC-1**: The command prints the five numbers, or "not recorded", for a named task from its state records, and the table for today's tasks.
Verified by: the validator runs the command on three of today's tasks and checks two numbers per task by hand against the state branch's commits and gate records. Limit: times come from commit and gate timestamps.

**AC-2**: The command adds no new record and reuses the existing timeline script.
Verified by: the candidate's diff and a run that leaves the state checkout unchanged.

## FO alignment

Alignment: not needed before implementation: the five numbers and the reuse are stated in the scope.
Release review: not needed: package tooling.
