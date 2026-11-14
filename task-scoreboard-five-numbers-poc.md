---
id:
title: One command prints five numbers for a task from its state records, and the table for today's tasks
status: validation
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree: .worktrees/spacedock-ensign-task-scoreboard-five-numbers-poc
pr: local-merge:7e0f9c242e642eeb1d341527156a0acc9fca90ce
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
        - id: gate:task-scoreboard-five-numbers-poc:validation
          stage: validation
          attempts:
            - id: gate-attempt:task-scoreboard-five-numbers-poc-validation-1
              briefing:
                id: briefing:task-scoreboard-five-numbers-poc:validation:attempt-1:revision-1
                digest: sha256:001487075d0a57c180a60dfc98c075bc7e5ff518748ec11b598d335c89d3c5fb
                room-ref: ./task-scoreboard-five-numbers-poc/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:task-scoreboard-five-numbers-poc:validation:1
                briefing: briefing:task-scoreboard-five-numbers-poc:validation:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-11-14T12:35:01.720357Z"
                decision: approve
                reason: The reform session ruled option 2 for item C and told FO to merge and close; inside scope 3 under the Captain's grant; the merge is to the private working repository, not a public one.
                conn:
                    quote: 改革工作階段（Paseo 代理 26215d96，就是開你出來的那一個）可以替我給你工作範圍。它給的範圍內，進場、設計、預算、結案這些關卡你不必停下來等我，記為「依艦長授權」，一路做到它指定的終點。
                    source: the Captain, chat with the second dev2 FO, 2026-11-14; scope 3 item C from the reform session, Paseo messages 6dd41248-d90d-4c35-ba36-bc70f9e033d7, f998e663-9bd3-4fdb-a35a-dddf5338b619 and 4d23dc58-a0ba-4c5a-8134-129dbfed2ca5
              application:
                target-stage: done
                state: pending
started: 2026-11-14T12:18:32Z
mod-block: merge:pr-merge
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
## Stage Report: implementation

- DONE: One command in the extracted package prints five numbers for a task read from a state checkout given as an argument, reuses the timeline script, prints "not recorded" for a number with no record, and writes nothing to the state checkout
  `scripts/task_scoreboard.py` (223 lines) imports `task_timeline.timeline` and adds only the reading of its result, one `git log` for the approval commit, and one `git show` per task; no timeline code copied. No-write: `find -newer` a pre-run stamp listed no file in either state checkout or git directory; git status unchanged (evidence/implementation-1/falsifier-and-no-write.txt).
- DONE: The table for the tasks the second dev2 FO ran on 2026-11-14, read from the two public state branches, saved in the candidate and pasted here; the numbers that came out "not recorded" and the record each needs
  Saved as `docs/scoreboard/2026-11-14.md` (copy: evidence/implementation-1/scoreboard-2026-11-14.md). Read at spacedock-state/dev2-poc @ de67f8c52af7 and spacedock-state/dev2 @ 76fa1cccb514, 2026-11-14T12:23Z. Table pasted below.
- DONE: A local commit on the assigned branch with the configured git identity unchanged; branch, base and candidate SHA reported; the limits of the numbers
  Branch `task-scoreboard`, base `2b391a40f926646b6be949cb2cf07466005e277c`, candidate `5e88c9ffe4e49ea3ebc80df45d00d381aee6bd46`; author is the configured identity (no `git config` write); not pushed. Limits are below and in the table file.

Table (unedited command output; the three running rows are measured to the read time):

| task | 1 first report (min) | 2 dispatches | 3 criterion changed | 4 questions | 5 minutes |
|---|---|---|---|---|---|
| extracted-package-real-use-routes-probe-poc | not recorded | backlog 0, implementation 1 | no: 2 criteria unchanged since backlog approval | 1 gate briefings; asks outside a gate: not recorded | 3.8 total = 3.7 machine + 0.1 waiting (running) |
| method-reading-code-and-tables-on-the-private-remote-poc | 12.8 | backlog 0, implementation 1, validation 1 | no: 2 criteria unchanged since backlog approval | 2 gate briefings; asks outside a gate: not recorded | 13.1 total = 12.9 machine + 0.2 waiting |
| private-cell-selfcheck-passes-on-a-fresh-clone-poc | 17.7 | backlog 0, implementation 1, validation 1 | no: 2 criteria unchanged since backlog approval | 2 gate briefings; asks outside a gate: not recorded | 17.9 total = 17.7 machine + 0.2 waiting |
| readme-rule-retirement-audit-poc | 149.0 | backlog 0, implementation 2, validation 1 | no: 1 criteria unchanged since backlog approval | 2 gate briefings; asks outside a gate: not recorded | 154.6 total = 149.1 machine + 5.5 waiting |
| shared-assumption-replay-on-archived-tasks-poc | 125.0 | backlog 0, implementation 1, validation 1 | no: 1 criteria unchanged since backlog approval | 2 gate briefings; asks outside a gate: not recorded | 130.7 total = 125.1 machine + 5.6 waiting |
| task-scoreboard-five-numbers-poc | not recorded | backlog 0, implementation 1 | no: 2 criteria unchanged since backlog approval | 1 gate briefings; asks outside a gate: not recorded | 3.7 total = 3.6 machine + 0.1 waiting (running) |
| test-value-pass-on-route-trial-prs-poc | 124.4 | backlog 0, implementation 1, validation 1 | no: 1 criteria unchanged since backlog approval | 2 gate briefings; asks outside a gate: not recorded | 130.4 total = 124.7 machine + 5.7 waiting |
| state-branch-writes-carry-no-private-identifiers | 28.1 | backlog 0, ideation 1, implementation 1, validation 1 | no: 5 criteria unchanged since ideation approval | 3 gate briefings; asks outside a gate: 1 | 203.5 total = 178.9 machine + 24.6 waiting |
| gate-text-and-sealed-evidence-carry-no-home-path-or-private-repo | 29.2 | backlog 0, ideation 1, implementation 1, validation 1 | no: 5 criteria unchanged since ideation approval | 2 gate briefings; asks outside a gate: not recorded | 149.2 total = 149.0 machine + 0.2 waiting (running) |
| extracted-package-says-five-rules-that-worked | not recorded | backlog 0, ideation 1 | no: 3 criteria unchanged since backlog approval | 1 gate briefings; asks outside a gate: not recorded | 4.0 total = 3.9 machine + 0.1 waiting (running) |

