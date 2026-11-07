# PR 800 validation acceptance

Candidate: `ae7750375bc19e482f829edc9a041d95fb280693`.
Base: `ba055b8a7a55a787ac989c4cef52d07dd75661ad`.

No user-visible screen changed. Run the four numbered steps in `acceptance.sh` as one exact fresh-shell command:

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/decline-becomes-task-only-with-a-bite/validation/acceptance.sh
```

1. Export the pinned candidate under /tmp. Expected: STEP 1 PASS and the full candidate SHA.
2. Exercise local rule behavior, wording controls, native dispatch, archived declines and guards. Expected: 11 deterministic acceptance groups passed, then STEP 2 PASS.
3. Reproduce the ADR pointer workaround and run the required ADR lint. Expected: same-file/supersession PASS, 62 ADR files checked with 0 legacy, then STEP 3 PASS.
4. Check the retained independent Sonnet readings and observer contrast. Expected: AC-7 PASS, the recorded C-reading variability LIMIT, AC-5 PASS, then STEP 4 PASS.

Every command and expected observation is in the corresponding numbered section of the script. Requires the existing named code/state checkouts, Python 3.11 or newer, Git, bash, Spacedock CLI 0.27.2 on PATH, kc-dev-flow-2 0.35.0 and the Spacedock 0.27.3 plugin root listed there. It creates only temporary exports and validation evidence files. It does not need network or credentials.

A pass covers this exact local candidate and retained model evidence. It does not launch fresh models, assess all possible decline reasons, prove adoption after release, retire old tasks, or authorize review, merge or publication. Temporary exports are intentionally left under /tmp for inspection. Model and observer reports retain their original outputs.
