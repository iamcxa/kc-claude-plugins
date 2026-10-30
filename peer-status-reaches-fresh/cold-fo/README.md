# Cold FO runs, FO-run, 2026-10-30

Harness: `claude -p --setting-sources project --strict-mcp-config --add-dir <package> --plugin-dir <package> --model sonnet`, one disposable adopted workflow, a logged `gh` wrapper (real, OPEN fixture, or unreachable). Prompts name the PR, carry no peers hint, and have no long-session load, so they do not reproduce the 2026-10-28 conditions.

Excluded as harness defects: absent, absent2 (package not readable or scripts denied).

| Version | Runs | Read peers | MERGED: no merge ask | Source down: action not assigned | OPEN: action kept |
|---|---|---|---|---|---|
| origin/main | base1-3 | 0 | 2/3 | not run | not run |
| 153e3b0d9 | absent3, cand2, cand3, open, down, notice | 0 | 3/3 | 0/1 | 1/1 |
| Scratch: extra clause in the README peers row | t1-6 | 0 | 3/3 | 0/2 | 1/1 |
| Scratch: one sentence at the top of the workflow's Extensions section | r1-7 | 0 | 3/3 | 2/3 | 1/1 |

Sentence tested in r1-7 (38 words): Before naming a Captain action from a peer, check that action at its original source in the current reporting turn; if inaccessible, mark it unverified and keep the check with FO; do not assign it to the Captain.

The notice run read the source too, so it is counted under MERGED only as a control, not in the 3/3.
