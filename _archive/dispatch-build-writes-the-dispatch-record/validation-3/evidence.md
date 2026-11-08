# Independent validation 3: exact candidate and amended retry contract

Verdict: **REJECTED for missing hosted evidence only** at PR #812 head `778367adde2e20e0b3e51966ddba2d9f77f9e614`. The amended local product criteria pass. AC-8 remains externally blocked; this verdict is not a request for a product repair for the HTTP 504.

Profile: pilot (bounded real use); no changed user screen. Base: `334d91e3165953b2ca7191e3308d80b6c02c4a99`, also the merge-base with observed origin/main `4deaa2aa108adeaf3c934fd2309e69d90ac3a076`. Product worktree: `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-dispatch-build-writes-the-dispatch-record`, branch `spacedock-ensign/dispatch-build-writes-the-dispatch-record`. Its head, branch and clean status were checked before and after. No product edits, product push, PR writes, review request, ready, merge, Git config writes or product worktree creation/removal occurred.

## Authority and current criteria

Read the task, all implementation dispatches and reports, `review/chief-engineer-1.md`, and `dispatch/validation-3-message-1.md`. Implementation follow-up 1 narrowly authorizes the observer command-list coupling; follow-up 2 preserves the intentional ADR 0047 supersession assertion and authorizes the candidate ADR linter. Follow-ups 3 and 4 require data preservation and one complete-scope precondition.

During this validation, the independently reproduced outside-staged retry was initially a Material finding F2 under AC-5. The Captain then chose 「接受為已知限制（建議）」 in amendment 1 on 2026-11-08. The task preserves the superseded AC-5 text in that amendment and introduces AC-9: no other-task staging means retry succeeds; other-task staging means exit 1, no envelope, no file/index changes. `design-surfaces-amended.log` exits 0. Scope scanning explicitly says not run because the task is at validation. The candidate did not change.

F2 is **settled by Captain amendment 1**, not an open repair finding. Validation-2 F1, staged-only content loss on the reused committed record, is fixed. No open Material, Deferred risk, Polish or Needs decision finding remains within the amended product scope. Missing AC-8 evidence remains a separate delivery hold.

## Acceptance results and falsifiers

- AC-1 PASS: the real 0.27.2 builder commits the accepted record with the stamped subject; both record checkers accept it and stdout contains the dispatch artifact path. No-stamp and missing-Model mutants fail.
- AC-2 PASS: every nonblank checklist/scope line reaches its matching record section and the worker artifact. Dropping one scope line fails.
- AC-3 PASS: missing Package root exits 1 with the prefixed diagnostic, no envelope, no record, unchanged task/HEAD and no builder invocation. Removal omission and build-before-check mutants fail.
- AC-4 PASS: omitted candidate exits 1 with the checker message; malformed candidate exits 2 before writing. Ignoring the checker fails.
- AC-6 PASS: advance commits with `state: update <slug>` before its envelope; commit failure withholds output and preserves pending record. A later intentional owner commit permits retry. Skipping state commit fails.
- AC-7 PASS: all three approved passages match; lint reports 5931/5931, delta -2; 47 lint tests, 115 record tests and real dispatch integration pass. Restoring base passages fails at 5933/5931. Independently reverting the authorized observer list entry fails the chat-only contract.
- AC-8 BLOCKED: exact-head hosted run `42468880068` fails installing pinned Spacedock with HTTP 504 / curl exit 22, skipping `test_dispatch_stage.py`, `test_sd_dispatch.py` and recovery. Local missing-binary hold and deleted-CI-step control pass. These are not hosted proof.
- AC-9 PASS (replaces AC-5): failed-stamp cleanup, clean immediate reuse, later-commit numbering and changed-input numbering pass. In both flat and folder layouts, unrelated staging exists before the successful first build; the immediate retry exits 1 with empty stdout and identical complete snapshots. Removing only outside staging in the disposable fixture restores exit 0 with no second record. No-removal, no-reuse and bytes-only-reuse mutants fail. An extra mutant staging the whole state repository before committed-record reuse fails the outside-index preservation assertion.

Original mutation output filenames retain AC5 because those executions preceded amendment 1; their behavior maps to AC-9. `acceptance/falsifiers/results.json` holds all 13 original controls; `scope-falsifiers/results.json` holds nine class controls; `outside-staged-falsifier.json` holds the additional amended-boundary control. Every intended mutation was rejected for its relevant assertion, rather than being counted solely from a nonzero subprocess.

