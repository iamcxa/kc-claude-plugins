# Independent validation of story-done-reports-release-remaining

Verdict: PASSED for the combined product behavior at producer
fd1caa475f85483cf5c4031a1e58656ff5d3eaff and dev2
fa485f008562f00ebf91deed19e58ea52bb4b4dc, both against
e8664a72b0f904e5dda3c391d52ab3abaca876b4. This is not a merge, publication,
rollout or real-use verdict. The second head alone has one expected consumer
failure. F1 below is an FO-owned dispatch-record handback before delivery.

Product code was exported with git archive under
/tmp/validation-story-progress-20261111/{producer,dev2,base}; the integrated tree
overlays only dev2's six changed paths onto the producer export. exact-bytes.json
binds each changed file to its original commit bytes. No product bytes or branches
were changed. The existing candidate's node_modules were reused explicitly;
environment.json records the dependency path, lockfile digest and tool versions.

## Criteria, halves, observations and falsifiers

All filenames below are relative to this evidence directory. Tests were actually
rerun; implementation logs were not treated as independent validation.

| Criterion | Half | Observation | Independently rerun falsifier |
| --- | --- | --- | --- |
| AC-1 | producer; dev2 invocation | AC1-before.stdout vs AC1-after.stdout: inbox-home 0/1 to 1/1, owner-account 0/4 to 1/4 and spacedock-dev/subspace-relay#999 | Before native status --set, report says 0/1 and 0/4; acceptance-final.log repeats the exact extension command with concrete paths |
| AC-2 | producer + combined consumer | Both relay/qnow old-field projections match base; due output files are identical; consumer-combined.log has 122 tests OK | AC2-live-members-as-declared.stdout changes continuity-latest acceptance; replay-falsifiers.json; AC2-members-as-declared.log rejects the reverse mutation |
| AC-3 | producer | progress-replay-result.json: 11 complete, 6 open, 167 empty; agent-reviews-from-link 6 tasks/5 done | AC3-live-declared-list-only.stdout gives 3 tasks; AC3-declared-members-only.log fails |
| AC-4 | producer | journey-tests.log exact refs for all eight forms with ssh, https, ssh URL and absent origin | AC4-drop-url-rule.log rejects raw URL output |
| AC-5 | producer | AC5-release-only.stdout and qnow-listing.stdout: r12 4/8 release-only tasks; off-map-replay.log adds one real scratch task and keeps it on a separate line | AC5-drop-release-only.log fails; native off-map control preserves both separate lines |
| AC-6 | producer | AC6-short.stdout: real 28-story release report has 7 lines/52 words; native fixture also exercises 28 populated stories, five-name lists and three refs | AC6-unbounded-lists.log rejects unbounded lists |
| AC-7 | producer + dev2 instructions | Old CLI exits 2; missing Spacedock exits 1 with one not-run line; both handling cases are in EXTENSION.md | AC7-silent-failed-read.log rejects exit-zero unavailable output |
| AC-8 | producer | schema.log prints members and 1.1.0; 1.0.0 digest retained; schemas tests pass | AC8-remove-version-bump.log rejects version removal |
| AC-9 | dev2, with amendment 1 | dev2.diff has only approved paths plus the allowed sample and ADR; words.json 612 to 713; workflow, consumer test and consumer registry bytes equal base | remaining-mutations.json: actual throwaway workflow edit is outside allowed paths; unchanged sample assertion rejects unrecorded field |
| AC-10 | future real adopter + FO | Not run; accepted criterion explicitly permits an unverified future check | No real archive/rollout evidence or real-use falsifier exists at this stage; scratch evidence does not substitute |
| AC-11 | dev2 | design-tests.log: both forms accepted; absent/fenced/empty/none-without-reason refused; unlisted workflows unaffected | AC11-unlisted-workflows.log and AC11-none-without-reason.log fail |
| AC-12 | dev2 | seed-replay.json and seed-replay-restored.log: relay 135/137, qnow 163/163, local 0/230; every changed verdict is only the intended Story refusal | AC12-force-all-workflows.json: mutant refuses all 230 local tasks |
| AC-13 | dev2 | Native task readiness and candidate checker give 31 relay/11 qnow names; watch-tests.log exercises the actual pr_watch subprocess before/after Story: none: test | AC13-skip-story-rule.log fails |
| AC-14 | dev2 ADR | adr-lint.log and acceptance-final.log: required 0076 present and lint exit 0; Captain words and Protects read against task records | AC14-missing-adr.log exits 1 when the ADR is absent |
| AC-15 | dev2 | design-tests.log compares recorded story with empty/different fields and none with a story; seed-replay.json confirms the two existing relay records | AC15-compare-presence-only.log fails |

## Replays and rerun corrections

