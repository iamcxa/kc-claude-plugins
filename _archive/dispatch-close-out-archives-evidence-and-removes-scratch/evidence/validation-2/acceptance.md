# Captain acceptance: PR 854

Candidate: `d4fe39e54dc7069b099d61c4b0e3fa2e5aecd8c6`.
There is no changed screen. This checks observable dispatch and cleanup commands.
Requirements: Git, Python 3 with its standard library, the explicitly supplied
Spacedock binary, the candidate Git object, and this committed evidence folder.
The native binary tested was Spacedock 0.27.2; Python was 3.15.0.

Run this exact command in a fresh shell (the scratch argument must not exist):

```bash
bash --noprofile --norc '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/dispatch-close-out-archives-evidence-and-removes-scratch/evidence/validation-2/acceptance.sh' '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-dispatch-close-out-archives-evidence-and-removes-scratch' /Users/kent/.local/bin/spacedock '/tmp/close-854-captain-verified' '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/dispatch-close-out-archives-evidence-and-removes-scratch/evidence/validation-2/captain-verified'
```

The five steps are in `acceptance.sh`, with exact commands:

1. Export the pinned candidate. Expected: `Pinned candidate exported`.
2. Run the existing decisive checks using the declared fixture adapter. Expected:
   `Decisive checks: passed`; `captain-verified/checks/acceptance.json` has 20 passing results.
3. Build a native dispatch, close one of two synthetic roots, and restore committed
   gzip. Expected: `Private-evidence instruction, own-root close, peer survival, committed restore: passed`.
4. Run AC-1's exact grep. Expected: `1`, exit 0, then `Acceptance: PASSED`.
5. Remove only the export this script created. Expected:
   `Acceptance scratch export removed`; the scratch argument is absent.

Observed output is `captain-verified.log`. Tests, native artifact, close output,
manifest, gzip and facts are under `captain-verified/`.

The adapter changes only three fixture `Package root` input strings to the
declared installed package path; it leaves candidate product bytes and all
assertions unchanged. `fixture_adapter.py` additionally supplies normal Python
module import metadata for Python 3.15; `reused/fixture_adapter.py` is the original.
The initial metadata failure is retained in `captain-run-initial.log`; the earlier
four-step passing run is retained in `captain-final/`.

This does not prove arbitrary workers obey privacy prose, hosted CI/review,
release, or the design's post-release real-adopter stop condition. It uses only
public synthetic input, never private repository evidence. The OUTPUT argument
is outside RUN, so the evidence survives its cleanup.
