# Round 5: repair the candidate's eager Story dependency

Candidate: 01d23393ebe5bfd63d8bcafc01859c3b146021d2, parent merge e079d0c555fde855527a82c7a497a4d07e6e4c04.
Stacked PR base: fd1caa475f85483cf5c4031a1e58656ff5d3eaff (#839). No product push or PR write occurred.
The Captain/FO's message 5 permits only the design_surfaces.py dependency repair. The candidate, not the laws test, was defective.

## Reproduction and regression boundary

laws-before-fix.log/exit run the unchanged ExitContractTest.test_check_exiting_1_with_no_stdout_exits_2 at the merge: exit 1 from a module-top workflow_extensions import. laws-after-fix.log/exit run the same test after moving that import into check_story_record: exit 0, preserving the expected exit 2 contract of its subprocess. red-green.json binds those results to the two heads.
The laws suite's fixed copied-script fixture is retained as the regression test: moving the import back to module top makes it fail. No assertion or fixture is changed. JourneyStoryTests (story-after-fix.log) exercise actual ds.check_task calls in seed and default modes, including scoped workflow admission and mismatched story refusal.

candidate-proof.json and verify-candidate.py bind the one-file repair and exact import relocation to the merged parent; authorized-repair.diff is the complete repair. Protected test, fixture, registry, workflow and reading-file hashes are unchanged from the merge. The producer subtree equals #839; every original dev2 file except design_surfaces.py remains byte-identical to fa485f008562f00ebf91deed19e58ea52bb4b4dc. The current stacked patch and original patch are both saved; they differ only by this authorized repair, so the former round's byte-identical-patch claim is superseded.

## Full local workflow replay

hosted-suites.json records the direct exit of every one of the 28 Python run steps extracted, in order, from .github/workflows/kc-dev-flow-2-tests.yml. Numbered logs retain output; hosted-suites-run.log has the final matrix result. All commands pass. Individual conditional skips remain in those logs and result messages; a passing command is not a claim that its skipped cases ran.
run-hosted-suites.py is the exact runner used. It asserts the candidate head before and after, the pinned Spacedock source SHA, the command count and a clean working tree. It invokes subprocesses without a pipeline and captures each producer's exit directly, with a 900-second per-command cap; no timeout occurred.
Prerequisites: the assigned dev2 worktree at the candidate SHA, Python, Node >=22.13, installed kc-journey-map npm dependencies (npm ci performed in round 4), Spacedock /Users/kent/.local/bin/spacedock 0.27.2, and the source checkout /tmp/opencode-story-done-round4/.sd-plugin-root at 4d158a484ec73e184861067f8ed1e20087fdc26a. Those are declared runner inputs, not committed product dependencies. A fresh machine must install/provide them and set the absolute WT/OUT/SD paths in the scratch runner.
runtime.json records the actual platform: macOS arm64 and Python 3.15. This is local execution of hosted commands, not an Ubuntu hosted CI run. The workflow file is unchanged; CI cost per PR was not measured.

## Guards and earlier validation coverage

guard-results.json records exact commands, working directory, logs and direct exits for ADR lint (--since the stacked base, --require 0076), fresh-ref number guards (--base the stacked base), comment ratio and document impact. All pass. document-verdicts.json records why ADR 0041/0057 remain unaffected and 0076 remains correct; no ADR change was needed for this import relocation.
validation-1 passed the combined tree without reporting this laws-suite failure. Its test-results.json and README list producer, design, idle-watch, dispatch and combined consumer suites plus the fresh-shell acceptance script and negative isolated-consumer run. validation-1-coverage.json records a bounded search of its retained evidence: no test_laws_check.py/laws_check.py/laws-suite run evidence is present. That record does not establish that the laws suite ran; it is not an earlier full-matrix pass, and its report was not rewritten.

## Retained scope and remaining work

The original implementation-1/evidence and independent validation-1/evidence retain native pinned replay, contract, mutation and short-report evidence. The repair reruns the affected import boundary, both Story modes and all 28 hosted command steps; it does not repeat those earlier historical mutations or native archive replays. AC-10 still requires the first real adopter archive after both releases and rollout. The map/canvas, declared status and release-acceptance behavior are unchanged by this repair.
The prepared second PR text is dev2-pr.md, also written at the dispatched /tmp path. FO still owns pushing this candidate, opening the second Draft PR on #839's branch, RoboRev, hosted CI and independent exact-head revalidation before any delivery ask. Local success grants no merge, release or rollout acceptance.
