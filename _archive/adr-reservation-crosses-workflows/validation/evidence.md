# Independent validation of PR #801

Candidate: `6a0a4aec60bb5900a0d363bae912acc5714f5974`. Base: `ba055b8a7a55a787ac989c4cef52d07dd75661ad` (`origin/main` at dispatch and GitHub validation read). Profile: pilot. The validator executed archived candidate bytes under `/tmp/adr-reservation-validation-801/candidate`; `/tmp/adr-reservation-validation-801/base` is the archived base. Product worktree remained clean on `spacedock-ensign/adr-reservation-crosses-workflows`. No worktree of the shared repository was created/removed, no shared Git config changed, no product commit, push, PR comment, review request or ready/merge action occurred.

## Goal sufficiency and minimal necessity

The accepted route works for published reservations in the shared repository's `spacedock-state/*` namespace: a single-branch clone fetches holders, reserve skips them, and check refuses a manually selected held number before a merge ask. The same replay against unchanged base returns 0060 and allows the collision; it also misses a folder-form sibling. Existing reserve/check functions are repaired without a new store, flag, configuration key or remote-write path. Parsing text from Git is needed to read holders, and path/branch exclusion is needed to permit the caller's own pushed copy without hiding other tasks. R5 precedence prevents duplicate reporting. The two README edits remove now-false words and the -6 step preserves ADR 0020's exact budget. ADR 0002 records the approved obligation. The added sixth file is necessary because the existing integration replay asserted empty stderr; AST comparison shows exactly one string constant changed and all other syntax is identical (`scope.json`). Reverting that test expectation fails on the exact two newly required warning lines (`ac10-falsifier.log`, exit 1); no stderr assertion is removed.

## Acceptance criteria and falsifiers

- AC-1: `replay-candidate.log` A1 returns 0061, `replay-base.log` returns 0060. Existing test uses a single-branch clone. Removing explicit state fetch or origin scan each causes an assertion failure.
- AC-2: A2 refuses 0060 with exact R8 holder and renumber instruction, exit 1; A3 accepts free 0061. Disabling R8 causes an assertion failure.
- AC-3: B1 returns 0061; the own-folder test also refuses 0060 at check. Flat-only scanning causes an assertion failure. Remote folder holders and archive/review exclusions also pass.
- AC-4: own pushed copy and explicit state-branch override pass; sibling on own branch and same-slug foreign holder with no origin fail. Whole-branch exclusion, missing origin probe, and removal of own-path exclusion each cause assertion failures.
- AC-5: base-held number produces R5 without R8. Replacing `elif` with `if` causes the no-double-report assertion to fail.
- AC-6: exact no-origin and failed-fetch diagnostics are checked; cached remote holders continue to refuse. Removing either warning causes an assertion failure. The sixth-file integration assertion checks both stderr lines exactly.
- AC-7: independently written line-based section/bullet counter confirms normalized startup 5993→5987, worker Number guards 224→221, Reserve 84→84, Check 44→44, Collision 204→201; lint whitespace budget 5939→5933. Only the two approved passages differ. Removing the -6 budget step is refused. See `independent-words.json`, `context-checks.log`, `candidate.diff`.
- AC-8: all R1–R8 and holder sources appear in help. Removing R8 from the docstring causes its test assertion to fail.
- AC-9: the amendment matches both the Captain's exact 「核准（建議）」 and the full bound question in the ideation gate; all original ADR text remains. Wrong-quote control is refused by the reader check; invalid Status is refused by installed ADR lint, exit 1. `adr-lint.log` passes, exit 0, 61 files, 0 legacy.
- AC-10: full suite and supplemental results are in `tests.json`; candidate CI is in `ci-final.json`. The restored empty-stderr expectation is a failing regression control. Installed and live candidate number checks both pass on exact candidate/base.

Behavioral/help mutation rerun: `probes.py` reuses the existing candidate tests against throwaway mutated scripts. All 11 mutations produce assertion failures, with no runtime errors. Unchanged base fails seven of nine cross-workflow tests. `context-checks.py` reruns the author's budget/quote controls; the additional independent recount uses line scanning rather than the author's section regex. `corpus.json` confirms parser output equality on 142 committed live/archive tasks at its recorded state SHA; this is parser equivalence, not a claim that every historic candidate was replayed.

## Live shared-state read

The initial sandboxed remote fetch failed and emitted the expected local-refs-only warning; it was not counted as live proof. The same command was rerun with approved network access using an isolated bare Git repository at `/tmp/adr-reservation-validation-801/live.git`. It fetched successfully and returned `PASS: no findings`, exit 0, with no fallback warning. The bare repository stores only disposable validation refs and objects; no shared branch/ref was changed.

Exact command:

```bash
python3 -B /tmp/adr-reservation-validation-801/candidate/kc-dev-flow-2/scripts/number_guards.py check --repo /tmp/adr-reservation-validation-801/live.git --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 --task /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/adr-reservation-crosses-workflows.md --base ba055b8a7a55a787ac989c4cef52d07dd75661ad --head 6a0a4aec60bb5900a0d363bae912acc5714f5974
```

