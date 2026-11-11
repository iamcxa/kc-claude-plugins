# Stacked candidate preparation — message 4

Head: e079d0c555fde855527a82c7a497a4d07e6e4c04.
Parents: fa485f008562f00ebf91deed19e58ea52bb4b4dc (original dev2) and
fd1caa475f85483cf5c4031a1e58656ff5d3eaff (pushed producer, sibling PR #839).

The assigned dev2 worktree was clean before and after the authorized merge.
merged-head.json, no-manual-change-proof.json and the two equal binary diffs
prove both product halves retain their original bytes. No history was rewritten,
no product file was changed by hand, and no product push or PR creation occurred.

run-hosted-suites.py extracts all 28 Python command steps from the unchanged
.github/workflows/kc-dev-flow-2-tests.yml, runs them sequentially on the combined
head, captures each producer exit code directly, and checks the head/tree again.
The local run completed with exit 1: 27 commands passed, test_laws_check.py failed
9 of 84 tests (1 conditional skip). The unchanged consumer suite passed 122 tests,
and the three native Spacedock suites passed. This is local macOS arm64/Python
3.15 evidence, not a hosted Ubuntu CI run. The native CLI is Spacedock 0.27.2,
and its plugin root was checked out at the workflow's exact pinned commit
4d158a484ec73e184861067f8ed1e20087fdc26a. Runtime versions are in runtime.json.

## New finding requiring scope authorization

sandbox() in test_laws_check.py copies five scripts, including design_surfaces.py,
but not the newly imported workflow_extensions.py. Import then fails inside the
temporary package before the intended law-check exit contract can be exercised.
24-test_laws_check.log records all nine failures. laws-baseline-control.json
proves the same narrow test passes at the producer base and fails at the candidate.
probe-laws-dependency.py leaves product bytes and assertions unchanged: copying
only the existing helper into the temporary fixture turns that same case green.

findings.json and finding-boundary.json retain the open Needs decision finding.
proposed-fixture-fix.diff is a reviewable proposal only, never applied to product.
Message 4 forbids manual product changes, and the original design does not list
that test file. FO was asked for the bounded scope ruling while other suites ran.
No repair authority was inferred from the failure or the passing isolated probe.
The combined candidate is not ready to claim a green full workflow.

## Guards and handoff

ADR lint requiring 0076, number guards with the explicit stacked base, and comment
ratio all passed; comments are 1.2% against the 5% maximum. doc_impact lists ADR
0041 (unaffected: existing seed bounds), ADR 0057 (unaffected: amendment comparison)
and ADR 0076 (already updated by the retained dev2 commit).

The PR text names #839 as the producer sibling and its branch as the base, records
the new merge head and reports the current failing workflow. Product publication,
RoboRev, hosted CI and independent new-head validation remain FO-owned and unrun.
CI cost was not measured; workflow definitions did not change. AC-10 remains
future acceptance after release/rollout and a real adopter archive.
