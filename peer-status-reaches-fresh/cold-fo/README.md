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

## Correction, 2026-10-31

The r1-7 row above overstated the sentence. Counting tool results that returned it, only r4 read it. Scored strictly (not assigned, FO keeps the check), source-down is 1/3 at best: r5 and r6 told the Captain to look at the PR himself, and r6 said it was waiting on him. FO put 2/3 to the Captain when asking for the 38 words; that number was wrong. Found by the amendment-1 engineering reviewer.

## Sentence in the dev entry skill, scratch copy of 153e3b0d9, runs s1-7

The same 38 words, in `skills/dev/SKILL.md` before "For existing work, preserve". Every run invoked that skill and the sentence came back in its result, 7/7.

| Case | Runs | Result |
|---|---|---|
| MERGED | s1, s2, s7 | 3/3 no merge ask, all queried the source |
| Source down | s3, s4, s5 | 3/3 marked unverified, not assigned, FO keeps the re-check |
| OPEN | s6 | action kept |

Limits: seven runs; a named PR; no long-session load; an FO resuming through spacedock:first-officer without the dev entry does not get this text. Baseline source-down was never run; 153e3b0d9 without any sentence gave 0/1.
