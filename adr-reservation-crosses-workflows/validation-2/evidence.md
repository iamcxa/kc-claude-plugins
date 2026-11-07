# Independent validation, repair head of PR #801

Candidate: `ef3ed3e05534e2a997acbdfb055a880fde1f484a`. Parent validation: `6a0a4aec60bb5900a0d363bae912acc5714f5974`. Base: `ba055b8a7a55a787ac989c4cef52d07dd75661ad` (`origin/main` and GitHub PR base at this run). Profile: pilot. Candidate and base were exported with `git archive` into `/tmp/adr-reservation-validation-801-r2/{candidate,base}`. No product edit, product commit, product push, worktree creation/removal, PR comment, review request, ready or merge action occurred.

## Verdict and repair

PASSED on the candidate above. No open Material, Needs decision or Polish finding. The original review finding is Material and fixed: a workflow's deleted remote state branch retained its reservation after a successful fetch, blocking a free number with no stale-fetch warning. Released workflow: an FO reserves/checks after another workflow deletes its published state branch. Harm: reserve skips a free number and check refuses it. Protected boundary: `value-ac[AC-1]` counts live holders and `value-ac[AC-2]` accepts a free number. Trigger: GitHub review comment 4495187504 and the reproduced no-prune mutation in `mutations.log`. The new test releases 0060 after deletion, preserves origin/main, and accepts 0060 at check; removing only `--prune` causes one assertion failure and no runtime errors.

`repair.diff` and `scope.json` prove the parent-to-candidate change consists only of the added fetch argument and one test. Removing the argument restores the parent script byte-for-byte; removing that test restores the parent test AST. The earlier authorized warning assertion, parser behavior, help, workflow wording, ADR amendment, word budget and CI definition remain unchanged. Prior documentary dispositions are carried only after their eight file hashes match; all criterion checks, falsifiers, parser corpus, package checks, live state and CI were rerun rather than carrying their old pass status.

## Acceptance criteria and failing controls

- AC-1: replay A1 reserves 0061 in a single-branch clone; unchanged base reserves 0060. Removing the explicit fetch or origin scan each fails the assertion.
- AC-2: replay A2 refuses held 0060 with R8, the exact foreign holder and renumber instruction, exit 1; A3 accepts free 0061, exit 0. Disabling R8 fails the test.
- AC-3: own folder task reserves 0061 and refuses 0060; remote folder tasks count while archive/review records do not. Restoring a flat-only scan fails.
- AC-4: own pushed task and explicit state-branch override pass; another task on the same branch and a foreign same-slug task without state origin refuse. Whole-branch exclusion, dropping the origin probe, and dropping own-path exclusion each fail.
- AC-5: a base-held number gets R5 without R8. Making both branches run fails the no-double-report assertion.
- AC-6: no-origin and failed-fetch warnings are asserted, and a cached holder still refuses after fetch failure. Removing either diagnostic fails. The integration test preserves the exact complete stderr tuple.
- AC-7: only two approved workflow passages differ. Recount: normalized startup 5993 to 5987; worker Number guards including heading 224 to 221; Reserve 84 to 84; Check 44 to 44; Collision 204 to 201. Whitespace lint budget is 5933/5933. Removing the -6 step is refused. See `words-context.json`, `context-checks.log` and `candidate.diff`.
- AC-8: help names R1 through R8 and own flat/folder plus origin state holders. Removing R8 from the docstring fails.
- AC-9: ADR 0002 preserves its prior text and appends the approved amendment. The Captain's quote and entire bound question match the gate. A wrong quote fails the reader control, and an invalid Status makes installed ADR lint exit 1. Required lint with `--since ba055b8a7a55a787ac989c4cef52d07dd75661ad --require 0002` passes with 61 files checked, 0 legacy, exit 0.
- AC-10: full package suite, number guards and dispatch tests pass; `tests.json` records counts/skips and `checks.json` exact commands. Restoring the base's empty-stderr assertion fails once without runtime errors. GitHub run 42324691650 completed successfully on the exact candidate, including `test_number_guards.py` and the pinned Spacedock integration; `ci-final.json` is the provider receipt. Installed and live candidate checks pass.

Twelve behavior/help/repair mutations were caught with no runtime errors; the unchanged base fails 8 of the 10 cross-workflow tests. Budget, quote, Status and integration controls add four checks. `falsifiers.json` and the referenced logs distinguish expected assertion failures from runtime errors. Parser equality was rerun against 142 committed task records; its state SHA and paths are in `corpus.json`.

## Live state read and its limits

The candidate fetched real origin successfully into disposable bare metadata at `/tmp/adr-reservation-validation-801-r2/live.git`, with shared objects used read-only, and returned PASS without a fallback warning. The earlier sandbox run warned of failed fetch and is not counted as live proof. `live-number-check.log` is the successful output; `record-live.py` documents the receipt.

On-disk state read is limited to `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state`, with 74 sibling flat/folder paths. Remote snapshots are origin/spacedock-state/{dev,dev-recovery-4b20a918,dev-recovery-9826ffcf,dev2,dev2-poc,ship,ship-flow}, with 336 eligible task paths. `live-read-set.json` records exact refs/SHAs and paths. Own disk paths/hashes were collected just after the run; the shared state can change concurrently. No other disk checkout or unpublished journey-map state was read. This candidate amends an ADR rather than adding one; collision rejection is established by the local-origin replays, while the live run establishes successful enumeration and a clean current candidate.

