# Captain acceptance

Candidate: c429ab1815a5fc5507056ee54f8005be024e1e69 (PR #854).
The surface is a command-line workflow; there is no changed screen.

Prerequisites: this public state checkout and its recorded candidate Git object; Python 3, Git, tar, bash; /Users/kent/.local/bin/spacedock 0.27.2; a writable temporary directory whose resolved package path is outside /tmp. The script uses macOS TMPDIR here and falls back to the invocation directory if TMPDIR is under /tmp. It creates an archive export, not a registered Git worktree. It does not use the product worktree or any earlier validator scratch.

Run this one command unchanged in a fresh bash shell:

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/dispatch-close-out-archives-evidence-and-removes-scratch/evidence/validation-3/acceptance.sh
```

- Step 1: export the exact candidate. Expected: Spacedock 0.27.2 and "Step 1 PASS".
- Step 2: build a native second dispatch, retry it, run the close command through collision refusal/retry, restore committed gzip and preserve the other dispatch. Expected: all probe booleans true, own worktree count 0, peer count 1, Scratch line count 1, "Step 2 PASS".
- Step 3: run the removed-scratch report check. Expected: report exit 0 and missing Captain-message path exit 1, nine tests OK, "Step 3 PASS".
- Step 4: run four regressions covering owned cleanup, role retry, later-write recovery and detached-state observer/cleanup merge behavior. Expected: four tests OK, "Step 4 PASS".
- Step 5: delete the export and fixture directory. Expected: "Step 5 PASS: temporary export removed"; command exit 0.

Observed unchanged run: captain-run.log, exit 0. These five steps took under five minutes.
Limits: synthetic native fixtures, not a model following the instructions or a real post-release adopter; no mechanical public-evidence classification; no real product worktree removal, gate approval, merge or release. The full package suite and falsifiers are separate validation evidence.
