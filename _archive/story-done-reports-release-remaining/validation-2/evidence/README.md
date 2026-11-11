# Independent validation, second dispatch

Verdict: PASSED for the current accepted checks at PR #839
`fd1caa475f85483cf5c4031a1e58656ff5d3eaff` and its stacked sibling PR #843
`01d23393ebe5bfd63d8bcafc01859c3b146021d2`. This supersedes validation-1 for
candidate identity and command coverage. AC-10 remains the explicitly permitted
future real-use check; this verdict is not merge, release, rollout or delivery acceptance.

All product checks used fresh `git archive` exports of #843 under
`/tmp/story-release-validation-2`, including a complete export for each Node
version. Mutation and pre-repair controls used separate temporary copies.
`exact-bytes.json`, `history-preservation.json` and `candidate-all-tracked-bytes.log`
bind the tested source to the dispatched commit and prove no tracked candidate
file changed. The producer subtree equals #839. PR bases are the immutable
`e8664a72b0f904e5dda3c391d52ab3abaca876b4` and #839 respectively, not a moving trunk.
`pr-839-final.json` and `pr-843-final.json` confirm both heads are still open and unchanged.

## Whole workflow commands and prior coverage

`workflow-results.md` lists every test/lint/install command, its direct exit,
runtime, output file and validation-1 coverage. `workflow-tests.json` contains
all 38 successful local check invocations: 28 dev2 Python commands, plus the
five journey commands on Node 22.13.0 and Node 24.18.0. The complete model suite
passes 276 tests on each Node; the laws suite passes 84 tests with one existing
conditional skip (`matrix-24-test_laws_check.log`). Runtime and setup substitutions
are explicit in `runtime.json` and `workflow-setup.json`.

These are macOS command executions. The Linux amd64 installer shell blocks were
not run on this host: native Spacedock 0.27.2 and the exact workflow source pin
`4d158a484ec73e184861067f8ed1e20087fdc26a` substitute for Linux setup. Actual hosted
results were read, not rerun by this worker: `hosted-dev2.json` is a successful
#843 run, and `hosted-journey.json` is the successful two-version #839 run.
No CI definition changed; cost per PR was not measured.

`validation-1-coverage.json` compares the original retained evidence itself.
Only five full dev2 commands were recorded there: skill lint, design surfaces,
release acceptance, dispatch records and watch. The other 23 commands have no
run record, including laws. Its 21 producer progress/schema tests were only a
subset of the full 276-test command; its npm install attempt was cancelled,
and doctor, typecheck and canvas-smoke have no retained execution record.

## Repair and Captain amendments

Captain amendment 2 is satisfied by both formal `Candidate:` lines and this
independent recheck of #843. `sibling-dispatch-check.json` uses the real delivery
parser and closes validation-1's F1 Needs decision finding: the sibling head is
now formally dispatched and pushed. No new Material, Deferred risk, Polish or
Needs decision finding is raised; existing limits remain below.

`repair.diff` contains only relocation of `workflow_extensions` into
`check_story_record`. The tests and their copied-script fixture are byte-identical.
`repair-red-green.json` reruns the same 13 ExitContractTest cases at the immediate
pre-repair merge and the new head: seven fail before with the missing import,
and all pass after. The full repaired laws suite also passes. Thus the retained
unchanged fixture detects reversal of this repair; the reported historical nine
whole-suite failures are not misrepresented as nine failures independently
reproduced by this narrower control. Seed and default Story checks still run.

Captain amendment 1 allows only adding the new member fields to the stored
sample. The unchanged whole-document consumer test passes all 122 tests at #843
(`matrix-12-test_release_acceptance.log`), and an extra unrecorded producer field
still fails that exact assertion (`amendment-1-mutant.log`). `exact-bytes.json`
proves the sample is only additive and the consumer test and contract registry
are unchanged. All original dev2 files other than the authorized import timing
are byte-identical to the original dev2 commit; merge parents remain intact.

## Every acceptance criterion and falsifier

`criteria.json` maps all 15 criteria to their half, primary output and independently
rerun counterexample. AC-10 is the only untested future criterion. The final
native progress driver and reverse driver both exit 0 in `final-native-results.json`.

- AC-1: `AC1-before.stdout` / `AC1-after.stdout` and the fresh acceptance log show
  the real Spacedock status operation changes inbox-home 0/1 to 1/1 and its release
  0/4 to 1/4, with spacedock-dev/subspace-relay#999. The before observation is the
  negative control; the invoked command instantiates the extension bullet verbatim.
- AC-2: both corpora's prior status/required/done/task-ID and release status/acceptance
  projections match field-for-field. Both `*-due-base.stdout` / `*-due-candidate.stdout`
  pairs are identical. `replay-falsifiers.json` independently shows a reverse
  mutation changing continuity-latest's acceptance.
- AC-3: `progress-replay-result.json` shows Relay 11 complete / 6 open / 167 empty,
  and agent-reviews-from-link 6 tasks / 5 done. The native reverse control counts
  only 3 declared members, and the changed-members mutation fails the test.
- AC-4: both complete model suites test all eight ref forms against ssh, https,
  ssh URL and absent origin. Dropping URL normalization fails `AC4-drop-url-rule.log`.
- AC-5: native QNow r12 has 4/8 release-only tasks and no story line. The separate
  temporary unknown-story task remains on its own line in `off-map-replay.log`;
  it is then removed. Dropping release-only output fails the reverse test.
