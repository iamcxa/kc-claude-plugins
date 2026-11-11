# Captain acceptance: PR 849

This command checks exact candidate `78905b08d6f38817ccdda5d2e91be478fd75dfc7`. It has no screen; the observable surface is the command-line design check.

Prerequisites: the assigned code checkout, this committed validation folder, Python 3, `/Users/kent/.local/bin/spacedock`, the declared kc-dev-flow-2 0.39.0 package, and the two pinned local state histories. `replay.py` declares every source repository and revision, including the read-only qnow adopter. No credential, install, fetch, product mutation or network call is required.

Run the four steps exactly as written:

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/worth-questions-asked-only-before-the-design-gate/validation/acceptance.sh
```

1. Export candidate, 0.39.0 baseline and 0.38.1. Expected: `Step 1 PASS: exact head 78905b08d6f38817ccdda5d2e91be478fd75dfc7 exported`.
2. Execute the seven Worth tests with the real Spacedock reader, then the three intentionally broken copies. Expected: `Ran 7 tests`, `OK` without skips, and `Step 2 PASS: 7 tests, no skips; all 3 mutations detected`.
3. Export and check all 173 pinned tasks from the two state repositories. Expected: all three Bite tasks match 0.38.1 (exits 1/0/0); `Step 3 PASS: 10 releases, 17 ideation refusals, no other differences`.
4. Run `adr_lint.py docs/adr --since 44f11855264bde64da284ffa9c1fef70e8ac38dd --require 77`, then scope/title controls. Expected: `70 ADR file(s) checked, 0 legacy`, `Step 4 PASS: 70 ADRs; approved scope and title`, `Acceptance PASS`, and one `Removed scratch:` line.

The exact commands are in `acceptance.sh`; `acceptance.log` is the validator's fresh-Bash output, with its exit recorded in `acceptance-result.json`. The script replaces this task's `replay.json` and `mutations.json` with new observations and deletes its own temporary export.

Limits: this is not the full suite on a merge result, a complete Observer run, hosted CI, a live re-fetch of the PR title, or release/adopter rollout. `pr.json` is the captured GitHub response for the exact head. FO owns the full merge-result suite with the real Spacedock binary before the merge ask.