Not recorded, with the record each would need:
- number 4, asks outside a gate: 9 of 10 tasks have no `asks.jsonl`; needed: an `asks.jsonl` entry written when the FO asks outside a gate. Only state-branch-writes-carry-no-private-identifiers has one (1 ask). A task with no file may have had no ask or an unrecorded one; the absence cannot tell which.
- number 1, first report: three tasks have no gate briefing or ask after their first dispatch yet (extracted-package-real-use-routes-probe-poc, task-scoreboard-five-numbers-poc, extracted-package-says-five-rules-that-worked); needed: nothing new, the briefing is not opened yet.

Difference from the dispatch: the spawn message said every task on the dev2-poc state branch ran today; 26 are on it and 7 started 2026-11-14 (local day, +08:00). The other 19 (one has no stage, 18 started 2026-09-22 to 2026-10-26) are left out of the table. `--since` takes any start if the Captain wants them.

Limits: times come from state-commit author dates and gate resolution timestamps; machine time includes idle time within a stage; a gate the FO resolved under a standing grant counts as waiting, so "waiting" is not always the Captain's time; running rows are measured to the read time; number 3 sees an edit to a `**AC-n**` block, not an amendment that changes a criterion without editing it; number 1 counts a gate briefing opened after a dispatch, so a task whose first report is its validation gate includes the whole implementation.

Checks run: hand check of two numbers on two tasks against the state commit log (method-reading-code-and-tables-on-the-private-remote-poc: implementation dispatch 19:51:42 to validation briefing 20:04:31 = 12.8 min, waiting 0.1 + 0.1 = 0.2; state-branch-writes-carry-no-private-identifiers: ideation dispatch 12:43:29 to ideation briefing 13:11:35 = 28.1 min). Number 3 falsifier: an AC-1 edit in a scratch clone prints "yes: AC-1 differ since backlog approval"; the unedited task prints "no". Not run: roborev (the candidate is in a different private repository), any test suite (none carried; the assignment asked for none beyond trusting the output), validation by someone other than me.

Scratch close: not run (see Summary).

### Summary

One command, `scripts/task_scoreboard.py`, prints the five numbers per task from the existing timeline script's result and the state history, and the 2026-11-14 table is saved in the candidate. The weak number is 4: nine of ten tasks have no `asks.jsonl`, so asks outside a gate print "not recorded". This report is a draft in scratch: both writes into the state checkout (evidence copy, then this report) were denied by the permission classifier, so FO needs to land it.

## Stage Report: validation

Verdict: PASSED. AC-1 and AC-2 hold at candidate b000ffce22a0 (base 2b391a40f926), branch `task-scoreboard` in the private working repository. Two reader risks are listed below; neither changes a number.