- AC-6: `AC6-short.stdout` is 7 lines and 52 words. The populated 28-story fixture
  exercises both five-name limits and the three-ref limit; unbounded lists fail
  `AC6-unbounded-lists.log`.
- AC-7: the old CLI exits 2; removing Spacedock from PATH yields exactly one
  not-run line and exit 1 (`failure-signals.json`). Silently succeeding on a failed
  read fails `AC7-silent-failed-read.log`; the extension explicitly handles failure.
- AC-8: `schema.log` registers members at 1.1.0 with the old 1.0.0 hash retained.
  Removing the bump fails `AC8-remove-version-bump.log`.
- AC-9: only the approved seven producer and six dev2/ADR paths change, including
  the amended sample. Extension words move 612 to 713, under 726, and the joins
  line names five points. Workflow bytes remain unchanged; an actual throwaway
  workflow edit is rejected by the path check (`remaining-mutations.json`).
- AC-10: no released adopter archive message was produced. This remains the
  accepted future check after both releases reach Relay.
- AC-11: both Story forms, absence, fences, empty/none-without-reason and unlisted
  workflows are exercised. Both reverse rules fail their unchanged assertions.
- AC-12: `seed-replay.json` / `seed-replay.log` show 135/137 Relay, 163/163 QNow
  and 0/230 local refusals. The all-workflows mutation refuses all 230 local tasks.
- AC-13: the real watch subprocess names the missing Story record and stops
  naming it after the valid line; native readiness yields 31 Relay and 11 QNow
  names. Skipping Story enforcement fails `AC13-skip-story-rule.log`.
- AC-14: required ADR 0076 quotes the actual task ruling and names the protected
  check. `adr-lint.log` exits 0; removal is refused with exit 1.
- AC-15: both default-mode Story/field mismatches fail and unlisted workflows
  remain exempt; both archived Relay records agree. A presence-only comparison
  fails `AC15-compare-presence-only.log`.

## Setup corrections, limits and proof boundary

Replay pins: Relay code `0fce82296710d7bf3b89c2871adefd71db2e2957`, state
`77f5bb4e0e286467ec7078038e8bb9d680baddde`; QNow code
`ebc59cf96fdd5303e0dfccb1559d6048724e33ae`, state
`03838f912be5a74c972750128955524d03b5a6b6`; local state `10149f1c5`.
Sources were read-only local repositories from the earlier replay. Their commit
objects, not mutated source working files, supplied new exports and history.

The seed/idle replay used pinned state Git history. Progress uses the same
unchanged archived file bytes without state Git metadata; `progress-archive-setup.json`
records all-file hash equality and `replay-history-setup.json` the setup details.
An initial QNow whole-repo extraction rejected an unrelated absolute `st` symlink;
its exact pinned docs were exported instead, without following that link.
No task field, product assertion or reader deadline was relaxed.

Both base and candidate hit the unchanged 30-second deadline while other suites
were running. `initial-timeouts/`, `progress-replay-*.log` and the first
`acceptance.log` retain those failures. Base equality proves no regression only
for that failure; it did not establish acceptance. After the command matrix
finished, one final sequential progress run, native reverse run and fresh Bash
acceptance all passed without changing the reader, data or expectations. These
successful runs do not establish a performance guarantee under concurrent load;
the accepted not-run message remains the failure path.

`workflow-results.md` also retains the initial network interruption, occupied-port
preflight and incomplete Node 22 export failures, and the narrow setup corrections.
No other session's server, data, worktree, state file or configuration was changed.

`limit-judgments.json` judges every implementation limit: filed members are not
exhaustive scope; a bare PR number can name the wrong origin repository; a prose
step can be skipped; one workflow is read; Story form and field agreement do not
prove map membership; the existing deadline can fail under load; real-use AC-10,
release/rollout and costs remain unverified. No canvas redraw or map write is added.

Goal sufficiency is supported for the approved bounded route by the native archive
and seed/idle paths. Minimal necessity is supported by the reverse controls for
each added field, rule and bound, the whole-document consumer mutation, and the
required ADR; no retained product change lacks an accepted criterion or ruling.

## Stage guards and affected documents

`guard-results.json` records passing task/design/dispatch/role, ADR, number and
comment checks; `number-guards.log` follows a successful fresh fetch. The sole
added code comment is the required ADR pointer; ratios are 0.0% and 1.2%, under 5%.
`document-verdicts.json` checks every affected document: ADR 0041 and 0057 are
unaffected for stated reasons, ADR 0076 is updated; producer doc impact is empty.
The reserved-record command run from the export with read-only Git metadata and
a temporary index was:

    python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1/scripts/adr_lint.py docs/adr --since fd1caa475f85483cf5c4031a1e58656ff5d3eaff --require 0076

It exited 0. `acceptance.sh` includes the exact temporary-index setup.

## Minimal Captain acceptance

Run this unchanged six-step script in a fresh shell:

    bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/story-done-reports-release-remaining/validation-2/evidence/acceptance.sh

Each step names its command and expected observation. It declares the local commit
sources, installed Node/Python/Git/Spacedock prerequisites and npm network need;
it creates only temporary exports and replay state. The final run exited 0 in
70.341 seconds, with observed before/after reports and required ADR output in
`acceptance-final.log`; `final-native-results.json` records the direct exit.
The final committed script bytes equal the executed script bytes. It does not
replace the full command matrix, historical corpora, hosted runs, review, release,
rollout or AC-10. No product push, PR comment, review request, merge or release
was made; only this task's state report and evidence are committed and synced.
