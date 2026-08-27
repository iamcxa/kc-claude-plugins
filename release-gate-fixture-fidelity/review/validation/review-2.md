# Validation review: release-gate fixture fidelity

## Decision

Approve exact candidate `0e9d613dc417f0467662cfd03a15a91d00d3508e` for PR #295 update and delivery review.

## Evidence

- The rebased candidate is exactly one file and seven additions over `31207d6`; the conflicting loader-test hunk was dropped because `main` already owns the absolute artifact path.
- The complete kc-dev-flow gate, focused loader test, Python compilation, diff-check, and pinned Spacedock 0.27.0-pre8 ablation pass.
- Baseline passes and all ten named mutants reject for expected evidence. `release-state-restored` reaches and matches `would strand` rather than either prior fixture error.
- Exact without-it restores the `main` fixture script and fails at published-tag candidate smoke because `candidate.json` is absent, proving the seven-line committed-Git setup is necessary.

## Bounds

- Product tree is clean and 0 behind `origin/main`.
- PR #295 still points to stale head `d339ba2`; approval authorizes rebuilding it at `0e9d613`, not merge or release.
- RoboRev remains the carried non-authoritative `UNKNOWN(state_unknown)` residual; its spent request was not retried.
