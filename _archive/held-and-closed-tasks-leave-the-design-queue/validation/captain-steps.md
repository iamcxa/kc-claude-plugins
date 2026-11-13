# Captain acceptance: PR 856, exact candidate
Requires the declared local product/state checkouts, Python 3 with pytest/PyYAML, Git, and /Users/kent/.local/bin/spacedock 0.27.2. There is no web UI in this task.

Run the four steps in the committed script unchanged in a fresh Bash shell:

```sh
/bin/bash --noprofile --norc '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/held-and-closed-tasks-leave-the-design-queue/validation/captain-acceptance.sh'
```

1. Export candidate 455846c6d30d4ab650c1c4503bc591722231586d; expected EXPORT with that SHA and the exact temporary path.
2. Load pinned public-state inputs; expected NATIVE INPUTS 14 held tasks and one-task subset.
3. Run the held tests; expected 11 passed, 144 deselected.
4. Recount output using native Spacedock query; expected CURRENT held=14 words=32 maximum=48 result=PASS, then ONE held=1 words=17 maximum=9 result=FAIL. Overall exit 1 is the reproduced design-bound conflict.

Observed in captain-acceptance.log, in under one minute. The validator supplied CAPTAIN_SCRATCH under its owned export root; the default creates and prints a new root. After retaining the output, delete only that printed root. This script creates no worktree, remote, published change or live task edit. It checks listing/word counts and held unit cases; it does not cover full GitHub integration, post-delivery Held edits, upstream status display, or delivery approval.
