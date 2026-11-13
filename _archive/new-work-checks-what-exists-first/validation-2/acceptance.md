# Captain acceptance, validation cycle 2

No visible UI changed. Requires the clean assigned code worktree at candidate `1fc2f05f88b18a62d4eda598158ffa385df9fae8`, the saved task evidence, Python 3, Git, ripgrep, the named package installation and network/Git-metadata access for reservation refresh.

Run exactly in a fresh Bash shell:

    bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/new-work-checks-what-exists-first/validation/acceptance.sh

The retained script has four steps:
1. Verify the pinned revision and clean code tree, then export tracked bytes. Expected: `STEP 1 PASS`.
2. Check candidate routing and scope and reject the old base. Expected: candidate exit 0, base exit 1, `STEP 2 PASS`.
3. Run repository lint and parse the accepted task design. Expected: `STEP 3 PASS`.
4. Check decision record 0083 and current number reservations, then recheck the unchanged code tree. Expected: `STEP 4 PASS`, final `ACCEPTANCE PASS`, exit 0, no stale-fetch warning.

Observed exact execution: `acceptance-authorized.log`, exit 0. The initial sandbox execution `acceptance.log` reached step 4 but returned exit 1 because state-ref freshness could not be established. No candidate change intervened. `commands.json` preserves both runs.

The script creates its own temporary export with `mktemp` and removes the resolved directory through its EXIT trap. Those generated pathnames were not printed by the existing script. The script has no dependency on this cycle's later-removed cold fixture.

This script checks source/loading and local guards. It does not rerun the cold model subject, private census, complete suite, hosted checks, merge, release or adoption. The independently observed cold replay is separate saved evidence in this directory.