On disk it read only the assigned workflow's own state checkout: `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state` (74 sibling flat/folder paths). It also read remote branch snapshots `origin/spacedock-state/dev`, `dev-recovery-4b20a918`, `dev-recovery-9826ffcf`, `dev2`, `dev2-poc`, `ship`, and `ship-flow`. Full ref names, exact SHAs and the 435 remote paths are in `live-read-set.json`. It did not read any other on-disk state checkout. In particular, an unpublished/no-origin journey-map state checkout is not covered by this live pass.

## Review-finding disposition and limits

No Material, Needs decision or Polish findings. The accepted limits below are Deferred risk, not newly introduced repair scope:

- F1 Deferred risk — reservation/push race. User/workflow: two FOs reserving before either push. Harm: same early number, then renumbering at check. Boundary: `value-ac[AC-2]` promises refusal of a published holder, while Design explicitly excludes an atomic lock. Trigger evidence: `limits.json` observes two 0061 reserves followed by R8 after another task publishes 0061. Becomes Material if check accepts a visible other holder or if atomicity is newly promised.
- F2 Deferred risk — invisible state. User/workflow: a workflow that has not fulfilled the approved state-publication obligation. Harm: other workflows cannot see its lines. Boundary: `contract[docs/adr/0002-applied-migrations-are-frozen-and-numbers-are-reserved.md#consequences]` requires a unique branch in `spacedock-state/*`; unsupported unpublished/out-of-namespace state is excluded. Trigger evidence: `limits.json` confirms own-only 0062 is invisible elsewhere and a custom namespace is not fetched; AC-6 warning is present. Becomes Material if a correctly published in-namespace reservation is missed.
- F3 Deferred risk — stale refs after fetch failure. User/workflow: reserve/check while the remote cannot be fetched. Harm: a newly pushed holder may be unseen. Boundary: `value-ac[AC-6]` requires a warning and permits local-ref fallback. Trigger evidence: warning mutations fail, cached holders refuse; initial sandbox failure showed the diagnostic and approved network rerun passed. Becomes Material if a blind read is silent or cached visible holders are ignored.

One-number-per-kind enforcement remains outside this task: `limits.json` confirms an existing two-line task still gets both numbers, matching the base contract's limitation. Supplemental release integration and full-suite optional historical/native inputs remain skipped as recorded in `tests.json`; local model-free dispatch tests do not prove native model/worker execution, human gate behavior, delivery-hook body or remote merge. Actual candidate GitHub CI now passed, superseding the implementation report's earlier unverified-CI limit. RoboRev remains FO-owned; its PR-body claim was read, not independently rerun. CI configuration is unchanged and per-PR cost was not measured.

## Documents and comments

`doc-impact-disposition.json` verifies every one of the eight listed affected documents, with independent byte comparison and a checked reason for unaffected status. Their protected facts are unchanged: ADR 0020 arithmetic, ADR 0037 +144 step/Team rule, ADR 0049 effort/table bindings, ADR 0052 historical counts, journey link, README maintenance entry, maintain-flow budget/review contract and retained learning. The changed ADR 0002 and workflow template are separately reviewed above. Only one added code comment points to governing ADR 0002; it neither narrates the change nor cites provenance or line numbers. `comment-ratio.log`: 1 comment / 207 code lines, 0.5%, maximum 5%, exit 0. Dispatch records, design surfaces and diff whitespace checks pass.

## Captain acceptance: five steps

Run exactly, in a fresh shell:

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/adr-reservation-crosses-workflows/validation/acceptance.sh
```

The script is self-contained except the named assigned repository, its sibling `replay.sh`, Python/Git and the dispatched 0.35.0 install. It creates disposable files/repos only under /tmp and never writes repository config. Step 1 exports the exact SHA. Step 2 asserts the four visible replay outcomes: 0061, held 0060 refused, free 0061 passes, folder holder skipped. Step 3 expects 37 tests OK. Step 4 expects workflow 5933/5933 and PASS. Step 5 runs the required installed ADR command with read-only Git metadata, expects 61 checked / 0 legacy and exit 0. The validator ran this exact file with `bash --noprofile --norc`; complete observed output is `acceptance.log`, ending `5/5 ADR lint PASS; acceptance PASS` (exit 0). No UI is changed. This script does not establish atomic allocation, visibility of unpublished state, a future network fetch, publication, adoption, merge or cleanup.

## Reproduction setup for additional evidence scripts

The command arrays for all checks and exits are in `checks.json`. To rerun `probes.py`, `context-checks.py` or `limits.py`, first export the exact head and base with `git -C <assigned-worktree> archive <SHA> | tar -x -C <new empty directory>` into the two /tmp directories declared at the top; their paths are explicit. `run-checks.py` also declares the install, state and Git metadata it reads. No credentials, secrets, live provider data or unpublished branch contents are embedded.