Exact live command:

```bash
python3 -B /tmp/adr-reservation-validation-801-r2/candidate/kc-dev-flow-2/scripts/number_guards.py check --repo /tmp/adr-reservation-validation-801-r2/live.git --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 --task /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/adr-reservation-crosses-workflows.md --base ba055b8a7a55a787ac989c4cef52d07dd75661ad --head ef3ed3e05534e2a997acbdfb055a880fde1f484a
```

## Deferred risks and implementation limits

- F1 Deferred risk — reservation/push race. User/workflow: two FOs reserve before either push. Harm: both obtain one number and one later renumbers. Boundary: `value-ac[AC-2]` promises refusal after publication, not atomic allocation. Trigger: `limits.json` records two 0061 reservations, then R8 after another task publishes it. Becomes Material if a visible holder is accepted or atomic allocation is promised.
- F2 Deferred risk — unpublished or outside-namespace state. User/workflow: a workflow has not met the accepted publication obligation. Harm: its holder is invisible elsewhere. Boundary: `contract[docs/adr/0002-applied-migrations-are-frozen-and-numbers-are-reserved.md#consequences]` requires a unique branch under spacedock-state/*. Trigger: unpushed 0062 affects only its own workflow; a custom namespace is not fetched. Becomes Material if a correctly published in-namespace holder is missed. No-origin warning is verified.
- F3 Deferred risk — failed fetch uses stale refs. User/workflow: reserve/check while origin is unavailable. Harm: a new holder can be missed or a deleted holder retained. Boundary: `value-ac[AC-6]` permits this fallback with a warning. Trigger: both warning controls and cached-holder refusal pass. Successful fetch now prunes deleted holders. Becomes Material if fallback is silent or a successful fetch retains the deleted holder.
- F4 Deferred risk — multiple numbers per task are not enforced. User/workflow: an existing task carries several ADR lines. Harm: cardinality is not rejected. Boundary: Design Limits explicitly excludes enforcement. Trigger: `limits.json` returns both existing lines unchanged. Becomes Material if a later accepted criterion requires exactly one reservation or one of these lines is ignored by collision checking.

Full-suite optional historical/native-input tests and supplemental integration skips remain unverified where their fixture inputs are absent. Native model-worker execution, human gates, delivery-hook body, publication/adoption and remote merge are not proven by these command tests. Independent RoboRev remains FO-owned and was not rerun. New-head hosted CI is now verified, superseding the implementation report's earlier missing-CI limit. CI configuration is unchanged; cost per PR was not measured.

## Goal sufficiency, necessity and retained documents

The published-holder reserve/check route meets the accepted bounded goal. Base and mutation controls show why the state scan, branch-qualified exclusion, R8, diagnostics and prune argument are needed. No new store, remote-write path, config key, flag, version bump or CI trigger is introduced. The exact warning assertion is the only authorized sixth-file change and catches the required diagnostics. Workflow text removes false claims and the -6 step preserves its budget; ADR 0002 records the accepted obligation.

The eight doc-impact entries are unchanged from parent and independently hash-verified in `doc-impact-disposition.json`: ADRs 0020/0037/0049/0052, journey slice map, package README, maintain-flow skill and root learning. Their prior unaffected reasons remain applicable because the repair changes no documented contract beyond removal of a stale deleted holder. ADR 0002 and workflow passages are checked separately above. The only new comment cites the governing ADR, not task/review provenance. `comment-ratio.log` reports 1 comment / 220 code lines, 0.5%, maximum 5%. Design-surface, dispatch-record and diff checks are recorded in `checks.json`.

## Captain acceptance, five steps

Run unchanged in a fresh shell:

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/adr-reservation-crosses-workflows/validation-2/acceptance.sh
```

Prerequisites are the exact assigned repository, Python 3, Git, dispatched 0.35.0 package and adjacent replay.sh. All test mutations stay under /tmp. There is no UI change. Step 1 exports the exact candidate. Step 2 asserts A1=0061, A2=R8/exit 1, A3=PASS and B1=0061. Step 3 expects 38 number-guard tests OK, including deletion/pruning. Step 4 expects 5933/5933 and lint PASS. Step 5 uses read-only Git metadata to run the installed ADR linter and expects 61 checked, 0 legacy, exit 0. The validator ran this exact file successfully; observed output is `acceptance.log`, ending `5/5 ADR lint PASS; acceptance PASS`. Its log write span was 87.067 seconds, under the five-minute bound. It does not prove atomic allocation, unpublished-state visibility, a future network fetch, native gates, publication, adoption or merge.

For additional evidence, `run-checks.py`, `probes.py`, `context-checks.py`, `limits.py` and `repair-evidence.py` declare their candidate/base paths and commands. Recreate those export directories from the pinned SHAs before rerunning. Final report/evidence publication uses the dispatched `spacedock state commit` under validation-2-message-1's explicit state-sync authorization; product publication and delivery remain FO-owned.
