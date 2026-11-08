# Independent validation 4

**PASSED**: PR #812 head `bd9d4abce4e0c61a69079d4e822b6ded45cfdc20`, base `334d91e3165953b2ca7191e3308d80b6c02c4a99`, active AC-1, AC-2, AC-3, AC-4, AC-6, AC-7, AC-8 and amended AC-9. No open product finding remains. This replaces the prior-head validation verdict; no prior-head local or hosted pass was transferred.

Profile is Pilot, bounded real use. Worktree `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-dispatch-build-writes-the-dispatch-record`, branch `spacedock-ensign/dispatch-build-writes-the-dispatch-record`, stayed clean at the assigned head. The observed origin/main is `4deaa2aa108adeaf3c934fd2309e69d90ac3a076`; its merge-base with the candidate is the assigned base. All executable candidate checks used Git archives or disposable mutation copies. No product change, product branch push, PR write, review request, ready action, merge, repository Git configuration write, or product-worktree creation/removal occurred.

## Accepted authority and review disposition

Read the task's current scope, Captain amendment 1, all implementation reports and dispatch addenda, prior validation-3 evidence, and chief-engineer-1. Follow-up 1 authorizes only the observer command-entry coupling; follow-up 2 authorizes the candidate ADR linter while preserving the historical ADR 0047 assertion. Follow-ups 3/4 adopt whole-task preservation and exclusive ownership, and follow-up 6 authorizes warning transport. AC-5 is withdrawn; AC-9 is its accepted replacement.

Read every inline review comment twice through the GitHub connector: two comments, no others returned. Comment **4505536959** (preserve existing uncommitted dispatch records) is fixed: the complete commit scope is checked before record selection, both representations and all owned data survive refusal, and nine guard mutations break the matching preservation oracle. Comment **4505793059** (forward successful record-check warnings) is fixed: both real-binary tests pass, and removing/duplicating/delaying forwarding or deduplicating whole streams fails the intended assertion. The warning exists on wrapper stderr before the real builder starts, shared lines occur once, distinct other-stage warnings survive, and stdout remains the envelope.

Both findings were already dispositioned Material by FO; both are now technically addressed at this head. Both GitHub threads remain unresolved administratively. This validator did not reply or resolve them. Validation-2 F1 is fixed; the prior F2 is settled by Captain amendment 1 and is not reopened. No new Material, Deferred risk, Polish or Needs decision finding. Review-thread administration, PR text, further provider review and delivery remain FO-owned.

## Acceptance evidence

- **AC-1 PASS:** Stamp commits a checker-accepted record and emits the JSON artifact path. Falsifier: No-stamp and no-Model mutations fail.
- **AC-2 PASS:** Every nonblank checklist and scope line reaches its record section and worker artifact. Falsifier: Dropped scope line fails the exact-input assertion.
- **AC-3 PASS:** Incomplete scope exits 1 before builder, removes owned record and preserves task/HEAD. Falsifier: Skipped removal and build-before-check fail.
- **AC-4 PASS:** Missing candidate exits 1; malformed candidate exits 2; neither builds. Falsifier: Ignoring checker failure admits dispatch and fails.
- **AC-6 PASS:** Advance commits before envelope; failed commit withholds envelope and preserves recovery. Falsifier: Removing state commit fails the commit subject assertion.
- **AC-7 PASS:** Three approved passages match, 5931/5931 words, pinned consumers pass. Falsifier: Base passages fail 5933/5931; previous observer entry fails chat-only lint.
- **AC-8 PASS:** Exact-head PR hosted run 42476440927 attempt 1 passed real-binary seam step. Falsifier: Unset binary exits 1; deleting step removes the seam command (local wiring control).
- **AC-9 PASS:** Amended retry contract, cleanup and changed-input/later-commit numbering pass in both layouts. Falsifier: No removal/reuse and bytes-only reuse fail; whole-state staging breaks outside snapshot.

The unchanged implementation acceptance runner exited 0, with **22** seam tests, **47** lint tests, **115** record tests, real dispatch transport and all **13** original controls. Every mutation's failing assertion was inspected, rather than counting any nonzero exit as proof. Four warning mutations, nine complete-scope mutations, one outside-staging mutation and the observer-entry control also passed their intended oracles.

The 28 checked-in CI Python commands were independently replayed at this candidate: **1225 reported tests, 11 optional skips**, every command exit 0. `package-ci/results.json` retains each command and count. Optional source-root skips are retained; real dispatch transport is separately exercised with the pinned source.

