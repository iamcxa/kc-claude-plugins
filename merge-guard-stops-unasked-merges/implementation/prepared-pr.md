feat(kc-dev-flow-2): stop merges without a saved ask

A Release PR could be merged even when the saved task merge ask did not carry it. Add a user-registered pre-tool guard that reads each task's newest on-disk merge record across linked state worktrees, asks on Claude, and refuses on Codex when the PR/head is uncarried.

Ancillary Release, workflow-sync and learning PRs can be recorded after the Captain approves a question naming the PR and head. Add the record command, registration instructions, ADR 0063, and the approved reminder in the delivery check output. Operator registration follows release; this PR edits no user settings.

Validation on 2026-11-06 at 871c6b2f4ebccfc2c67df91d7d39ad038aa0710f: merge-guard unit suite 16 passed; delivery suite 156 passed and one existing skipped; skill lint, ADR lint, number guards and comment ratio passed (0.9%, maximum 5%). Fourteen native host cases cover Claude headless/interactive behavior, Codex with and without operator rules, and missing/unreadable/raising scripts. Six unit mutations were rejected; removing the failure wrapper ran the fake merge, and removing the record head check let historical PR #672 pass. Replay: 54 pass / 30 stop; with synthetic ancillary approvals: 74 pass / 10 stop, with #672 still stopped. Commands and raw evidence are in the task state's implementation/ folder.

CI cost per PR was not measured. Existing package-path triggers are unchanged; one unit-test command is added. RoboRev and hosted CI have not run; FO owns publication and these checks. Existing phone evidence is the Captain's recorded AC-10 observation, not a new device test.
