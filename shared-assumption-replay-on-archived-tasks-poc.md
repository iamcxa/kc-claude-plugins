---
id:
title: Would naming the shared assumption after two failed fixes have found the later cause on 5 archived tasks (read-only replay)
status: validation
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree: .worktrees/spacedock-ensign-shared-assumption-replay-on-archived-tasks-poc
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
              resolution:
                type: Resolution
                id: resolution:spacedock:shared-assumption-replay-on-archived-tasks-poc:backlog:1
                briefing: briefing:shared-assumption-replay-on-archived-tasks-poc:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-14T02:33:38.87005Z"
                decision: approve
                reason: 'Captain 「三張都准入，預算照你的提議」 (chat with this FO, 2026-11-14) to the bound backlog question: selects profile poc and accepts outcome, Non-goals, Stop condition, AC-1 and the Budget of 1 implementation and 1 validation cycles as filed.'
              application:
                target-stage: implementation
                state: consumed
started: 2026-11-14T02:35:18Z
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


## Stage Report: implementation

- DONE: For each of the 5 named archived tasks: reading only dispatch records 1 and 2 of the repeated stage and the first two worker reports, the shared assumption you would name and the check you would run, committed to the state branch BEFORE you open dispatch 3 or anything later
  Final counted set uses implementation; FO commit c24854032f31aa6281810d7d0c492ebb206d1f6d freezes implementation/assumptions.md and v2 input records before all five third-dispatch reads (evidence/implementation-1/freeze-receipt-v2.json, third-dispatch-read-log.json). Allowed report leakage is disclosed, not called temporal blindness.
- DONE: Then, per task, what dispatch 3 actually changed, quoted beside your named assumption, and whether they match
  implementation/report.md and evidence/implementation-1/comparison.json retain all five frozen hypotheses, dispatch-3 quotes, outcome quotes and causal-match reasons; investigation-only requests are distinguished from later committed repairs.
- DONE: The count k of 5 with the stop condition applied: k below 2 means the prompt does not help
  Literal causal-quote k=2/5 (laws historical bytes; verdict qualified labels), so the numeric drop condition does not fire; 0 independent blind predictions demonstrated is evidence coverage, not measured accuracy or efficacy (counts.json, applicability.json).
- DONE: Keep ui-design-review-in-ideation in the report as contaminated, outside the count of 5, with what exposed it.
  The required learning.md read exposed its later fence-blind Surfaces/corpus-verdict repair; comparison.json retains the exclusion and the original frozen hypothesis remains unchanged.
- DONE: Replace it with the next task in rework-round order that has saved dispatch records and that no learning note you have read names: delivery-gate-verdict-form, then extension-instruction-reaches-dispatch, then followup-dispatch-records-checked. Say which you took and why any was skipped.
  Took the first, delivery-gate-verdict-form, absent from the learning note read; no candidate was skipped and the other two were not reached. Its separate cross-task mention and later-report leakage are disclosed.
- DONE: The count stays k of 5 over five blind rows; all five named assumptions are committed before any dispatch 3 is opened.
  Five counted tasks were third-dispatch-file-blind at c2485403; all hypotheses/checks match committed bytes. Historical temporal blindness is not established because permitted report 2 often already contains post-dispatch-2 work; no stronger blind-prediction claim is made.
- DONE: Verify source integrity, aggregation and product/archive boundaries
  verify-replay.json passes source hashes, quote lines, freeze bytes, task set, recorded ordering and count consistency; changed-hypothesis and changed-quote scratch controls both fail as expected (integrity-controls.json). Semantic grading is manual; final-boundaries.json shows unchanged clean product c2f035b6612f5edb42220576b3414e993531ffd6 and unchanged inspected archive paths.
- DONE: Run the applicable exit checks and close scratch
  comment_ratio.py: code lines 0, comment lines 0, 0.0%, limit not enforced below 20 lines; doc_impact.py: 0 documents; number_guards.py PASS with local-ref-only fetch warning (checks.json). scratch.py close exited 0; stdout below, scratch-removed.txt and evidence/implementation-1/close.log.
- SKIPPED: Treat the generic design-surfaces seed shape check as an acceptance gate
  FO explicitly ruled it not applicable to this four-stage POC route; its raw missing-Surfaces/Visible-change exit 1 remains in design-surfaces.log, not reported as clean or repaired.
- SKIPPED: Product candidate changes, PR text/publication, roborev, live model replay, CI and CI cost measurement
  Approved read-only boundary: base=candidate c2f035b6612f5edb42220576b3414e993531ffd6 on spacedock-ensign/shared-assumption-replay-on-archived-tasks-poc; no product push/PR. Proposed checks were not executed; historical worker claims were not rerun; CI cost not measured.
- SKIPPED: Final state commit/sync, independent validation and copying the report beside the study
  FO owns these per the explicit mid-run direction; the worker runs no further state commit and does not claim delegated checks passed.

### Summary

The read-only replay records literal k=2/5 without activating the k<2 drop condition, but its permitted reports leak later work and do not establish independent predictive benefit. All final five hypotheses were frozen before dispatch 3 was opened; the contaminated UI row is excluded and replaced, the source/product boundaries are unchanged, and scratch is closed. FO commits the final report, validates it independently, and copies it beside the study.

Scratch-close stdout (exact):

```text
Scratch removed: /private/tmp/dev2/kc-claude-plugins-0a31751399576cc5/shared-assumption-replay-on-archived-tasks-poc/implementation-1 (236113 bytes)
Evidence: evidence/implementation-1/ (24 files, 74.2 KiB)
```
