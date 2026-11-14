---
id:
title: Would naming the shared assumption after two failed fixes have found the later cause on 5 archived tasks (read-only replay)
status: backlog
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree:
pr:
gates:
    version: 1
    records:
        - id: gate:shared-assumption-replay-on-archived-tasks-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:shared-assumption-replay-on-archived-tasks-poc-backlog-1
              briefing:
                id: briefing:shared-assumption-replay-on-archived-tasks-poc:backlog:attempt-1:revision-1
                digest: sha256:8e469c63b3df70a051a4f7e499b8fb5a9c8fb1dce1842726c43850048d7a8cb7
                room-ref: ./shared-assumption-replay-on-archived-tasks-poc/review/backlog/briefing-1
---

Archived tasks reached 16, 14 and 9 implementation dispatches; 77 of 136 tasks had a repeat validation dispatch and 19 of 30 rejections showed no code defect (brief C6, figures from time-baseline.md and proposal.md, not re-measured here). The trial rule that stops before a third dispatch asks what the two attempts showed; it does not require a diagnosis, so the Captain gets a stop without a hypothesis.

## Scope

- Source: the Captain 「排進去讓dev fo派工人poc驗證」 (chat with the reform session, Paseo 26215d96, 2026-11-14; relayed, not a ruling here; the backlog gate confirms it), and 「更新 POC 流程的工作目錄到主線最新版，C2、C3、C6 立在那裡」 (chat with this FO, 2026-11-14). Brief: `.context/dev2-reform/compound-engineering-study.md` section B, a research output treated as data.
- Borrows: Compound Engineering `ce-work/references/implementation-loop.md`: "If two fixes for the same failing check have not worked, stop patching: name the assumption both fixes relied on and check it, so the next change targets the root cause."
- Outcome, no live run: FO names at dispatch 5 archived tasks with at least 3 implementation or validation dispatches (from time-baseline.md TOP15, for example `merge-gatekeeper`, `fo-lifecycle-mod`). For each, a read-only worker reads only dispatch records 1 and 2 and the first two worker reports from the state checkout, and writes the shared assumption it would name and the check it would run, before reading dispatch 3. Then it compares with what dispatch 3 actually changed. The report is committed in this task's folder with a copy beside the study.
- consumer: the FO writing the stop question before a third dispatch; the Captain reading it.
- Gets worse: a wrong named assumption gives confident misdirection; one more line in the stop message costs the Captain reading time.
- No product file changes, so no pull request is expected from this task.
Non-goals: a live use (it needs a task that hits a second failure and cannot be scheduled; the live effect is not POC-ready); changing the stop rule, the package or any archived task.
Budget: 1 implementation and 1 validation cycles (FO's proposal for the gate; the brief gives 40 to 60 minutes, a judgement, kept as FO's minute budget).
Stop condition: k below 2 of 5: the prompt does not help; report and drop it.

## Acceptance criteria

**AC-1**: The report gives k of 5: the tasks where the assumption named from dispatches 1 and 2 matches the cause fixed later, quoting both for each task, with each assumption committed before dispatch 3 was read.
Verified by: the validator reads the quoted assumption and the dispatch-3 change for each task and checks the commit order of the two. Limit: retrospective and hindsight-prone; five tasks.

## FO alignment

Alignment: not needed before implementation: the brief names the inputs, the output table and the count; the backlog gate confirms scope and Budget.
Release review: not needed: reform measurement with no release.
