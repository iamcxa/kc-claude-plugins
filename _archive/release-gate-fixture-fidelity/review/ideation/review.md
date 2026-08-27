# Ideation review

- Entity: `release-gate-fixture-fidelity`
- Bound incident: Release Please PR #258 at `43dfeea0bd3bc9904384350b7075e39ef82efa00`, failed run `32929119727`.
- Proposed slice: change only `scripts/kc-dev-flow-minimal-stack-ablation.test.py` and `kc-dev-flow/scripts/profile-contract-loader.test.py`.
- Repair: initialize the copied repository fixture with a committed `HEAD`, and pass the committed review artifact by absolute path.
- Proof already reproduced: with only those two fixture changes on Spacedock `0.27.0-pre8`, the baseline passed and all ten mutants were rejected; `release-state-restored` reached the intended `would strand` guard.
- Stop numbers: at most 2 files, 25 gross changed lines, and 20 Git-fixture setup lines. Any runtime, CI workflow, dependency pin, release metadata, or third-file change returns to the Captain.
- Delivery: one Draft PR to `main`; Release Please PR #258 rerun, merge, and release remain Captain-owned.