## Class repair against chief-engineer-1

Source review confirms one `check_task_scope(state, scope)` call after read-only `resolve_scope` and before `select_record`, covering fresh, retry, new-round and advance. The scope matches the real builder's `entityCommitPaths`: flat task file plus companion directory, or the folder-form task directory. Literal pathspecs and NUL-delimited reads compare HEAD/index, raw worktree bytes and executable modes; conflicts, unsupported types/paths, hidden index flags and nonignored untracked data hold.

`scope-summary.json` independently checks **98 unchanged snapshots**, including the **92-row matrix**. Locations include task, older dispatch, reused record, new record, nested report and a literal filename containing spaces/brackets/newline; routes cover both task layouts and all four dispatch paths. States include three-version divergence, additions/deletions/renames, conflicts, types/modes, stat spoofing and index flags. All refusals have nonzero exit, empty stdout, named diagnostic, no builder or cleanup call, and preserve HEAD, all file bytes/existence/modes, semantic index entries/flags and outside sentinels.

Nine isolated mutants remove the guard, index comparison, worktree comparison or untracked check; narrow the scope to the record or dispatch directory; move the guard after record creation; or bypass it on retry/advance. Each fails the matching preservation assertion and produces differing snapshots. The original F1 also passes an independent retained retry-index probe.

Allowed routes use the real builder: clean stamping/exact inputs, identical reuse, changed-input/later-commit numbering, owner reconciliation, advance commit-before-envelope, checker failure, staged-then-failed cleanup and committed-then-assembly failure retry. Unrelated work remains outside the task commit. The accepted no-op retry limitation is separately exercised; it is not claimed as successful dispatch.

Exclusive same-task writing must last through check/build/commit/cleanup. This precondition is not a transaction lock and establishes no overlapping-writer safety. The diagnostic tells the owner to preserve/reconcile versions before an intentional commit, not to blindly state-commit divergent contents. No upstream transaction redesign is claimed or required by this accepted boundary.

## Commands actually run

The original implementation acceptance runner was run unchanged in a fresh Bash shell, exited 0, and wrote `acceptance/candidate.txt` only after its chain passed:

```bash
SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock SD_PLUGIN_ROOT=/tmp/pr812-validation3.KfmHwh/spacedock-4d158a484ec73e184861067f8ed1e20087fdc26a DISPATCH_SCOPE_LOG=/tmp/pr812-validation3.KfmHwh/evidence/scope-snapshots.jsonl bash --noprofile --norc '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/dispatch-build-writes-the-dispatch-record/implementation/acceptance.sh' '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-dispatch-build-writes-the-dispatch-record' 778367adde2e20e0b3e51966ddba2d9f77f9e614 '/tmp/pr812-validation3.KfmHwh/evidence/acceptance'
```

Its helper revisions at execution predate the AC-9 label update; the state history at `12fc3a66d` retains that version. Tests run from a fresh Git archive and mutations from disposable candidate copies with bytecode disabled; no fixture uses the product repository's Git configuration.

The 28 checked-in CI Python commands were independently replayed via the existing `implementation/repair-1/run-package-tests.py` from `/tmp/pr812-validation3.KfmHwh/export`: 1223 tests reported, 11 optional skips, all 28 commands exit 0. `package-tests/results.json` retains exact commands. Optional SD_PLUGIN_ROOT is unset for unit commands as in CI and explicitly supplied for real integration. Separate original acceptance records 20 seam tests, 47 lint tests, 115 record tests and real transport.

`run-gates.py` and `gate-results.json` retain every command and exit. Git-dependent archive checks use read-only GIT_DIR with GIT_WORK_TREE pointing to the export:

```bash
python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/adr_lint.py docs/adr --since 334d91e3165953b2ca7191e3308d80b6c02c4a99 --require 0070
python3 -B kc-dev-flow-2/scripts/adr_lint.py docs/adr --since 334d91e3165953b2ca7191e3308d80b6c02c4a99 --require 0070
```

Installed exit **1** is the known pre-#806 false positive on the intentional ADR 0047 assertion. Candidate exit **0**, 63 ADRs, is authorized by implementation follow-up 2; installed success is not claimed. Number guards, dispatch records, design surfaces, document impact and diff checks exit 0. Comment ratio is 3/776 = 0.4%, maximum 5%; all added comments were read and only module docstrings and the ADR pointer are substantive comments.

