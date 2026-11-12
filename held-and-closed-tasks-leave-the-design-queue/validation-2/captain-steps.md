# Captain acceptance
Run from a fresh bash shell:
```sh
/bin/bash --noprofile --norc '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/held-and-closed-tasks-leave-the-design-queue/validation-2/captain-acceptance.sh'
```
The script has four steps: export exact candidate; export fourteen frozen public tasks; run eleven held tests; measure one/fourteen/125 tasks and reject one-word-over-bound counterexamples. Expected final output: PASS: exact candidate held behavior and amendment-4 counts. Expected exit: 0.
Requirements and fixed checkout paths are declared in the script. It needs Python 3 with PyYAML and pytest, Git, tar, wc, Spacedock and the named repository/state objects. No network or credentials are required.
The validator ran the same script with CAPTAIN_SCRATCH='/tmp/validate-held-closed-v2-20261112-193629/captain' and CAPTAIN_EVIDENCE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/held-and-closed-tasks-leave-the-design-queue/validation-2/captain' under /bin/bash --noprofile --norc; observed output is captain-acceptance.log. These overrides only place scratch and saved output; the assertions are unchanged.
This does not update live Held sections or prove upstream plain status, hosted CI, native worker launch, merge integration or delivery. The default interactive invocation removes only its own mktemp directory. The validator retained its explicit root until evidence commit, then removed that exact root.

