# Captain acceptance — exact candidate cdb99da0

Run the four numbered steps in `acceptance.sh` together, unchanged, in a fresh Bash shell:

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/denied-command-denies-only-that-command/validation/acceptance.sh
```

Prerequisites: this machine's named repository, synced task state, Python 3, Git, tar, Bash, installed kc-dev-flow-2 0.38.1 at the script's explicit Codex path, `/tmp/denial-replay-b21-fo/native-turns.json`, and the six native session logs it names. Raw session logs stay local and are deliberately absent from state; another machine cannot reproduce step 2 from the public state branch alone. The script creates only a temporary export, bare metadata clone, evidence copies and logs. It starts no worker, executes no command from a session log, changes no installed package and creates no linked worktree.

1. Export the pinned candidate and prepare isolated metadata. Expected: only `kc-dev-flow-2/extensions/paseo/EXTENSION.md` differs from the pinned merge base, then `STEP 1 PASS`.
2. Re-extract and re-score native evidence under the original rule. Expected: `STEP 2 PASS: 6 valid; 4 exact receipts/actions in the original turn; 2 controls; no retry.`
3. Corrupt disposable evidence for each retained criterion. Expected: unchanged evidence succeeds; new turn, changed reason, queued send without receipt, wrong audit bytes and post-denial retry are rejected; `STEP 3 PASS`.
4. Run candidate package lint and installed ADR lint. Expected: lint PASS, workflow 5939/5939 words, 67 ADR files and zero legacy, then `STEP 4 PASS` and `ACCEPTANCE PASS`.

Observed: the exact command above exited 0 under `bash --noprofile --norc`; full output is `checks/captain-acceptance.log`. Its disposable evidence directory is `/tmp/denial-acceptance.HvI9Vb`. The dispatch's separately named Claude-package ADR lint also exited 0 (`checks/dispatch-adr-lint.log`); the two installed ADR scripts have identical bytes.

This change has no user-visible screen. This acceptance re-scores existing recorded behavior and checks the textual candidate; it is not a new runtime replay, does not reproduce the original qnow build-flag incident, and does not test real Claude denial handling, future models or timing conditions. Evidence mutations establish rejection by the scorer, not that a new model run would fail in the same way. Publication, hosted CI, merge, release and adoption are outside this script.
