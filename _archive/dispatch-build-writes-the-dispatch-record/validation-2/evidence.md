# Independent validation, repair head

Verdict: REJECTED at `0d84d5d1b96fd674dba3a442d69c2e7898cceccd`, PR #812.
Profile: pilot; no user-visible screen. Base is `334d91e3165953b2ca7191e3308d80b6c02c4a99`, both the implementation base and current main/head merge-base.
Current origin/main was `4deaa2aa108adeaf3c934fd2309e69d90ac3a076`; its later sibling changes are not candidate deletions.
Assigned worktree: `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-dispatch-build-writes-the-dispatch-record`. Its branch/head and clean status were checked before and after. Product bytes were not edited; no product push, PR write, review request, ready or merge action was performed.

## Finding F1: Material

Released user / normal workflow: FO uses the accepted immediate-retry path in a shared state checkout with a partially staged edit to the same last committed record.
Observable harm: when the worktree file equals the original record but its index blob differs, the wrapper returns success and silently replaces the staged content with the worktree version. Status changes from MM to clean without advancing HEAD.
Protected boundary: `contract[kc-dev-flow-2/references/profiles/pilot.md#pilot-bounded-real-use]` requires data safety at exposed persistence/retry seams; implementation follow-up 3 expressly requires existing record bytes and staging to remain intact.
Trigger: `retry-index-probe.json` and the independently rerun `captain-run/retry-index.json`. `dispatch_stage.py` lines 44–46 reuses based only on the worktree bytes; the index check at line 48 is bypassed. Real Spacedock 0.27.2 then executes `git add -A` for the task paths (pinned upstream `internal/dispatch/stamp.go`, `commitAndPublishEntity`).

The probe uses the candidate's existing split-root fixture: successful dispatch; append an annotation; stage the record; restore only worktree bytes to the original; call the same dispatch again; compare index entries, worktree, HEAD and status. No unrelated record or artificial path is involved.
A disposable copy with an index-diff refusal immediately before reuse preserves the staged blob and returns 1 (`retry-index-control.json`). That control is not a product fix.
Recommendation: route F1 to implementation, check index identity before committed-record reuse, and cover this specific retry state. No other Material, Deferred risk, Polish or Needs decision finding was identified.

## Criterion results and their negative controls

- AC-1 PASS: complete record, both checkers, stamped subject, envelope. `implementation-rerun/dispatch-stage.json`; no-stamp/no-model mutants are rejected.
- AC-2 PASS: every nonblank checklist/scope line reaches its matching record section and dispatch artifact; dropping a scope line fails the assertion.
- AC-3 PASS: incomplete notes exit 1 before build, remove only the invocation's new record, leave task/HEAD and spy unchanged; no-removal/build-before-check mutants fail.
- AC-4 PASS: absent candidate exits 1, malformed candidate exits 2, no build; ignoring the checker is rejected.
- AC-5 PASS for its stated normal/failure/retry/new-round cases: no-removal/no-reuse/bytes-only-reuse mutants fail. These green cases omit F1's partially staged committed retry.
- AC-6 PASS: real advance commits before returning an envelope, failed state commit withholds it; pending uncommitted record is now preserved and refused until explicitly committed, after which identical reuse succeeds. Skipping state commit is rejected.
- AC-7 PASS: three approved passages match; 5931/5931 words with delta -2; 47 lint tests, 115 record tests and real dispatch integration pass. Restored base passages fail at 5933/5931. Reverting the authorized observer entry independently fails the existing chat-only contract.
- AC-8 NOT MET at observed run 42464643158: exact-head installation fails with HTTP 504 / curl exit 22; seam, dispatch integration and recovery steps are skipped. `ci-job.log` and `ci-jobs.json` retain the primary evidence. Local unset-binary rejection and CI-step deletion controls pass. The source-wiring counterexample is not a hosted mutated run.

All thirteen original falsifiers and the three repair regressions catch their intended broken behavior; their traces were inspected. The original reported P2 scenarios (untracked, staged/worktree divergence at a new path, and index-only path) are fixed, but F1 shows the preservation claim is incomplete.
CI path filters and pins remain unchanged; cost per PR was not measured. The 504 is missing CI evidence, not evidence of a product defect, and no CI rerun was requested by this worker.

## Commands actually rerun

The implementation runner was executed unchanged in a fresh Bash shell and exited 0:
```bash
SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock SD_PLUGIN_ROOT=/tmp/pr812-validation2.gfsHcD/spacedock-4d158a484ec73e184861067f8ed1e20087fdc26a bash --noprofile --norc '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/dispatch-build-writes-the-dispatch-record/implementation/acceptance.sh' '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-dispatch-build-writes-the-dispatch-record' 0d84d5d1b96fd674dba3a442d69c2e7898cceccd '/tmp/pr812-validation2.gfsHcD/evidence/implementation-rerun'
```
It exports the fixed candidate with git archive; its mutations run in disposable copies. All regular checks and the independent probe execute exported bytes, with bytecode writes disabled. No worktree of the product repository was created or removed; test fixtures own separate temporary repositories.

