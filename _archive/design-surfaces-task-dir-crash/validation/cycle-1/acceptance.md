# Captain acceptance

No screen changes. This five-step check exercises the command entrance and the actual PR-watch seed subprocess. It requires Bash, Git, Python 3.11+ and the existing repository containing the two recorded commits. It creates and removes its own export; no earlier `/tmp` artifact is needed.

Run this exact command in a fresh shell:

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/design-surfaces-task-dir-crash/validation/cycle-1/acceptance.sh /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-design-surfaces-task-dir-crash
```

The script's five steps and observations:

1. Export candidate `ef9aaffcbc48d6f17dd2e1dd744c4ffb5862d0f8`; its full SHA prints.
2. Run the five real-CLI entrance tests and invalid-encoding test; `Ran 6 tests`, `OK`, `2. entrance tests PASS`.
3. Run the actual seed subprocess through PR-watch for valid, invalid fields, invalid encoding, missing and removed-after-read inputs; all five JSON records say `passed`, and the last records exit 2 with one error line; `3. exit-code consumer PASS`.
4. Lint the candidate's architecture decision records against `8125e6d516d32abbf79c6772de10cde2c20900a8`; `73 ADR file(s) checked, 0 legacy`, `4. ADR lint PASS`.
5. Compare checker bytes to the pinned commit; `5. unchanged candidate PASS; acceptance PASS`. The command exits 0 and its automatic cleanup removes the export.

Validator execution: exact command above, fresh `bash --noprofile --norc`, exit 0; observed output in `acceptance.log`. The validator supplied only TMPDIR to place the disposable export inside its owned cleanup root; the script does not require that variable.

Limits: this quick script does not replay private adopter files, the full package suite, mutation checks, hosted CI, model behavior, merging, publication or released adoption. Those claims remain separate evidence and authority. It is not a delivery approval.
