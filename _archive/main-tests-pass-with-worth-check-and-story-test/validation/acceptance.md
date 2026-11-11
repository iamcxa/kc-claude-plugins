# Captain acceptance

This change has no user-visible screen. The five steps in `acceptance.sh` exercise the real checker and existing tests without editing the product checkout. Prerequisites are the declared local checkout, Python 3, Git, the installed Spacedock 0.27.2 executable, and the Codex kc-dev-flow-2 package path written in the script. Its first step fetches main and refuses if the tested base or candidate changed; a later main requires a fresh merge-result validation, not updating the script's expected SHA without rerunning it.

Run this exact command in a fresh shell:

```bash
/bin/bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/main-tests-pass-with-worth-check-and-story-test/validation/acceptance.sh
```

Expected observations, in order:

1. Exact candidate/current main verified and `spacedock 0.27.2` printed.
2. Candidate/base exported into an owned temporary directory.
3. Both PATH modes run 2 Story tests and the full 226-test suite; both pass with 4 existing optional historical skips.
4. The 2 native-stage tests pass and ADR lint prints `70 ADR file(s) checked, 0 legacy`.
5. The original base test fails once in each mode, then `ACCEPTANCE PASS` and the removed temporary path are printed.

The validator ran this unchanged command; observed output is in `acceptance.log` (exit 0). The first sandbox attempt stopped at Git's FETCH_HEAD write; its original output is preserved in `acceptance-sandbox.log`, and the same command passed with authorized access. The script removes its own temporary directory on exit.

Limits: this compact acceptance does not run every workflow command, publish a PR, run RoboRev, approve a gate, merge, release, or establish installed-package rollout. Those are separately evidenced or retained as FO obligations in the task report. The full workflow runs use the pinned Spacedock source root and release executable in `spacedock-provenance.json`; the local platform is Darwin arm64, while the separately recorded hosted run is Ubuntu with the workflow's Linux artifact.
