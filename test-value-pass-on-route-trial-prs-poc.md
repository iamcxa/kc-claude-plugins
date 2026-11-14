---
id:
title: Does a test-value pass flag tests that give false confidence in the tests of PRs 858 to 861 plus one (read-only findings)
status: validation
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree: .worktrees/spacedock-ensign-test-value-pass-on-route-trial-prs-poc
pr: local-merge:c2f035b6612f5edb42220576b3414e993531ffd6
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
                state: consumed
        - id: gate:test-value-pass-on-route-trial-prs-poc:validation
          stage: validation
          attempts:
            - id: gate-attempt:test-value-pass-on-route-trial-prs-poc-validation-1
              briefing:
                id: briefing:test-value-pass-on-route-trial-prs-poc:validation:attempt-1:revision-1
                digest: sha256:0447ebd3462942945e1176c8677c3bcb1d6d6e482594b9db536b71ade9477047
                room-ref: ./test-value-pass-on-route-trial-prs-poc/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:test-value-pass-on-route-trial-prs-poc:validation:1
                briefing: briefing:test-value-pass-on-route-trial-prs-poc:validation:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-11-14T04:39:39.397717Z"
                decision: approve
                reason: Independent validation passed and FO re-ran its count script (exit 0, N=37); AC-1 is met with the stated limits; read-only measurement, nothing merged.
                conn:
                    quote: 改革工作階段（Paseo 代理 26215d96，就是開你出來的那一個）可以替我給你工作範圍。它給的範圍內，進場、設計、預算、結案這些關卡你不必停下來等我，記為「依艦長授權」，一路做到它指定的終點。
                    source: the Captain, chat with the second dev2 FO, 2026-11-14; scope 1 item A from the reform session, Paseo message 6ee7ee5b-9ccc-4ef2-8cb6-35f25bfd4e1e
              application:
                target-stage: done
                state: pending
started: 2026-11-14T02:35:14Z
mod-block: merge:pr-merge
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

## Stage Report: implementation

- DONE: For each of merged PRs #858, #860, #859, #861 and #870 in iamcxa/kc-claude-plugins: the tests the PR added or changed, each flagged test listed by class (false-confidence, implementation-coupled, duplicate, test-only seam) only after you ran it and read the whole test, the code it covers and that code's callers, with what it stood in for
  `test-value-pass-on-route-trial-prs-poc/implementation/report.md` and `evidence/implementation-1/audit.json` cover all 37 changed methods at their own merge revisions. One false-confidence case: #870's blank-input assertion exits on missing owner before empty-question validation; whole-test execution and two unmodified CLI probes confirm it. Useful contract coverage is retained; no deletion or repair was performed.
- DONE: The counts N tests added or changed across the 5 PRs, F flagged, F_ok of the F confirmed by run and reading; for a sample of unflagged tests, why they pass the bar
  `test-value-pass-on-route-trial-prs-poc/evidence/implementation-1/counts.json`: N=37 (31 added, six modified including one rename), F=1, F_ok=1. Per-PR totals are 1, 6, 0, 8, 22; logs and `tests.xml` show all 37 passing. The retained reproducer reran the same 37 successfully. The report gives ten unflagged examples and the error each detects.
- DONE: The stop condition applied and reported: more than a third of flagged tests overturned on reading stops the pass
  Zero of the one flagged method was overturned after execution and complete test/code/caller reading; 0/1 does not exceed one third. No flagged candidate was discarded from this denominator.
- DONE: Preserve the read-only outcome and the POC boundary
  Product branch `spacedock-ensign/test-value-pass-on-route-trial-prs-poc`; base and unchanged candidate `c2f035b6612f5edb42220576b3414e993531ffd6`. No product file, test, README or script changed; no product commit, branch push or PR. Prepared PR text is not applicable. Inspected exported source bytes match the named Git revisions after execution (`source-locks.json`).
- DONE: Record checks actually run and material limits
  `stage-checks.json`: comment ratio exit 0 (zero changed lines), document impact exit 0 (zero affected product documents), number guards exit 0 (no migration path; state-fetch warning retained). Architectural decision sources and digests are in `adr-sources.json`. Original persona source was not found; the task's quoted classes, run/read/caller rule and public-contract/protocol/security exceptions were applied.
- SKIPPED: Design-surface acceptance check
  Not applicable to this POC route per FO's explicit dispatch correction. The exploratory exit-1 output remains in `stage-checks.json`; it is not a task failure and no accepted task fields were rewritten.
