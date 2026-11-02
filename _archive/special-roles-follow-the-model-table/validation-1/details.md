# Independent validation of PR #764

Verdict: **PASSED for this task's pre-merge validation scope**, at `562b1a87198d97bb2ae1d87b72884e390b20e146`, against stacked base `c129cb215c2630d08853eeffae0fd5a2ee7e40c6` (PR #763). No new Material, Deferred risk, Polish, or Needs decision finding. This is not a clean integrated-delivery verdict: the previously recorded default-roster discrepancy remains owned by PR #765, and AC-10's seed retirement is due after merge.

The assigned branch stayed at the candidate, with no product edits, commits, pushes, PR comments, review requests, or readiness changes. Checks ran from the detached throwaway checkout `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-special-roles-follow-the-model-table/.validation-562b1a87`; it is removed at handback.

## Acceptance criteria and falsifiers

| Criterion | Independently observed result | Negative evidence |
| --- | --- | --- |
| AC-1 | 27 role tests include all specified pilot/prod Claude and Codex names. | Removing Astra causes 2 failures; restoring leading-word recognition causes 4. |
| AC-2 | Repair and review-round events require Opus rank; dated rules and waivers retain behavior. | Removing the floor causes 4 failures. |
| AC-3 | All 184 committed tasks at state `fbf834f07625a7ce05a9393bc64aaa1b6cfe83d8`: 0 exit changes, 16 expected message changes, 0 unexpected changes. Real archived peer-policy task with its waiver removed: base 1, candidate 0. | Replacing Astra with Sol returns 1. All 16 message changes consist only of the approved family/floor wording and open model placeholder. |
| AC-4 | Role, PR-watch, and delivery-gate suites exercised the real trigger script. | Reverting both-family wording causes 6 role-test failures. |
| AC-5 | Fresh native Claude session `9531c3e0-bf87-4e67-adf0-5ca975635f5c`: chief engineer/reviewer Opus xhigh; director/observer Sonnet high; exactly four Agent calls with no model argument; zero scoped warnings. | Fresh base session `37c1a991-7bd4-4dfd-84de-b3c8cc93edca`: all four medium, four warnings. Chief-engineer reasoning-field mutation session `cd4502c3-e8d5-49bc-9b07-a4fdcecb0657`: medium and one warning. |
| AC-6 | Seven rows match exactly; lint and 47 lint tests pass; real committed-roster resolver accepts both explicit max and ultra. | Changed Claude cell and changed agent effort are refused; removing the table comparison makes its mutation test fail. |
| AC-7 | Workflow 5781 words at base and head, unchanged budget steps, all four roles named, family phrase counts 1/0; real dispatch suite passed. | Removing director yields reviewer-record gaps; restoring all-workers gives implementation-family count 0. |
| AC-8 | Six fresh stamped Spacedock builds: Claude ideation/validation Opus and implementation Sonnet; Codex null in each stage. | Removing either Opus state setting reruns the real build and reports Sonnet/from defaults. |
| AC-9 | Candidate ADR lint and both installed-script paths pass; changed-record lint with base and --require 0049 returns 0, 48 files/0 legacy. ADR 0026 amendment and ADR 0049 quotes checked against the task's accepted gate records. | Empty disposable ADR folder with --require 0049 returns 1: required ADR 0049 does not exist. |
| AC-10 | Diff from origin/main for release_acceptance.py and release-acceptance extension is empty. PR #764 is still OPEN/Draft; the old design-director seed remains backlog. | Post-merge retirement falsifier is not yet due. FO must retire/check it after merge; neither that action nor a future pass is claimed. |

## Commands and evidence

The exact six-step Captain script is [acceptance.sh](acceptance.sh). It was run unchanged with:

```bash
/bin/bash --noprofile --norc '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-special-roles-follow-the-model-table/.validation-evidence/acceptance.sh'
```

Exit 0. [acceptance-output.log](acceptance-output.log) retains all output, including 27 role tests, 47 lint tests, 9 POC-derivation tests, 48 ADRs, 5781 words, seven table rows and clean release-walk/candidate checks. The script takes less than five minutes and has no graphical surface. It does not rerun native model calls, the historical corpus, the complete CI suite, hosted CI, or post-merge retirement.

