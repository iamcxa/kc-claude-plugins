# Reproduce phase-1 evidence

Use candidate `72216e2e947e962737a17c6e61ef3800f9d639c4` in the assigned product worktree. Copy this evidence directory to scratch before execution.

Run `python3 -B investigate.py <candidate-worktree> <scratch-directory>`: expected exit 1, ten tests, three assertion failures for partial repair/growth/mixed changes, seven controls passed, zero errors. `tests.json` and `scenarios.json` preserve named results and actual CLI output.

Run `python3 -B analyze.py <candidate-worktree> <scratch-directory> <scratch-directory>/corpus-inputs.json`: expected exit 0; seven unchanged named event payloads under the analysis-only per-id proposal. It writes `proposed-runtime.diff` and never applies it. The proposal function is extracted from the standalone investigation script, not installed into production.

`identity.json` binds the product head, clean status and source hashes; `proposal.md` states the scope and remaining authorization. All Git state mutations made by the tests are confined to temporary repositories; configured identities/global-config isolation are passed through the existing test fixture. No product commit, product push, review message or PR update was made.