`scope-summary.json` verifies **98 unchanged snapshots**, including the **92-case** matrix. Locations/routes include flat and folder task layouts, fresh/retry/new-round/advance, new and reused records, task data and nested/literal reports. States include staged-only, worktree-only, partial and equal changes, additions/deletions/renames/conflicts/types/modes, index flags and stat spoofing. Each refusal is nonzero, emits no envelope, names its path, calls neither builder nor cleanup, and preserves complete scoped/outside data. Independent retry probes reproduce the originally reported staged-only case and accepted outside-staged limitation.

## Exact commands run

Prerequisites: Git, Python 3, tar, installed real Spacedock `/Users/kent/.local/bin/spacedock` reporting 0.27.2, declared worktree above, and source at pinned commit `4d158a484ec73e184861067f8ed1e20087fdc26a`. The source was freshly downloaded only into `/tmp/pr812-validation4.Lmnx4p` from GitHub's commit tarball API; SHA256 `ffb76da0623090f7d06f752601a8f250a0034e2bfeebe6bb163ce4f4f6d4bb3d`. No downloaded source or archive enters task state.

```bash
SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock SD_PLUGIN_ROOT='/tmp/pr812-validation4.Lmnx4p/spacedock-source' DISPATCH_SCOPE_LOG='/tmp/pr812-validation4.Lmnx4p/scope-snapshots.jsonl' DISPATCH_STAGE_LOG='/tmp/pr812-validation4.Lmnx4p/dispatch-commands.jsonl' bash --noprofile --norc '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/dispatch-build-writes-the-dispatch-record/implementation/acceptance.sh' '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-dispatch-build-writes-the-dispatch-record' bd9d4abce4e0c61a69079d4e822b6ded45cfdc20 '/tmp/pr812-validation4.Lmnx4p/acceptance'
SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock SD_PLUGIN_ROOT='/tmp/pr812-validation4.Lmnx4p/spacedock-source' python3 -B '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/dispatch-build-writes-the-dispatch-record/implementation/repair-1/run-package-tests.py' --code-root '/tmp/pr812-validation4.Lmnx4p/candidate' --output-dir '/tmp/pr812-validation4.Lmnx4p/package-ci'
SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock python3 -B '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/dispatch-build-writes-the-dispatch-record/implementation/repair-3/warning-falsifiers.py' --code-root '/tmp/pr812-validation4.Lmnx4p/candidate' --output-dir '/tmp/pr812-validation4.Lmnx4p/warning-falsifiers'
SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock python3 -B '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/dispatch-build-writes-the-dispatch-record/implementation/repair-2/scope-falsifiers.py' --code-root '/tmp/pr812-validation4.Lmnx4p/candidate' --output-dir '/tmp/pr812-validation4.Lmnx4p/scope-falsifiers'
python3 -B '/tmp/pr812-validation4.Lmnx4p/run-gates.py'
SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock python3 -B '/tmp/pr812-validation4.Lmnx4p/independent-checks.py'
SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock python3 -B '/tmp/pr812-validation4.Lmnx4p/outside-staged-falsifier.py'
```

All exited 0. The package runner and unchanged acceptance script are existing state helpers, not new product tests. Their logs are retained beside this report. Auxiliary source copies and test fixtures use temporary repositories, never this product repository's shared configuration.

Git-dependent archive gates use read-only metadata from `git -C '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-dispatch-build-writes-the-dispatch-record' rev-parse --absolute-git-dir`, with GIT_WORK_TREE pointing to `/tmp/pr812-validation4.Lmnx4p/candidate`. The required installed check was actually run:

```bash
python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/adr_lint.py docs/adr --since 334d91e3165953b2ca7191e3308d80b6c02c4a99 --require 0070
python3 -B kc-dev-flow-2/scripts/adr_lint.py docs/adr --since 334d91e3165953b2ca7191e3308d80b6c02c4a99 --require 0070
```

Installed exit **1**: the known pre-#806 false positive on the unchanged historical ADR 0047 supersession assertion. Candidate exit **0**: 63 ADRs checked, 0 legacy. Follow-up 2 expressly authorizes this substitution; the installed tool is not called clean. Other loaded-package tools come from `/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0`; exact command arrays and exits are in `gate-results.json`.

Number guards, dispatch records, design surfaces, doc impact and diff checks exit 0. Design surfaces says the task is presentable and explicitly does not run Scope scanning at validation. Comment ratio: **3 comment lines / 822 code lines = 0.4%**, below 5%; all added comments were read, and the functional ADR pointer is retained.

## Captain acceptance script

No screen changed. This six-step command exercises observable CLI behavior and is self-contained with its two adjacent fixture probes:

```bash
bash --noprofile --norc '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/dispatch-build-writes-the-dispatch-record/validation-4/acceptance.sh' '/tmp/pr812-validation4.Lmnx4p/captain-final'
```

