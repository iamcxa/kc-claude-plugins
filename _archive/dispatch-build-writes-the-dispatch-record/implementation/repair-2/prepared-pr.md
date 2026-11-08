feat(kc-dev-flow-2): record stage dispatches before building

Stage dispatch records previously depended on FO saving a separate copy before
building the worker artifact. Add `dispatch_stage.py` to write the record from
the build's checklist and scope notes, run both existing record checks, then
build through Spacedock. The pinned stamp commit includes the record; advance
dispatches commit it before returning their envelope. Immediate identical retries
reuse their record, while changed input or an intervening state commit creates a
new round. Failed checks/builds remove only a record this invocation created and which is still absent from HEAD, including its index entry; a record already committed is retained for retry.

Keep model/roster supplied by FO and leave the package-version/workflow-checkout
preflights separate. Record the accepted ruling in ADR 0070. Replace the three
approved workflow passages verbatim and lower the word budget from 5933 to 5931.

The additional `kc-dev-flow-2/skills/observer/SKILL.md` edit was authorized by FO
in implementation follow-up 1: its chat-only command entry must match the shortened
README command, as enforced by `lint-skills.py`. The uncorrected entry fails lint;
the updated entry passes. No other observer behavior changes.

Validation: real Spacedock 0.27.2 split-root seam tests, the lint mutation suite,
dispatch-record tests and real dispatch transport checks; thirteen counterexamples
exercise the accepted falsifiers. A fresh-shell acceptance runner exports the
exact candidate without bytecode caches and retains its logs under the task's
`implementation/fresh/` state evidence. Candidate ADR lint, number guards,
comment ratio and document dispositions are recorded there. The installed 0.35.0
ADR linter has the base's known pre-#806 false positive on a deliberate historical
ADR assertion; FO authorized using the candidate's corrected linter. That historical
assertion is unchanged.

The new CI step uses the workflow's existing package/workflow path triggers and
pinned real binary. CI cost per PR: not measured. Hosted CI and RoboRev are not
run by this worker; FO owns product publication and both reviews. No version bump.


The repair now checks Spacedock's complete task commit unit before selecting or
creating a record: the flat task file and companion directory, or the whole
folder-form task. HEAD, index and raw worktree bytes/modes must agree; conflicts,
hidden index flags, unsupported types/escapes and nonignored untracked task files
hold dispatch without builder/cleanup calls or state changes. Owners must
preserve and reconcile staged/worktree versions before an intentional commit;
blindly running state commit on divergent versions is unsafe.

Exclusive same-task write ownership must last through the check, build, commit
and cleanup. This single precondition is not a transaction lock and provides no
concurrent-writer safety guarantee. Other tasks may remain dirty. The pinned
Spacedock 0.27.2 builder has an inherited no-op retry limitation: if an unrelated
path is staged, its global cached-diff check may attempt an empty task-scoped
commit and fail. The repair preserves all versions in that case; ordinary
retries succeed, and dispatches that change this task leave unrelated staged,
unstaged and untracked work intact and outside their commit.

The whole-scope proof covers flat/folder layouts, fresh dispatch, reused record,
new round and advance, and snapshots HEAD, index entries/flags, file bytes/modes
and outside sentinels. Nine isolated mutations must fail their matching snapshot
preservation assertion. Evidence for this repair is implementation/repair-2 in
the shared task state. Hosted CI, independent review and publication remain FO-owned.
