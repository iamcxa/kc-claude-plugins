# Independent validation of PR #807

Candidate: `2760f259379e9c3bb43bab9efa56d90c5b657ab1`.
Base: `139feeaee7ce037a0c6535568cd6bd103155cbae` (`origin/main` at validation).
Profile: Pilot. Product code was read and run from two `git archive` exports under `/tmp/validate-design-check-807-5kl7jk6e`; the assigned code worktree was not edited.

## Captain acceptance

Requires bash, git, tar, python3, the named code repository containing the candidate/base, and the named local Relay repository containing `spacedock-state/dev2` and replay commit `6008953a2501c4ff82bfb50b9d76f649259802a8`. Paths are explicit defaults in the script; `CODE_REPO` and `RELAY_REPO` may select equivalent local repositories. No credentials are needed with the recorded local sources.

Run unchanged from any directory:

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/design-check-says-not-run-without-a-scope/validation-1/acceptance.sh
```

The script has four steps with expected output written above each command block:
1. Export pinned code and clone the pinned Relay state into fresh `/tmp` directories; print the identity.
2. Run the candidate CLI on the original Relay task; print presentable and the exact `scope check not run: backlog briefing binds llms-teaches-versions/review/backlog-gate.md, not this task file`, exit 0.
3. Run the base CLI on the same task; reproduce `Scope changed after the backlog gate (01d0e0e4)`, exit 1.
4. Run all 25 `ScopeCheckTests`; additions/removals hold, the folder/untracked/archive case stays checked, and dated amendments take priority. Expected `OK` and `ACCEPTANCE PASS`.

Observed output is in `acceptance.log`: all four passed in a fresh `bash --noprofile --norc`. This script covers the selected behavior and negative control; it does not replace the full regression suite, hosted review, merge, publication or installed-plugin adoption. The task records `Surfaces: none` and no graphical screen change; the observable surface is the CLI output above.

## Criteria and falsifiers

- AC-1: independently cloned `/Users/kent/conductor/workspaces/subspace-relay/dhaka`, branch `spacedock-state/dev2`, checked out full replay SHA above. Candidate exit 0 with exact first two lines; base and removed-guard mutation both exit 1 naming `01d0e0e4`. `replay.json` and `relay-*.log` preserve stdout/exit. The Relay clone is clean after replay; no source Relay files were changed.
- AC-2: all 25 Scope cases pass, including the unchanged original added/removed Scope, amendment, fence and exempt-prefix cases. Unconditional guard mutation fails the named added-line assertion; guessed-parent path fails the folder/archive case. `acceptance.log`, `focused-tests.log`, `mutations.json` and corresponding mutation logs.
- AC-3: foreign files with and without their own Scope produce not run; the no-Scope fixture remains not run after adding a task Scope line. A missing-Scope-only guard fails the copied-Scope fixture. `mutations.json`, `mutation-guard-only-when-Scope-missing.log`.
- AC-4: foreign binding with dated amendment is clean for the working copy and the amendment commit, then holds a further unrecorded Scope line. Returning before amendment lookup fails that assertion. `mutation-guard-before-amendment-lookup.log`.
- AC-5: `diff-files.txt` has only the two approved Python paths; `diff.patch` and source-blob comparison pin exact bytes. The boundary predicate rejects a third unapproved path. Both workflow files are identical and contain 5933 words (`scope-integrity.json`). Lint passes. No CI, manifest, version, README or ADR source changed.

The replay and mutation drivers reuse the implementation's instruments, inspected and copied into a fresh evidence directory with only source/export locations adjusted. Each instrument was rerun independently against the archived candidate; every code mutation runs in a new bytecode-free temporary copy. `metadata.json` names the original execution root, and `checks.json` records every command/cwd/exit. The self-contained Captain script creates its own exports and Relay clone and has no dependency on that original execution root.

## Other verification

The package scripts come from the dispatched `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0` install. Candidate behavior/lint/tests use the candidate export. For Git-aware package checks only, `GIT_DIR` pointed at the assigned worktree's existing Git metadata and `GIT_WORK_TREE` at the candidate export; all Git operations were read-only. Unit tests did not inherit those variables.

Exact ADR command (cwd the candidate export with those two variables):

```bash
python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/adr_lint.py docs/adr --since 139feeaee7ce037a0c6535568cd6bd103155cbae --require 0027 0042 0048
```

Exit 0; 62 ADR files, zero legacy. Number guards exit 0 (`no findings`; migration guard skipped because no migrations-path is declared and the task has no database changes). Comment ratio exits 0: 0 comment lines / 60 code lines, 0.0%, maximum 5%; the changed module docstring accurately describes the added boundary. Dispatch records and the package task-design check exit 0; the task's own Scope check says not run because it is now at validation, while the Relay and test cases explicitly exercise ideation.

Affected documents from `doc-impact.json` were independently read:
- `docs/adr/0041-seed-admission-enforces-required-fields.md`: unaffected; seed-only admission and its protected required fields do not change.
- `docs/adr/0057-rewritten-criteria-are-compared-with-the-captains-words.md`: unaffected; replacement-word comparison and dispatch validation do not change.
No retained diagram was changed; no rendered-diagram claim is made. The only changed prose is the checked module docstring.

## Goal sufficiency, necessity, and limits

The original false hold disappears at the real recorded binding; removing the new guard brings it back. Each helper/branch is tied to identity normalization, the new reason, or amendment priority; deleting or weakening those boundaries is detected by the named mutations. The four added tests exercise those behaviors. The two-file change is sufficient and bounded for the accepted Pilot goal.

The Captain's ideation decision explicitly accepted foreign binding option A and dropping the gate-prepare warning. Consequently a foreign binding without a dated amendment receives no Scope comparison even if its own file contains Scope; this is the accepted tradeoff, not a pass claim for unperformed comparison. The unchanged checker remains ideation-only and does not authenticate whether amendment words truly came from the Captain. No upstream Spacedock warning or binding support was added.

Implementation's publication, RoboRev and CI omissions were accurately marked not run at implementation. Current GitHub read (`pr.json`) confirms Draft PR #807, OPEN, exact head and base; reported unit, parity, live-route, docs-build and security checks succeed, docs deploy is skipped. This is an observation of provider results, not this worker running hosted CI, not a complete required-check/merge-readiness audit, and not local RoboRev evidence. FO retains exact-head reviews, gate acceptance, merge and delivery. CI cost per PR was not measured; no CI trigger changed.

Review-finding disposition: no new Material, Deferred risk, Polish or Needs decision finding on the candidate (`findings.json` is empty). Accepted/unchanged limits above are not new findings. The state-commit/no-push ambiguity was resolved by FO in `dispatch/validation-1-message-1.md`: the helper's state-branch sync is allowed, product publication remains prohibited.

The original Relay task Scope was also compared against its own task file at bound commit `01d0e0e440632472fdfc0c4ce1bd21ccd7d7d974`: identical (`relay-identity.json`). Thus the base failure is confirmed as a cross-file baseline error, not an unnoticed real Scope edit.

## Regression conclusion

`python3 -B -m unittest discover -s kc-dev-flow-2/scripts` at the candidate export exited 0: 985 tests, 7 existing skips (978 executed). `discover.log` is the raw output. The focused checker exited 0: 217 tests, 4 existing skips. The skipped checks require optional historical-corpus inputs or the real-builder package environment; they do not represent passing historical-corpus or host coverage. The independent Relay replay and all 25 Scope cases were executed, not skipped. Python version: 3.15.0.

Verdict: PASSED recommendation for candidate `2760f259379e9c3bb43bab9efa56d90c5b657ab1`, within the accepted Pilot scope. No product edits or candidate commits were made during validation.
