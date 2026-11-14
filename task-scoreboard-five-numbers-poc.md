---
id:
title: One command prints five numbers for a task from its state records, and the table for today's tasks
status: implementation
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree:
pr:
gates:
    version: 1
    records:
        - id: gate:task-scoreboard-five-numbers-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:task-scoreboard-five-numbers-poc-backlog-1
              briefing:
                id: briefing:task-scoreboard-five-numbers-poc:backlog:attempt-1:revision-1
                digest: sha256:d79a6a484046d635be0597dea341dd8c06c656b0ea5d9851bc164947b3dd7011
                room-ref: ./task-scoreboard-five-numbers-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:task-scoreboard-five-numbers-poc:backlog:1
                briefing: briefing:task-scoreboard-five-numbers-poc:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-11-14T12:16:17.208155Z"
                decision: approve
                reason: Inside scope 3 given by the reform session under the Captain's grant; no public merge, outward action, outcome-definition change or suspected key is involved in admission.
                conn:
                    quote: 改革工作階段（Paseo 代理 26215d96，就是開你出來的那一個）可以替我給你工作範圍。它給的範圍內，進場、設計、預算、結案這些關卡你不必停下來等我，記為「依艦長授權」，一路做到它指定的終點。
                    source: the Captain, chat with the second dev2 FO, 2026-11-14; scope 3 from the reform session, Paseo message 6dd41248-d90d-4c35-ba36-bc70f9e033d7
              application:
                target-stage: implementation
                state: consumed
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
