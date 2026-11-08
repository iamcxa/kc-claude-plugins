# Independent validation evidence

Verdict: PASSED for iamcxa/kc-claude-plugins#812 at afa4523468a2e86e6c6e0467591df00bf8e51d35.
Base: 334d91e3165953b2ca7191e3308d80b6c02c4a99 (the candidate's recorded origin/main base).
Profile: pilot; Surfaces: none. No product edits, product commit, push, PR comment, review request, ready action or merge.

## Reproduction and identity

Assigned code worktree: `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-dispatch-build-writes-the-dispatch-record`.
The candidate was exported with `git -C <assigned-worktree> archive afa4523468a2e86e6c6e0467591df00bf8e51d35 | tar -x -C <fresh-/tmp-directory>`.
`candidate.diff` is the read-only base/head diff. The assigned worktree was clean at the declared branch/head before and after testing.
`export.txt`, `implementation-rerun/export.txt`, `implementation-rerun/candidate.txt` and `captain-run/export.txt` identify the archives.
The implementation's existing acceptance runner was rerun, unchanged:
```bash
SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock SD_PLUGIN_ROOT=/tmp/spacedock-0272-source DISPATCH_STAGE_LOG='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/dispatch-build-writes-the-dispatch-record/validation/dispatch-commands.jsonl' bash --noprofile --norc '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/dispatch-build-writes-the-dispatch-record/implementation/acceptance.sh' '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-dispatch-build-writes-the-dispatch-record' afa4523468a2e86e6c6e0467591df00bf8e51d35 '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/dispatch-build-writes-the-dispatch-record/validation/implementation-rerun'
```
Observed exit 0. Its ordinary checks execute in a fresh git archive; its existing mutation runner copies the clean fixed candidate into disposable directories. No repository worktree was created or removed; test fixtures own separate temporary repositories and their metadata.

## Acceptance criteria and falsifiers

| Criterion | Independently rerun evidence | Counterexample caught |
| --- | --- | --- |
| AC-1 | `implementation-rerun/dispatch-stage.json`, test_stamp_commits_complete_record_and_exact_inputs: complete record, both checkers, stamp commit subject and envelope JSON | AC1-no-stamp fails commit-subject assertion; AC1-no-model exits 1 with missing Model |
| AC-2 | The same test compares every nonblank input line against the record's matching section and the dispatched artifact | AC2-drop-scope-line fails on the removed line |
| AC-3 | test_incomplete_record_does_not_build_or_change_state: exit 1, checker diagnostic, no record, unchanged state HEAD/task, no spy marker | AC3-no-removal leaves the record; AC3-build-before-check writes the marker |
| AC-4 | test_validation_candidate_is_required_before_build: missing Candidate exits 1; malformed SHA exits 2; spy remains uncalled | AC4-ignore-checker incorrectly succeeds and fails the expected-exit assertion |
| AC-5 | test_failed_stamp_removes_uncommitted_record_and_passes_error; test_identical_retry_reuses_only_at_adding_commit; test_changed_checklist_creates_next_committed_record; staged-failure cleanup also passes | AC5-no-removal, AC5-no-identical-reuse and AC5-reuse-on-bytes-alone each fail the intended record/commit assertion |
| AC-6 | test_advance_commits_record_and_withholds_envelope_on_commit_failure: state commit, advance envelope, failed commit suppression and retry all pass | AC6-no-state-commit fails the commit-subject assertion |
| AC-7 | Three approved passages compared verbatim; lint 5931/5931; 47 lint tests and 115 record tests pass; test_sd_dispatch exits 0 | AC7-base-passages exits 1 at 5933 versus 5931; observer-base-mutant.log separately proves why the authorized observer edit is needed |
| AC-8 | ci-run.json: run 42462125244, exact head, completed success; pinned binary installation and test_dispatch_stage.py/test_sd_dispatch.py steps succeed | Removing the CI step removes its seam command; unset SPACEDOCK_BIN exits 1 naming the variable |

All 9 seam, 47 lint, and 115 record tests pass with no skips. The real dispatch integration script also passes; it explicitly excludes model execution, skill discovery/reading, human gates, hook bodies and remote merge.
`implementation-rerun/falsifiers/results.json` contains 13/13 caught cases with adjacent patches and failure logs. Failure traces were inspected: they fail the intended assertions, not setup.
CI source still uses package/workflow path filters and the same pinned Spacedock 0.27.2 setup. CI monetary cost per PR was not measured. No CI trigger was broadened.
The AC-8 deletion counterexample is a source-wiring check; no deliberately broken workflow was published.

## Goal sufficiency and necessity

`without-writer.json` records a fresh split-root fixture exercised through the real unwrapped builder: exit 0 and a dispatch artifact, but no task record. Calling the candidate wrapper in that fixture then commits the record under the stamp subject. Commands are in `independent-probe-commands.jsonl`.
All nine changed files map to the writer, real-seam test, existing consumers, required CI invocation, approved word budget or ADR. `observer-base-mutant.log` proves the ninth file's existing chat-only coupling.
No change to the underlying checker, upstream Spacedock, model resolver, two preflights, versions, or unrelated observer rules.
`lifecycle-words.json` is an independent recount: startup/resume 5933 to 5931; fresh dispatch including successful checker output 116 to 101; follow-up 147 to 87. Idle, report/coverage, merge and archive obligations are unchanged.
Every added comment was reviewed: only the permitted ADR pointer and file headers/docstrings; the comment-ratio gate reports 0.9% versus the 5% limit.
`doc-impact.json` and `doc-impact-verdicts.json` cover all 13 affected-document entries; one ADR is updated, twelve are unaffected with reasons agreeing with the candidate diff, retained text and consumer checks.

## Gates and the two FO rulings

Commands, expected exits and observed exits are in `gate-results.json`. Archive-only Git-dependent checks use the assigned worktree's read-only `GIT_DIR` and `GIT_WORK_TREE=<candidate-export>`; no Git configuration was changed.
Installed command:
```bash
python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/adr_lint.py docs/adr --since 334d91e3165953b2ca7191e3308d80b6c02c4a99 --require 0070
```
Observed exit 1: test_sd_dispatch.py's intentional ADR 0047 supersession assertion. `base-installed-adr-lint.log` reproduces the same defect on the base; `installed-adr-lint.log` records the candidate.
Authorized replacement:
```bash
python3 -B kc-dev-flow-2/scripts/adr_lint.py docs/adr --since 334d91e3165953b2ca7191e3308d80b6c02c4a99 --require 0070
```
Observed exit 0, 63 ADRs checked. The historical assertion stays unchanged.
`dispatch/implementation-1-message-1.md` authorizes the observer chat-only entry; reverting only that entry makes lint fail. Message 2 authorizes the candidate checker because the installed 0.35.0 predates merged PR #806.
Number guards exit 0; design surfaces exit 0 (Scope check correctly not run at validation); five dispatch records complete; comment ratio exit 0; diff check exit 0.

## Captain acceptance

No user-visible screen changes. The following executes five annotated steps in a fresh Bash shell, with no hidden shell state:
```bash
bash --noprofile --norc '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/dispatch-build-writes-the-dispatch-record/validation/acceptance.sh' '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/dispatch-build-writes-the-dispatch-record/validation/captain-run'
```
That exact command was run unchanged; observed exit 0 and all five expected PASS lines in `acceptance.log`. Each step states its expected observation in the script; `captain-run/` contains actual command output.
Prerequisites are the declared clean assigned worktree at the candidate, Python 3, Git, tar and /Users/kent/.local/bin/spacedock 0.27.2.
It checks the local writer seam, refusal/retry paths, README coupling and candidate ADR gate. It does not cover hosted CI, release/adoption, model correctness, live worker/model execution, merge authority or a real user batch; hosted CI is separate evidence above.

## Implementation limits reassessed

- PR publication and hosted CI were not run by implementation: the current Draft PR exists and the exact-head CI run now succeeds.
- RoboRev remains delegated to FO and was not run by this validator; no clean review claim is made.
- Old installed ADR exit 1 is retained and reproduced, not relabelled as success. The exact candidate replacement is authorized.
- Model/Roster are caller-supplied; preflight checks stay separate; follow-up records stay manual. These are accepted D2/D3 and Scope exclusions, not missing implementation.
- Direct Spacedock bypass remains possible; the independent probe confirms it. Actual FO adoption after release remains unverified by design.
- Immediate retry and new-round behavior after changed input or intervening state commit were independently exercised.
- Local /tmp/spacedock-0272-source was the implementation-declared source tree. It has no Git metadata; an additional pinned-source download was denied and not retried through another route. Local source provenance was not independently authenticated; exact-head hosted CI separately checks out the declared commit 4d158a484ec73e184861067f8ed1e20087fdc26a and passes the same integration test.
- No new production obligation, credential use or external mutation was introduced by validation. Product/gate/merge authority remains FO/Captain-owned.

Findings under Review-finding disposition: none in Material, Deferred risk, Polish or Needs decision. Existing accepted limits above remain explicit; they are not newly promoted findings.