- DONE: AC-1, independent run and hand check on three finished tasks, two numbers each
  Ran `python3 -B scripts/task_scoreboard.py <state> <task>` (one-task mode) and a five-task table on spacedock-state/dev2-poc @ 9fed3682138c, and one-task plus `--since 2026-11-13T16:00:00Z` on spacedock-state/dev2 @ 010a6b7bd532, 2026-11-14T12:29Z, then again at 12:32Z; every run exited 0. Hand checks against state-commit author dates, briefing-room first commits and gate `at` values (local +08:00):
  method-reading-code-and-tables-on-the-private-remote-poc (dev2-poc). Number 1: implementation dispatch 19:51:42 to validation briefing room 20:04:31 = 12 min 49 s = 12.8; printed 12.8. Number 2: one `dispatch: … entering implementation` and one `… entering validation` commit = implementation 1, validation 1; printed the same.
  readme-rule-retirement-audit-poc (dev2-poc). Number 1: implementation dispatch 10:35:03 to validation briefing room 13:04:03 = 149 min 0 s = 149.0; printed 149.0. Number 2: implementation 2 comes from two dispatch records (dispatch/implementation-1.md, implementation-2.md), though the commit log carries only one `entering implementation` subject; validation 1. Printed implementation 2, validation 1.
  state-branch-writes-carry-no-private-identifiers (dev2). Number 1: ideation dispatch 12:43:29 to ideation briefing room 13:11:32 = 28 min 3 s = 28.05, printed 28.1. Number 5 waiting: backlog 12:42:27 to gate `at` 12:42:30.2 = 0.05; ideation 13:11:32 to 13:11:35.5 = 0.06; validation 15:36:27 to 16:00:53.8 = 24.45; the script rounds each stage to 0.1 + 0.1 + 24.4 = 24.6; printed 24.6 (unrounded sum 24.56). Number 4 also checked: 3 briefing rooms (backlog, ideation, validation) and asks.jsonl with 1 line; printed "3 gate briefings; asks outside a gate: 1".
  Saved table against the fresh run: every finished row in docs/scoreboard/2026-11-14.md matches the fresh run cell for cell (the five finished dev2-poc rows and state-branch-writes-carry-no-private-identifiers). Running rows differ only in their minutes, as the file says they will.
- DONE: AC-2, reuse and no write
  The diff from base to candidate adds two files only, scripts/task_scoreboard.py (228 lines) and docs/scoreboard/2026-11-14.md (55 lines); scripts/task_timeline.py has a 0-line diff. The script does `import task_timeline as tl` and takes its times from `tl.timeline`, `tl.when`, `tl.mins` and `tl.find_task`. Its own code is read-only git: one `git log` to find the approval commit, `git show` of the task file at that commit, and `rev-parse` and `branch`. No timeline logic is copied. No-write, run twice, each time with a stamp made before the runs: `find -newer stamp` over both state checkouts and both git directories listed 0 files, HEAD and `git status --porcelain` (0 lines) were unchanged in both, and the candidate worktree's status was unchanged too (runs used `python3 -B`).
- DONE: Plain-words line on "first report" and "waiting"
  The line starting "Read with care:" prints in one-task mode (last line) and in table mode (under the state header), and appears twice in the saved table (once per branch). It does not print with `--json`. That mode is not one of the two the AC names, but a reader of JSON output does not get the warning.
- DONE: Limits of this check and what could mislead a reader
  1. Which dev2 tasks are in the saved table is not explained. The dev2 table names three tasks by hand. A `--since 2026-11-13T16:00:00Z` run on the same branch returns seven tasks that started today. The other four are behaviour-baseline-first-cell, captain-question-outside-a-gate-is-an-open-record, first-method-against-no-method-reading and architecture-documents-have-a-layout-and-each-fact-one-home. The scope says "tasks the second dev2 FO ran", but the state records do not say which FO ran a task, so I could not check the selection, and the saved file does not give the rule. A reader could take the dev2 table to be the whole day.
  2. Number 5 rounds each stage to 0.1 min before adding, so a total can be 0.1 above the unrounded sum: method-reading-code-and-tables-on-the-private-remote-poc prints 13.1 total, and the stages sum to 13.03 unrounded.
  3. `--json` must come before the task names. `--json <task>` after the state path fails with "unrecognized arguments" (exit 2, run-json-order.txt), and `<state> <task> --json` works.
  4. The script's own limits still hold: times are commit author dates; "waiting" includes gates the FO resolved under a grant; number 3 sees only edits to `**AC-n**` blocks.
  I hand-checked 7 numbers on 3 tasks. I did not check number 3 by hand, I re-ran no falsifier, I read no task from another day, and I ran no test suite (the candidate carries none). roborev was not run.
- DONE: Scratch close
  Output: "Scratch removed: …/validation-1 (24824 bytes)" and "Evidence: evidence/validation-1/ (0 files, 0.0 KiB)", exit 0. It deleted the first report draft and run logs. I re-ran the runs and the no-write check into a sibling folder, validation-1-out, at 12:32Z with the same results. The numbers above come from both runs. The intermediate raw timeline dump is gone, and its values are quoted inline above.
  Logs (validation-1-out): run-one-poc.txt, run-table-poc.txt, run-one-dev2.txt, run-table-dev2.txt, run-json-order.txt, state-commits.txt, briefing-commits.txt, pre.txt, post.txt, newer.txt. Not archived (private): the candidate script and its diff; reproduce: `git diff 2b391a40f926 b000ffce22a0` in the private working repository.

### Summary

The command prints the five numbers or "not recorded" for a named task, and the table. Seven hand-checked numbers on three finished tasks from both state branches match. The saved table's finished rows equal a fresh run. The candidate imports the timeline script unchanged, and a run wrote nothing to either state checkout. Reader risk: the saved dev2 table holds 3 of the 7 tasks that started there today, and the file does not say why.
