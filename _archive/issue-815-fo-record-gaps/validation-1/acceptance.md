# Captain acceptance: PR 826

Candidate: `e608489c62fd387aeafaa5a1a6111ae59cd7d383`; base: `6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1`.

Run all five steps unchanged in a fresh shell:

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/issue-815-fo-record-gaps/validation-1/acceptance.sh
```

The script declares the existing checkout and installed kc-dev-flow-2 0.37.0 package it needs. It exports the pinned commit to a new `/tmp/issue815-acceptance.*` directory; Git metadata is read only. Requires Python 3, Git and tar. No credentials or browser step.

1. Export and identify the candidate. Expected: `Step 1 PASS: exported e608489c62fd387aeafaa5a1a6111ae59cd7d383`.
2. Exercise the four record boundaries, including incorrect question, missing question, invalid second screenshot, coverage folder and misplaced Captain steps. Expected: `Ran 32 tests`, `OK`, `Step 2 PASS`.
3. Check package instructions and the approved word budget. Expected: `5933 of 5933 words`, package `PASS`, `Step 3 PASS`.
4. Check all changed architecture decision records and require ADR 0073. Expected: `66 ADR file(s) checked, 0 legacy`, `Step 4 PASS`.
5. Check added comments and whitespace. Expected: `code lines 248, comment lines 1, 0.4%`, maximum `5%` met, no whitespace errors, `Step 5 PASS`.

Validator observed exactly these outcomes, exit 0; see `acceptance.log`. The same script also ran from the final state path; see `acceptance-final-path.log`.

No screen changes are in scope. This short script does not repeat the archived corpus replay or complete suite, prove that a human saw the bound question or reviewed every screenshot, publish/merge/release the candidate, or send the issue reply. Those obligations remain distinct in the stage report.