Primary command groups:
- [run-ci-suite.py](run-ci-suite.py), [suite-results.json](suite-results.json), [suite-reconciled.json](suite-reconciled.json): all 26 Python commands from the candidate CI job, on the pinned Spacedock plugin `4d158a484ec73e184861067f8ed1e20087fdc26a` and local binary 0.27.2. Initial temporary directories were nested in the repository, which contaminated seven nominally non-Git fixture tests and made the dispatch helper reject the fixture's inherited worktree path. The initial run therefore had seven failed commands; it was not clean.
- Corrected runs: design-surfaces and ADR suites with Git-discovery ceiling; the seven failed unit cases, plus the full dispatch integration, rerun with independent temporary directories as recorded in the corrected/outside-git logs. All failed cases then pass. Aggregate coverage is 1009 unit tests: 1002 passed and 7 existing conditional skips; real dispatch and observer recovery passed. This is reconciled evidence, not a claim of one clean full-suite invocation.
- The seven skips remain four optional design/amendment corpus or historical inputs, one optional journey YAML integration, one optional real dispatch builder, and one obligation-history corpus. The full real dispatch suite ran separately.
- [mutations.py](mutations.py), [mutations.log](mutations.log): five product-code counterexamples, all detected. [poc-mutation.py](poc-mutation.py), [poc-mutation.log](poc-mutation.log): retaining removed ideation model makes the repaired derivation test fail.
- [replay.py](replay.py), [replay-results.json](replay-results.json), [replay-messages.json](replay-messages.json): real pinned task history and actual waiver/Sol controls.
- [native-evidence.json](native-evidence.json), [native-turns.json](native-turns.json): actual Agent inputs, assistant model/perTurnEffort, session/transcript identifiers and hashes. Probe children returned immediately and performed no role review. The first sandbox attempt had no login access; native access succeeded without reading credentials.
- [dispatch-stage-controls.log](dispatch-stage-controls.log), [dispatch-stage-records.json](dispatch-stage-records.json): six real builds and both state-model removals. Fixtures were `/private/tmp/dev-flow-2-sd-wkzd78bn`; these are test artifacts, not user approvals.
- [guards.json](guards.json): number guard PASS at the assigned base; comments 63 code/2 comment lines, 3.2% <= 5%; design surfaces presentable; seven document dispositions matched.
- Required exact command also rerun: `python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since c129cb215c2630d08853eeffae0fd5a2ee7e40c6 --require 0049`, exit 0, 48 files/0 legacy. The invoked skill resolves its package root to the corresponding Codex install; its command passed too.

Evidence probes retain their executed absolute paths. To replay those probes, recreate the named detached checkout at the pinned SHA and the named evidence directory; no product install or config change is required. The Captain acceptance script creates and removes its own detached checkout and does not depend on the other probe directories.

## Findings, limits and ownership

No new candidate finding. The implementation report's limits remain accurate:
- The trigger checker reads declared Reviewer lines; it does not authenticate the model that actually ran. Claude perTurnEffort is a recorded turn setting, not a measurement of reasoning quality. An explicit Agent model argument can override the file.
- Codex settings still pass manually through Paseo. Spacedock stage-worker effort has no dispatch field; the accepted follow-up owns it. Explicit max/ultra roster choices remain permitted. Model equivalence, stage cost and CI cost per PR were not measured; no CI trigger changed.
- RoboRev job 1400's High finding is observed in the saved exact-head review: the old adoption recommendation still says high while the table says xhigh. The dispatch assigns that JSON/prompt work to PR #765; it is outside this candidate's approved files. No clean review, sibling validation, integrated recommendation, merge or release is claimed. FO retains integration and exact-head review.
- Installed 0.34.0 `dispatch_records.py` exits 1 on three Paseo final-reply records because it predates PR #763. The candidate's inherited checker returns `5 dispatch record(s) complete`/0. This is a versioned prerequisite, not a new repair in this task; preserve it at delivery.
- Hosted PR #764 was refreshed on the assigned SHA: five checks SUCCESS. PR #765 is OPEN/Draft at `57321c0b4e9006c2a80c72b4afb1aa368e1ec2a2`, based on this task's branch. A transient sandbox refresh could not connect; the native read-only refresh succeeded.
- AC-10 retirement and its after-merge falsifier remain FO obligations. The task's frontmatter and gate state were not changed.

Goal sufficiency is established at the approved boundary: real Claude settings, recorded-model floors, both-family wording, table/agent agreement and actual stage-model dispatch all work. The removal controls establish necessity for the rank change, floor, effort key, table comparison and explicit stage defaults. The 15 changed files match the approved implementation list plus the separately dispatched POC test repair; no extra capability was retained.

Document impact: updated ADR 0049 and package README; ADR 0026's model-floor amendment is present. Unaffected dispositions verified for ADR 0020 (budget unchanged), ADR 0037 (shared-work rule unchanged), adoption.md (same integration/proof scope), maintain-flow/SKILL.md (same commands/budget contract), and learning.md (historical evidence unchanged). Every added comment is an ADR protection pointer, not implementation narration. Word counts are in [words.json](words.json): workflow 5781->5781, model-roster 634->760, chief-engineer 129->122, reviewer 188->179, director 118->122, observer 135->139; the last two gain only the ADR pointer's four words. No changed graphical screen or product diagram required a screenshot.