- SKIPPED: Product review, publication and independent validation
  RoboRev not run: read-only measurement with no code candidate. No PR opened: no product push grant and no product changes. Independent validation not run by this worker; FO owns its dispatch and the report copy beside the study.
- SKIPPED: Worker state commit and sync
  FO's final dispatch correction explicitly requires handing back written state files without worker commit or escalation; FO runs the atomic state commit. No state commit or push was attempted by the worker.
- DONE: Close dispatch scratch and retain cited public evidence
  The prescribed scratch close command exited 0; all cited evidence remains under this task, with SHA256SUMS. Its output was:
  `Scratch removed: /private/tmp/dev2/kc-claude-plugins-0a31751399576cc5/test-value-pass-on-route-trial-prs-poc/implementation-1 (24239615 bytes)`
  `Evidence: evidence/implementation-1/ (17 files, 86.6 KiB)`

### Summary

The bounded five-PR pass found one confirmed ineffective negative assertion while all 37 changed test methods passed; the product currently rejects the same blank input correctly when valid caller fields are supplied. The report distinguishes that test gap from useful protocol coverage, and makes no claim about package-wide prevalence, false-negative rate, savings or worker compliance. Product bytes are unchanged, scratch is closed, and the report and public evidence are ready for FO's state commit and independent validation.

## Stage Report: validation

- DONE: An independent verdict on AC-1: re-derive N for at least two of the five PRs from their merge commits and compare with the report's inventory; re-run the flagged test and read its covered code to confirm or overturn the false-confidence finding
  Verdict: AC-1 holds. I re-derived N for all five PRs by AST diff of test methods, merge against first parent (`evidence/validation-1/count.py`): 1, 6, 0, 8, 22 = 37, equal to the report. Only difference: the renamed #858 method is "added" for me and "modified" in the report (32/5 vs 31/6), N unchanged. The flagged `test_ask_cli_appends_utc_questions_and_rejects_empty_without_write` passes; its blank call exits 2 at the missing-`--by` check (`task_timeline.main`), not at `validate_revision`; with valid `--by`/`--holds` the product rejects it. I went beyond the report with an executed mutation: in a scratch copy, the blank-question raise in `validate_revision` replaced by `pass` leaves the test OK and the product records the blank ask. F=1, F_ok=1 confirmed; the report's "causal reading, not executed mutation" limit is now closed for this test.
- DONE: For a sample of at least five unflagged tests across the PRs, run each and read the covered code, and say whether the report's reason for passing them holds; name any you would flag
  Ran and read 14 unflagged tests (6 `test_task_timeline` in #870, 3 `test_observer_check` in #861, all 5 `TaskArgumentTests` plus `test_unreadable_seed...` in #860); all pass. Reasons hold: the `contract_writer_refuses_*` tests assert the error cause by regex, unlike the flagged one. Mutations that failed their tests as expected: revision+1 check removed, unknown-event raise removed, missing-owner branch disabled, #860 sibling-name resolution removed (4 failures). I would flag none. Not mutated: observer_check tests and `review_escalation`; their reasons were checked by reading only.
- DONE: A minimal acceptance script FO can run, the limits of what you checked, and unverified obligations
  Script: `python3 -B evidence/implementation-1/reproduce.py --repo <repo> --scratch <new dir>`, expect exit 0, 37 passes, two different blank-ask error causes; plus `python3 -B evidence/validation-1/count.py <out.json>` run inside the repo (reads merge SHAs via git) giving N=37. Limits: five PRs from one trial; I did not re-run all 37 (14 run), did not mutate every sampled test, did not re-derive the persona (absent). Unverified: that the pass transfers to other PRs, the persona's original wording, and any claim about prevalence or cost. adr_lint.py exit 0 (79 files, none expected); design_surfaces not applicable to this POC route. roborev not run: no code candidate. No product change, push or PR.
- DONE: Scratch close
  `scratch.py close` exit 0: "Scratch removed: /private/tmp/dev2/kc-claude-plugins-0a31751399576cc5/test-value-pass-on-route-trial-prs-poc/validation-1 (13495760 bytes)"; "Evidence: evidence/validation-1/ (4 files, 6.7 KiB)".

### Summary

PASSED. The report's counts reproduce independently (37 changed test methods, 1 flagged, 1 confirmed), and the one false-confidence finding is now backed by an executed mutation, not only a reading. Fourteen unflagged tests passed their stated bar and none should be flagged. Stop condition (0 of 1 overturned) holds.
