# Independent validation: PR 849

Verdict: **PASSED for the dispatched candidate validation**, exact head `78905b08d6f38817ccdda5d2e91be478fd75dfc7`, base `44f11855264bde64da284ffa9c1fef70e8ac38dd`. AC-5's full merge-result suite remains a named FO pre-merge obligation, not evidence this worker produced and not merge approval. The GitHub snapshot in `pr.json` is Draft/open at that head. Product bytes were not edited; the changed-file export hashes match the commit (`bytes-and-tools.json`).

## Accepted decisions

The actual ideation gate record approves all three parts of its bound question: native current-stage reading with unreadable-stage refusal, D1's narrowed stop-condition reading (remove only the Worth error and preserve 0.38.1 output), and D2's third-file observer change. These are accepted scope, not new permission questions. ADR 0077 already restricts answers to ideation and exempts old records; ADR 0017 and ADR 0041 support judging historical requirements at event time. No new decision record is needed.

## Acceptance evidence and falsifiers

- **AC-1 PASS.** `replay.json` contains original stdout, stderr and exit for all three Bite tasks against 0.38.1: 1/0/0 and byte-equal outputs. The remaining `adr-required-statement` Supersedes error exists on 0.38.1 and is outside this repair. The baseline stage rule restores Worth on all three.
- **AC-2 PASS.** Existing new tests use the actual Spacedock binary, with ideation (with/without Design), backlog, empty/absent stage, implementation, validation including quoted/commented YAML, and done. `candidate-tests.log` and `acceptance.log` show the native cases ran. Reverse-stage and never-require mutations fail the later/earlier cases respectively (`mutations.json`); all four and five subcases fail as expected.
- **AC-3 PASS.** The existing failing-reader executable exits 23, producing exactly one reader error and no Worth line. Deleting error recording causes its test to fail (`mutations.json`). The no-README actual-task check also shows reading does not require a surrounding adopted README (`additional-evidence.json`).
- **AC-4 PASS.** `replay.json` covers exactly the 75 plugin plus 98 qnow top-level tasks at the two declared commits, with per-file hashes, raw outputs and native stage reads for affected tasks. Exactly the ten named later-stage tasks lose Worth, seventeen ideation tasks retain it, and there are no other output differences or gained errors. Both unrelated-output injection and a later-stage row retaining Worth are rejected. Sources were only read; their status before and after the replay agrees.
- **AC-5 PARTIAL / FO remainder.** Commit diff and live captured PR metadata show only the three approved files, a `fix(kc-dev-flow-2):` title, and no version/CI changes. Extra-path and non-fix-title controls are rejected in `acceptance.log`. This worker ran the complete affected design-surface suite at candidate and baseline. The full kc-dev-flow-2 suite on the actual merge result, with the real reader, is explicitly assigned to FO before the merge ask and has not been independently observed here.
- **AC-6 PASS within its named replay.** `observer-review.md` independently applies the candidate historical design-check paragraph to the bound second briefing at `d57ed9b75ba5`. The task hash matches its artifact; the event-time README independently resolves to `04809c3c6146c9f4a8f2f0b916fe84c94bfaa1a3`. Baseline and candidate CLI still emit Worth at ideation. Candidate instruction yields current-schema incompatibility, while reverting to the seed-only sentence yields violation. This is the accepted one-paragraph replay, not a complete Observer lifecycle run.

## Test-count discrepancy

`baseline-tests.log`: 226 discovered, four existing optional history cases skipped, **222 passed**. `candidate-tests.log`: 229 discovered, the same four skipped, **225 passed**. `test-inventory.json` compares parsed Python function bodies without line-location attributes: no removal, rename or change to any existing test; exactly three methods were added. The 226-versus-225 comparison mixed discovered and passed counts. No negative case was lost.

## Other required checks

`checks.json` retains exact commands, cwd, stdout, stderr and exit. Repository skill lint, ADR lint (`--since` base plus `--require 77`), number guards, comment ratio, affected-document listing, dispatch-record validation and task check all exit 0. ADR lint checks 70 records. Comments add 0 lines among 38 code lines (0.0%, maximum 5%). Workflow text remains unchanged at 6008/6008 words. The installed-package task check and role-trigger check separately exit 0 (`installed-task-check.json`, `role-triggers.json`). The role report shows one implementation and one validation cycle, within budget.

The document list is unchanged from implementation. Independently read dispositions: ADR 0041 unaffected because seed admission bounds do not change; ADR 0057 unaffected because amendment word comparison does not change; ADR 0076 unaffected because story checks do not change; ADR 0077 unaffected because its existing ideation-only answers and old-record exemption match this repair. The observer sentence is updated. `additional-evidence.json` verifies the reported reading deltas and six added observer words.

## Finding disposition

- **F1 Deferred risk — CI omits the two native-reader tests when no Spacedock is present.** Released user/workflow: a maintainer running the normal GitHub test job; the design test command is before Spacedock installation in the unchanged workflow. Observable harm: no broken behavior at this head was observed; future stage regressions could escape those two checks. Affected promise: `value-ac[AC-2]` keeps both earlier-stage refusal and later-stage release, and `value-ac[AC-5]` requires FO's real-reader merge-result run. Trigger evidence: `no-cli.log` executes seven tests with exactly two skips; `candidate-tests.log` and fresh `acceptance.log` execute both locally. Becomes Material if a supported faulty stage path is demonstrated or delivery proceeds without the required native-reader run. No CI repair is authorized by this three-file scope.

No Material, Polish or Needs decision finding is added. D1 and D2 are settled by the Captain's recorded approval.

## Limits assessed

- The four historical suite skips predate this change; all 226 old bodies remain identical. The task-specific 173-task corpus and the explicit historical briefing were separately exercised. No unrelated amendment-history corpus is claimed green.
- Number guards warns that state fetch failed; local reservations may be stale. The exact candidate adds no ADR, migration or reservation, so this warning does not invalidate its no-number-change result. Remote reservation freshness remains unproved.
- The manual Observer paragraph replay is sufficient for AC-6's named case and no broader agent behavior. No real post-release archived adopter is claimed.
- Product push/Draft creation have already happened according to `pr.json`. RoboRev is only reported in that PR body as FO-owned; this validator did not rerun it. Hosted CI, merge-result full suite, merge, release, and adopter rollout are not claimed by this report.
- CI cost was not measured; no CI configuration or triggers changed.
- All persistent proof is in this validation folder. The first mutation attempt had an export-layout error and is retained in `mutations-attempt-1.log`; it was not counted as a killed mutant. The corrected layout and the fresh-shell script both ran the intended assertion failures. No product change was made to obtain those results.

## Goal and necessity

The native CLI fulfills the limited-use compatibility outcome without weakening ideation/backlog or unreadable-stage refusal. Reverting the stage change restores the observed ten-task blockage; removing each new test target loses an exercised stage/error counterexample; reverting the observer sentence restores the named historical false violation. Each retained change maps to the accepted goal and has a demonstrated without-it consequence. The scoped validation passes, with FO's delivery obligations still outstanding.

