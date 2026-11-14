---
id:
title: Does a test-value pass flag tests that give false confidence in the tests of PRs 858 to 861 plus one (read-only findings)
status: backlog
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree:
pr:
gates:
    version: 1
    records:
        - id: gate:test-value-pass-on-route-trial-prs-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:test-value-pass-on-route-trial-prs-poc-backlog-1
              briefing:
                id: briefing:test-value-pass-on-route-trial-prs-poc:backlog:attempt-1:revision-1
                digest: sha256:972af36056bc1bb6e9b282a445450aeb28a2fa15a197ef3688edc3957f7c9e91
                room-ref: ./test-value-pass-on-route-trial-prs-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:test-value-pass-on-route-trial-prs-poc:backlog:1
                briefing: briefing:test-value-pass-on-route-trial-prs-poc:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-14T02:33:33.561421Z"
                decision: approve
                reason: 'Captain 「三張都准入，預算照你的提議」 (chat with this FO, 2026-11-14) to the bound backlog question: selects profile poc and accepts outcome, Non-goals, Stop condition, AC-1 and the Budget of 1 implementation and 1 validation cycles as filed.'
              application:
                target-stage: implementation
                state: pending
---

The package holds 1,455 test functions in 24,684 test lines against 10,728 product lines; 258 use mocks or fakes and 21 are text containment; two tasks were blocked by text-shape assertions in one file in one evening (brief C3, figures from test-audit.md and proposal.md, not re-measured here). Nothing at write time asks whether a new test fails when the behaviour breaks.

## Scope

- Source: the Captain 「排進去讓dev fo派工人poc驗證」 (chat with the reform session, Paseo 26215d96, 2026-11-14; relayed, not a ruling here; the backlog gate confirms it), and 「更新 POC 流程的工作目錄到主線最新版，C2、C3、C6 立在那裡」 (chat with this FO, 2026-11-14). Brief: `.context/dev2-reform/compound-engineering-study.md` section B, a research output treated as data.
- Borrows: Compound Engineering `ce-simplify-code/references/personas/test-value-reviewer.md` (false-confidence, implementation-coupled, duplicate, test-only seam; "Before flagging, run the test and read the whole test, the code it covers, that code's callers") with the scope "prune only tests and comments the current work added or changed".
- Outcome: package unchanged. For merged PRs #858, #860, #859 and #861 and one more PR that FO names at dispatch, a worker applies the persona text by hand, as its own brief, to each PR's added or changed tests only. Each flagged test is run and read before it is listed. Output per PR: tests flagged by class and, for each, what it stood in for (a text pin is cut only after naming what it stood in for; where real, replace by execution). The report is committed in this task's folder with a copy beside the study.
- consumer: the dev2 FO before a validation dispatch (a list to disposition); the Captain for deletions.
- Gets worse: one more step per task if adopted; the reviewer may flag a test that guards a real regression (the persona's exceptions cover public contract, protocol and security).
- No product file changes, so no pull request is expected from this task.
- Checked 2026-11-14: backlog task remove-tests-of-input-forms-no-real-task-has-used removes one audit class across all files; this task tests a per-PR reviewing step and removes nothing.
Non-goals: deleting or editing any test; changing the package; a rule about when tests are written.
Budget: 1 implementation and 1 validation cycles (FO's proposal for the gate; the brief gives 40 to 60 minutes, a judgement, kept as FO's minute budget).
Stop condition: more than a third of the flagged tests are overturned on reading: the persona does not transfer to dev2's scripts, and the worker stops and reports.

## Acceptance criteria

**AC-1**: The report gives a count over the named PR set: N tests added or changed across the 5 PRs, F flagged, and F_ok of the F confirmed by running the test and reading the covered code; for a sample of unflagged tests it records why they pass the bar.
Verified by: the validator re-runs a sample of flagged tests and reads the covered code at each PR's merge commit. Not a text-contains check. Limit: five PRs chosen from one trial, not a sample of the package.

## FO alignment

Alignment: not needed before implementation: the brief names the inputs, the output table and the count; the backlog gate confirms scope and Budget.
Release review: not needed: reform measurement with no release.