The relay code/state pins are 0fce82296710d7bf3b89c2871adefd71db2e2957 /
77f5bb4e0e286467ec7078038e8bb9d680baddde; qnow code/state are
ebc59cf96fdd5303e0dfccb1559d6048724e33ae /
03838f912be5a74c972750128955524d03b5a6b6; local state is 10149f1c5.
Fresh code copies and pinned state archives were made from the implementation's
local scratch repositories, not its modified working files. Source commits were
read-only. Only scratch inbox-home and the temporary off-map control changed.

For idle readiness, body archives alone are insufficient: without state Git
history, Spacedock omitted needs-preparation rows. Restoring pinned state history
restored those rows. Running after the inbox-home done control gives 30 rather
than 31; the final unmodified pin gives 31. A temporary off-map task also changed
the qnow corpus to 164 during one attempted count; after removing that probe, the
final replay is exactly 137/163/230 tasks. Failed attempts are retained in the
other seed logs; seed-replay-restored.log and seed-replay.json are the final run.

The supplied replay/mutation drivers were inspected and rerun from fresh
exports. The scripts/ copies only parameterize paths and replace git lookups in
exports with read-only lookups at the pinned repository. Python uses -B; mutant
copies omit caches. The implementation's assembled verify.sh was not run because
it requires product worktrees rather than the dispatch-required exports; its
component commands were rerun and the replacement acceptance.sh was run in full.

## Suites and guards

test-results.json records the 21 producer checks (20 initially passed; the one
canvas test passed separately with permitted loopback), 222 design tests (four
existing conditional skips), 136 watch tests, 125 dispatch tests (one existing
conditional skip), and 122 integrated consumer tests. The expected failure in
consumer-dev2-alone.log is the unchanged whole-document assertion in
DueTests.test_live_producer_keeps_done_but_live_release_and_agrees_on_unbuilt.
Thus merging/rebasing the producer first is a real dependency, not just scheduling.
Any rebased dev2 head needs validation at that new head.

guard-results.json records actual commands and exit codes for skill lint,
design check, dispatch records, ADR lint, document impact, number guards and
comment ratio. The added comment is an ADR pointer, not narrative. Comment ratios
are 0.0%/1.2%, both below 5%. Initial number-guard runs could not fetch state refs;
number-guards-fresh.log is the successful fresh-ref rerun for the only ADR-adding
head. Producer adds no ADR. ADR 0041 and 0057 remain applicable and unaffected;
0076 is updated. Producer doc impact is empty. CI definitions are unchanged and
cost per PR was not measured. pr-839.json is the remote read; the second PR is
not published. RoboRev, approval, release and rollout were not performed here.

## Minimal Captain acceptance

Run the committed acceptance.sh in a fresh Bash shell:

    bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/story-done-reports-release-remaining/validation-1/evidence/acceptance.sh

It has six commented steps with expected observations. Prerequisites are named
in the script: both local commit objects, the specified Relay source clone with
its pinned objects, the dispatched package, Python, Node >=22.13, Spacedock 0.27.2,
and the existing candidate's installed npm dependencies. It exports new files
under /tmp and changes only scratch state. acceptance-final.log is the actual
successful full run, exit 0; acceptance-result.json records its scope and limits.
The script file was executed exactly as supplied, using its /tmp location before
copying these same bytes into the task folder.

It does not test a clean dependency installation, every historical replay,
hosted CI for the second PR, review, publication, release, rollout or AC-10.
An earlier npm-ci attempt failed on this host and was cancelled; package/lock
bytes are identical to base, so that attempt is not attributed to this change.
The successful script makes the preinstalled dependency prerequisite explicit.

## Findings and retained limits

- F1 Needs decision: FO owns the formal sibling candidate record. The newest
  dispatch's header lists only fd1caa475f85483cf5c4031a1e58656ff5d3eaff;
  sibling-dispatch-check.json uses the real delivery-gate Candidate parser and
  does not recognize fa485f008562f00ebf91deed19e58ea52bb4b4dc. The checklist
  authorizes this validation, but contract[docs/adr/0036-a-reserved-adr-may-land-on-a-named-sibling-pr-of-the-same-task.md#decision]
  requires the formal line for a sibling to supply ADR 0076. Before a delivery
  ask, FO must arrange the latest dispatch record and any rebase validation;
  the validator did not rewrite FO's dispatch. No material product defect was
  demonstrated in the accepted current criteria.

The implementation's stated limits stand: filed tasks cannot prove exhaustive
scope or delivery acceptance; bare PR numbers may resolve to the wrong origin
repository; an FO prose step can be skipped; only one workflow is observed; story
line form/field agreement does not prove map membership. The original 30-second
reader limit remains; these successful reads do not prove it cannot time out
under load. No canvas redraw or map write is added. The true adopter archive
message, release rollout and any ongoing support obligation remain outside this
validation. Goal sufficiency for the current bounded route is supported by the
native archive control and seed/idle path; each retained field/check/doc maps to
a criterion, mutation or the approved ADR, without extending scope.
