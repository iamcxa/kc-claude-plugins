
## Stage Report: implementation

- DONE: Repair the candidate in kc-dev-flow-2/scripts/design_surfaces.py by loading workflow_extensions only inside the check that uses it.
  Candidate 01d23393ebe5bfd63d8bcafc01859c3b146021d2 on spacedock-ensign/story-done-reports-release-remaining-dev2 has parent e079d0c555fde855527a82c7a497a4d07e6e4c04; implementation-1-round5/evidence/candidate-proof.json and authorized-repair.diff prove the sole change is moving the import into check_story_record.
- DONE: Keep a test that fails if the import moves back to module top; do not change the test or its fixture.
  The unchanged laws copied-script fixture is the regression: laws-before-fix.log exits 1 with ModuleNotFoundError, laws-after-fix.log exits 0 for the same ExitContractTest case; red-green.json binds both heads. Restoring the eager import reproduces the failure before the expected subprocess exit 2.
- DONE: Preserve the Story rule wherever seed and default checks run.
  story-after-fix.log runs both JourneyStoryTests; full design suite passes 222 tests (4 existing conditional skips). Removing the Story check or its workflow scope would fail missing-record/mismatched-field or unlisted-workflow controls.
- DONE: Re-run all 28 hosted workflow commands on the new head and report them.
  hosted-suites.json and numbered logs record all 28 direct exits as 0, including 84 laws tests (1 existing conditional skip), 122 unchanged consumer tests and the three native Spacedock command suites; runtime.json pins CLI 0.27.2 and source 4d158a484ec73e184861067f8ed1e20087fdc26a. This is local macOS/Python 3.15 execution, not hosted CI.
- DONE: Say validation-1 passed the combined tree without this suite failing being reported, and what its record shows about whether that suite was run.
  validation-1-coverage.json: its test-results.json/README list producer, design, watch, dispatch, combined consumer and the fresh-shell script, but retained evidence contains no laws-suite run record. It does not establish that laws ran; the earlier validation report is unchanged and is not a full-matrix pass.
- DONE: Preserve the merge history and compare the stacked dev2/docs/adr diff with the original dev2 patch.
  Stacked base fd1caa475f85483cf5c4031a1e58656ff5d3eaff (#839); merge parents remain fa485f008562f00ebf91deed19e58ea52bb4b4dc and fd1caa475f85483cf5c4031a1e58656ff5d3eaff. dev2-original.diff/dev2-stacked.diff differ only by the authorized import relocation; every other original dev2/ADR file and the producer subtree are byte-identical.
- DONE: Retain the approved two-PR design, additive progress contract, archive report and Story admission behavior within the named files plus Captain amendment 1's sample.
  candidate-proof.json preserves all seven producer files, the other five dev2/ADR files, unchanged consumer assertion/registry, reading file and workflow. The 122-test whole-document consumer suite passes; no map/canvas write or version bump is added.
- DONE: Retain the pinned replay and runnable falsifier evidence for AC-1 through AC-9 and AC-11 through AC-15.
  implementation-1/evidence and validation-1/evidence retain native counts, short-report, ref/contract and mutation controls; candidate-proof.json bounds this repair to import timing, and seed/default plus the full command matrix are rerun here. Prior historical replay/mutation results are not represented as new-head executions.
- DONE: Recheck ADR 0076, reserved numbers, comment ratio and affected documents against the stacked PR base.
  guard-results.json records all exits 0: ADR lint --since fd1caa475 --require 0076; fresh-ref number guards --base fd1caa475; comment ratio 1.2%, max 5%; repository skill lint is matrix step 1. document-verdicts.json retains ADR 0041/0057 unaffected and 0076 correct, quoting the unchanged Captain ruling.
- DONE: Update /tmp/impl-story-done-reports-release-remaining-dev2-pr.md with the new head, stack, sibling and checks.
  dev2-pr.md is the durable copy; the scoped Conventional Commit title is retained and #839's branch is the proposed base. It describes the candidate dependency repair without changing tests or their fixtures.
- DONE: Append a complete superseding implementation stage report and commit/sync the scoped state evidence.
  This report and implementation-1-round5/evidence contain the actual commands, direct exits, byte proofs and remaining limits; state commit is path-scoped and synchronized separately from the unpushed product branch.
- SKIPPED: Repeat the earlier native historical replays and all prior mutations on the new head.
  This narrowly authorized repair rechecks the failing import surface, both Story modes and all 28 workflow commands; earlier scoped evidence remains retained rather than silently promoted to new-head evidence.
- SKIPPED: AC-10: the next real adopter archive after both releases and rollout.
  This remains the explicit future check; a local replay or green test matrix is not that real archive message.
- SKIPPED: Product push, second Draft PR creation, RoboRev, hosted CI, independent new-head validation, review, ready, merge, release and rollout.
  FO owns these actions; no PR opened: no push grant. Local tests of RoboRev wiring do not constitute a RoboRev review. CI cost per PR was not measured; CI definitions are unchanged.

### Summary

This supersedes the earlier implementation reports for the active candidate and publication preparation: 01d23393ebe5bfd63d8bcafc01859c3b146021d2 corrects the candidate's eager dependency on top of the preserved merge, with tests and fixtures unchanged. All 28 local hosted-workflow command steps pass on that exact head; validation-1's retained record does not establish a laws-suite run. The second product branch remains unpushed, and FO-owned publication, independent revalidation and real-use acceptance remain open.