All 28 CI-listed Python commands exited 0 (1215 tests reported, 11 optional skips) when independently replayed from `/tmp/pr812-validation2.gfsHcD/candidate` via the existing implementation `repair-1/run-package-tests.py`; see `package-tests/results.json` and command logs. SPACEDOCK_BIN is /Users/kent/.local/bin/spacedock 0.27.2; the optional SD_PLUGIN_ROOT is omitted for unit suites as in CI, and provided explicitly for the real integration step.

`run-gates.py` records every command and exit in `gate-results.json`. Git-dependent archive checks receive read-only GIT_DIR plus GIT_WORK_TREE pointing at the export; Git config is unchanged.
```bash
python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/adr_lint.py docs/adr --since 334d91e3165953b2ca7191e3308d80b6c02c4a99 --require 0070
python3 -B kc-dev-flow-2/scripts/adr_lint.py docs/adr --since 334d91e3165953b2ca7191e3308d80b6c02c4a99 --require 0070
```
Installed exit 1 is the settled pre-#806 false positive on ADR 0047; candidate exit 0 checks 63 ADRs. Follow-up 2 explicitly authorizes this substitution. Follow-up 1 authorizes only the observer command-list coupling, verified by the independent revert counterexample.
Number guards, design surfaces, dispatch records, doc impact, comment ratio and diff checks exit 0. Comment ratio is 3/379, 0.8%, below 5%; every added comment was read and only allowed headers/docstrings and the ADR pointer were found.

## Minimal Captain acceptance

Run this exact command in a fresh shell; it was run unchanged and exited 1:
```bash
bash --noprofile --norc '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/dispatch-build-writes-the-dispatch-record/validation-2/acceptance.sh' '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/dispatch-build-writes-the-dispatch-record/validation-2/captain-run'
```
The six commented steps declare the commands and expected observations. Observed: PASS 1 through PASS 5, then `FAIL 6: immediate retry discarded staged-only dispatch content`.
Prerequisites: the declared clean worktree at the exact head, Python 3, Git, tar and installed real Spacedock 0.27.2. The companion `retry-index-probe.py` is retained beside the script.
There is no changed screen. The script substitutes observable local record/commit/index results; it does not cover hosted CI, model execution, actual post-release adoption, merge or release authority.

## Necessity, retained documents and limits

`without-writer.json` independently shows a real direct stamped dispatch creates an envelope but no record; the wrapper then commits the record. The nine changed files map to this goal, its tests/CI, budget, authorized observer coupling or ADR. F1 prevents declaring the accepted Pilot journey safe despite this demonstrated necessity.
`independent-checks.py` confirms approved passages and all 13 document dispositions; the 12 unaffected documents are byte-identical to base and their referenced claims remain valid. `doc-impact-verdicts.json` records each verdict.
Independent per-moment counts are in `lifecycle-words.json`: startup/resume 5933→5931, fresh dispatch including successful checker output 116→101, follow-up 147→87. Other lifecycle obligations and rendered diagrams are unchanged by the product diff.

Implementation limits were judged individually:
- Model and Roster remain caller-supplied; their correctness is not verified by the wrapper. This is accepted D2.
- Package-version and workflow-checkout preflights stay separate, accepted D3.
- Follow-up messages stay manually recorded, accepted Scope exclusion.
- Direct Spacedock bypass remains possible and is independently demonstrated; post-release FO adoption is unverified.
- Identical retry and new-round boundaries work for the listed cases, but their data-safety claim is rejected by F1.
- The old installed ADR failure is not relabelled clean; the authorized candidate checker passes.
- RoboRev disposition remains FO-owned; roborev not run: this validator has no review/publication handoff. The refreshed Codex code-review summary reports completed with no findings at this exact head (pr-comments-latest.json); that does not invalidate F1's independently reproduced failure.
- The existing real binary reports 0.27.2. A fresh source archive was downloaded only to `/tmp/pr812-validation2.gfsHcD` from the full pinned upstream commit 4d158a484ec73e184861067f8ed1e20087fdc26a; SHA256 `16e23e4c0371e7f6712885b691f321e71219d9963dcc402c4a5e814807e70dc0`. The source download succeeds; no download was put in task state.
- Hosted CI is currently blocked by the external download 504, not replaced by local passes. No production obligation, real credential use or product mutation was introduced.
- Task remains at validation; gate approval and any repair/merge/release choice remain with FO/Captain.

