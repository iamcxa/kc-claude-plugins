# Candidate acceptance, four steps

No visual UI changed. Prerequisites: Python 3 standard library, Git, bash, the declared repository, Spacedock `/Users/kent/.local/bin/spacedock`, and installed package `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.39.1`. No credentials or private repository inputs are used. The candidate is pinned to `223dbb6d1b5e895a45d11537b9494aa08610c8f8`.

The adjacent `acceptance.sh` is the exact four-step script run under fresh bash. Run it unchanged (the last argument is a new output folder owned by this rerun):

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/dispatch-close-out-archives-evidence-and-removes-scratch/evidence/validation-1/acceptance.sh /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-dispatch-close-out-archives-evidence-and-removes-scratch /Users/kent/.local/bin/spacedock /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.39.1 /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/dispatch-close-out-archives-evidence-and-removes-scratch/evidence/validation-1/fo-acceptance
```

1. `git archive` exports the exact head into a newly created directory; an EXIT trap removes that exact directory. Expected: export succeeds, no worktree is added to the real repository.
2. `python3 -B fixture_adapter.py ... implementation-1/acceptance.py ...` executes the existing decisive checks. Expected: `Existing decisive checks: passed`, 19 passed rows in `checks/acceptance.json`. The adapter changes only three Package root fixture inputs from the /tmp export to the declared installed package; the candidate product files and test assertions remain unchanged. Raw unadapted evidence is retained separately and failed, so it is not claimed green.
3. `python3 -B close_restore.py ...` invokes the actual close CLI in its own synthetic repo. Expected: close exit 0, owned root absent, no registered worktree under that root, compressed committed evidence restores to its SHA-256, truncating it fails. `close-restore.json` also records the two discarded fixture files.
4. `python3 -B privacy_probe.py ...` checks the generated worker instruction against the Captain's all-private-repository exclusion. On this rejected head the expected observation is `private-repository instruction: MISSING; emitted rule excludes secrets and personal data only`, and overall exit **1**. No private evidence is opened. The EXIT trap still runs; `acceptance-removed.txt` names the removed export.

Observed: `captain-run.log`, `captain/checks/acceptance.json`, `captain/close-restore.json`, `captain/privacy.json`, `captain/acceptance-removed.txt`. This is a rejection reproducer, not a passing delivery claim. It does not cover post-release adoption, live model instruction-following, hosted CI, or the AC-3 wording decision. The latter is independently reproduced by `ac3_scope.py` and `ac3-scope.json`.
