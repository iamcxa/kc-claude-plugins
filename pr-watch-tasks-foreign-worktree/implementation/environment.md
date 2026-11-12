# Local verification environment

Python 3.11.14, Git, Spacedock CLI 0.27.2 and pinned Spacedock plugin source at `4d158a484ec73e184861067f8ed1e20087fdc26a` (the CI pin). The source was exported with `git archive` from the existing read-only Spacedock clone into the assigned worktree; no runtime or dependency was installed. All product source was read from the assigned implementation worktree.

## Two runner corrections, no product change

The first full matrix used a TMPDIR under the assigned worktree. A plain extracted fixture then inherited its outer Git repository, while native SD also recognized `.worktrees` in its ancestor path and refused it as an entity location. The first run exited 1: 20 commands passed, eight failed. Failed commands (raw output retained in `first-suite-logs/`):

- `kc-dev-flow-2/scripts/test_design_surfaces.py`
- `kc-dev-flow-2/scripts/test_adr_doc_checks.py`
- `kc-dev-flow-2/scripts/test_dispatch_records.py`
- `kc-dev-flow-2/scripts/test_delivery_gate.py`
- `kc-dev-flow-2/scripts/test_pr_watch.py`
- `kc-dev-flow-2/scripts/test_laws_check.py`
- `kc-dev-flow-2/scripts/test_dispatch_stage.py`
- `kc-dev-flow-2/scripts/test_sd_dispatch.py`

`root-cause.json` records the same plain-directory Git query returning the outer root inside the worktree, and failing as intended outside Git. The previously failing ADR control passes outside Git (`root-cause-control.log`).

The second full matrix used an outside-Git TMPDIR, but the runner resolved `/tmp` to macOS `/private/tmp`. It exited 1: 27 passed, `test_replay_dispatch.py` alone failed because its expected package path retained `/private` while the other side explicitly stripped it. The unchanged full replay command passes all eight tests when TMPDIR retains the `/tmp` spelling (`replay-dispatch-rerun.log`). The runner now preserves that spelling with `absolute()`.

`final-suite-results.json` joins all 28 distinct CI test commands at the unchanged candidate, replacing only that named failed command with its passing rerun. The completeness check prevents omissions and double counting. This is not a single all-green matrix invocation; both unsuccessful matrices remain intact. The final result is 1412 unittest cases including 11 skips, plus two separate native CLI checks. The skip groups are declared external amendment/gate/obligation corpora, an optional real-builder setup and journey-map runtime dependencies; the changed watcher suite ran all 136 tests without skips.

## Reproduction

Use `run_full_suite.py <candidate-worktree> <pinned-spacedock-source> <spacedock-binary> <new-TMPDIR-outside-any-git-checkout>`. On macOS keep the literal `/tmp` spelling for the final argument rather than its `/private/tmp` realpath. The test runner reads its command list directly from the candidate CI workflow. It does not download the pinned CLI/source or install optional journey dependencies. The temporary source export and fixture roots are disposable and listed in `scratch-plan.json`; restore the pinned source from the public Spacedock commit before a later full replay.

The accepted narrow fresh-shell script is `accept.sh <candidate-worktree> <public-workflow> <spacedock-binary>`. It requires Python 3, Git and declared native Spacedock, forbids provider reads in the missing-worktree proof, and writes one output file per criterion. Mutation source is compiled directly from explicit text under `python3 -B` after clearing generated caches; child bytecode writes are disabled. Actual copies of the unchanged lifecycle documents are used for the two document mutations. No production file is changed by a mutation.