## Minimal Captain acceptance

Run exactly this in a fresh shell:

```bash
bash --noprofile --norc '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/dispatch-build-writes-the-dispatch-record/validation-3/acceptance.sh' '/tmp/pr812-validation3.KfmHwh/evidence/captain-run-amended'
```

The six commented steps name their exact commands and expected observations. Prerequisites are the declared clean candidate worktree, installed real Spacedock 0.27.2, Python 3, Git and tar; the two companion probes are beside the script. It exports rather than executing from the product worktree. There is no changed screen.

The validator ran the script unchanged after amendment with the output directory `/tmp/pr812-validation3.KfmHwh/evidence/captain-run-amended`; `captain-run-amended.log` records PASS 1–6 and exit 0. The earlier failure under AC-5 is retained in `captain-run-final.log` and `acceptance-before-amendment.sh`; it is not overwritten or relabelled as a pass.

This minimal local script does not replace the full matrix, all package tests, hosted CI, model execution, real post-release adoption, review or delivery authority. The outside-staging removal is a disposable-fixture diagnostic control, not advice to change another worker's real index.

## Hosted evidence and limits

Latest same-head runs are recorded in `ci-runs-latest.json` and `ci-run.json`. Main run `42468880068` is the required real-binary evidence, and it did not reach the seam. The other failed runs are `42468880154` and `42468880263`; FO's dispatch and follow-up attribute those to HTTP 504 downloads. The validator directly retained the main run's failure log `ci-failed.log`. FO owns reruns after the external release-asset download recovers. No hosted mutation or rerun was requested through GitHub by this worker.

CI path filters and pins are unchanged; **cost per PR was not measured**. Local success cannot replace AC-8.

Implementation limits judged individually:
- FO-supplied Model/Roster correctness is not verified: accepted design decision 2.
- Package version/workflow preflights remain separate: accepted design decision 3.
- Follow-up messages remain manually recorded: accepted scope exclusion.
- Direct Spacedock bypass still creates no record; independently reproduced in `without-writer.json`. Post-release FO adoption remains unverified.
- Existing-record preservation and whole-scope refusal are verified under exclusive ownership; no concurrency-safety claim.
- Pending advance-record recovery requires intentional owner reconciliation/commit; the record and lack of envelope are verified.
- No-op retry with other-task staging is the exact accepted AC-9 limit; both layouts preserve all bytes/index entries.
- The installed ADR error remains recorded, with the expressly authorized candidate checker result.
- roborev not run: FO owns local review and publication. No independent external-review disposition is claimed here.
- Worker execution, Captain gates, real adoption, merge and release remain unverified; local synthetic approvals are test inputs.

The real binary reports 0.27.2. A fresh source archive at pinned commit `4d158a484ec73e184861067f8ed1e20087fdc26a` was downloaded only under `/tmp/pr812-validation3.KfmHwh`; SHA256 `16e23e4c0371e7f6712885b691f321e71219d9963dcc402c4a5e814807e70dc0`. No download is stored in task state. `export-integrity.json` checks 1,582 tracked files in each of two exports with zero byte mismatches.

## Sufficiency, necessity and retained documents

Within the amended local Pilot boundary, the wrapper records actual dispatch inputs, rejects incomplete data, preserves pre-existing scope state and exercises recovery. Hosted delivery sufficiency remains unproved solely because AC-8 is blocked.

The real direct-builder control produces an envelope with no record; the wrapper then commits the record. Each of the nine changed product files maps to the writer, real seam tests/CI, exact budget and consumers, the authorized observer coupling, or ADR 0070. Removing the writer, checks, cleanup, reuse rules or commit seam breaks the named controls; retained changes have no unrelated platform scope.

`doc-impact-verdicts.json` records all 13 affected document dispositions, with the 12 unaffected documents verified byte-identical to base and their referenced claims reviewed. ADR 0070 accurately records the approved package-writer decision. Independent lifecycle counts: startup/resume 5933 to 5931; fresh dispatch including successful checker output 116 to 101; follow-up 147 to 87. Other lifecycle obligations and product diagrams are unchanged. No new diagram-rendering proof is claimed.

The task remains validation. FO/Captain retain the hosted-evidence, gate, merge and release decisions.