I ran that exact command unchanged in a fresh Bash shell: exit **0**, `captain-final.log` contains PASS 1 through PASS 6 (plus 6a). Its steps export/check the exact clean head and binary, run nine selected seam/warning tests, verify 5931/5931 words, refuse the missing binary, run the authorized ADR checker, then exercise both retry-preservation boundaries. It finished within the five-minute bound. Output and helper files are preserved here; no secret is required.

It does not replace the full preservation matrix, package regression suite, hosted run, worker model execution, post-release adoption, provider review, Captain gate or delivery. The outside-staging removal happens only inside a disposable diagnostic fixture; it is not advice to modify another worker's index.

## Hosted evidence

GitHub run **42476440927**, attempt **1**, `kc-dev-flow-2 tests`, is completed **success** and explicitly binds `head_sha=bd9d4abce4e0c61a69079d4e822b6ded45cfdc20`. Job **128718733545** passes installation of the pinned binary, `test_dispatch_stage.py` (**22 tests**), `test_sd_dispatch.py` (real 0.27.2 transport), and observer recovery. Sources: `hosted-run.json`, `hosted-jobs.json`, `hosted-job.log`, and https://github.com/iamcxa/kc-claude-plugins/actions/runs/42476440927.

Precisely, the PR workflow checks GitHub merge ref `e2d8c52fdc3702ffefd605d251144a7ca93dc10b`, merging this head into `4deaa2aa108adeaf3c934fd2309e69d90ac3a076`; the checkout log confirms both parents. This is the requested PR run associated with the exact candidate, not a claim that the hosted job checked out the bare head. Bare-head local archives were checked independently. AC-8 is satisfied; earlier HTTP-504 runs and prior-head success were not reused. CI triggers retain the existing package/workflow path filters; **CI cost per PR was not measured**.

## Implementation limits, judged

- Model and roster remain supplied by FO; correctness of those claims is not verified, per accepted D2.
- Package-version/workflow preflights remain separate, per D3; wrapper tests do not claim to perform them.
- Follow-up messages remain manually recorded, the explicit non-goal.
- Direct native builder calls can bypass record writing. `without-writer.json` independently shows direct success without a record and wrapper success with its committed record. Actual FO adoption after release remains unverified.
- Whole-task refusal intentionally blocks pending same-task work. Under exclusive ownership, scoped HEAD/index/worktree preservation and owned-only cleanup are exercised. No transaction lock or concurrent-writer guarantee is claimed; exclusivity must last through check/build/commit/cleanup.
- Advance commit failure leaves the pending record and withholds the envelope; intentional owner reconciliation/commit recovers it. This is exercised, not silently called automatic recovery.
- Immediate no-op retry with another task staged exits 1 without an envelope and preserves every byte/index entry in both layouts. Clean retry recovers; source `internal/dispatch/stamp.go` checks global cached paths before a path-scoped commit. This is exactly accepted AC-9.
- Installed ADR lint's false positive remains recorded with the authorized candidate check; no historical assertion or product linter was edited.
- Implementation's publication/hosted evidence limits are refreshed here: PR is still Draft/open at the specified head and hosted AC-8 passes. RoboRev and later provider review were not run by this validator; earlier-head review evidence is not promoted.
- Synthetic gates and real-binary fixtures do not prove live worker execution, human acceptance, production use, merged delivery or release. FO/Captain retain those actions.
- Original fixture transport logs explicitly leave skill discovery/reading, worker execution, human gates, delivery hook body and remote merge untested. Those are outside this task's accepted automatic-record seam.

## Sufficiency, necessity and retained documents

The bounded journey now writes the actual inputs before dispatch, checks them, commits through the real builder, preserves pre-existing task work and delivers required successful-check warnings before build. The direct-builder counterexample proves why the wrapper is needed. Each of the nine base-relative changed files maps to this writer, its real seam/CI, word budget and consumer pins, the authorized observer coupling, or ADR 0070. No unrelated product scope is retained.

All 13 doc-impact entries have itemized dispositions in `doc-impact-verdicts.json`; the 12 unaffected documents are byte-identical to base and their referenced claims were inspected. ADR 0070 matches the accepted words and write/check/build order. The historical harness files match only the generic argparse name and are unrelated. Three approved workflow passages remain verbatim. Independent lifecycle counts: startup/resume 5933 to 5931, clean fresh dispatch including checker output 116 to 101, follow-up 147 to 87. Warning-bearing dispatches now correctly retain their owed reminder; that repair is not a claim of zero diagnostic output. No product diagram was changed or new rendering proof claimed.

`export-integrity.json` verifies all 1,582 tracked file bytes in each inspected export. Product SHA/branch/status stayed unchanged. The task remains at validation; this report supplies the independent verdict and does not advance or approve its gate.
