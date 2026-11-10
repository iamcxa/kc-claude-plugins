# Reproducing the F3 investigation

`identity.json` binds the unchanged product candidate, source hashes, clean status and the two test results. `candidate-tests.json` has the expected failing F3 test; `proposal-tests.json` and `proposal-existing-l4.log` exercise an unapplied copy. `probes.json` contains actual CLI output and zero structural issues; `gate-comparison.json` records unchanged public check/seed outputs. Read `proposal.md` and the unapplied `proposed-input.diff` before deciding on a repair.

Copy this directory to scratch before reproducing so the durable evidence is not overwritten. Python 3, Git and the exact candidate checkout are required. `investigate.py` returns **1 intentionally** after confirming one candidate assertion failure, no errors, passing proposal controls and an unchanged product checkout:

```sh
python3 -B investigate.py <candidate-worktree>
```

The impact probe requires the three local state repositories/ranges and README paths declared in `corpus-inputs.json`. It reads Git objects in one batch per repository and compares pure predicates, then exercises only the seven named L4 first-parent ranges. It does not repeat a full-history CLI run or modify Git history. It should exit 0:

```sh
python3 -B impact.py <candidate-worktree> corpus-inputs.json
```

The current candidate must remain `d7502656c765e36ce3d24be8602862ccc2551254`, with a clean working tree. Temporary repositories/packages are removed by their context managers. The proposal is generated from the candidate source in `proposal.py`; it is not applied to the product. `source-boundary.json` names the two package callers and unchanged shared functions. `manifest.json` seals the evidence. State-report publication does not authorize a product commit, product push or PR write.
