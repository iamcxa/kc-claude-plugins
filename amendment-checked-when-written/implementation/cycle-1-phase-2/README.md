# Cycle 1, phase 2: authorized F1 repair

`candidate.txt` and `artifact.json` pin the one local repair commit. `boundaries.json` limits this repair to `laws_check.py` and its three regression tests; the marker/parser helpers, documentation, workflow, version and CI files did not change in this phase. The complete task branch still changes only its four approved files.

`tests.json` records one result per package test file; `tests-summary.json` supplies counts and the local Spacedock version. `run-tests.py` checks that the set of all package test files equals the test-file commands in the repository's CI workflow. It runs each file using `python3 -B`, with bytecode absent and writes full logs. The CLI fixtures use local Spacedock 0.27.2 and the declared plugin root 0.27.3, while CI pins both to 0.27.2; this is local evidence, not hosted CI proof. Optional fixture skips are in each log.

The completed run's 27 test-file commands each exited 0. Its driver then failed an overbroad post-run bytecode-absence assertion because child processes generated seven caches. `all-tests.log` retains that assertion; `finalize-tests.log` records the driver's `--finalize` path checking the existing 27 receipts against the unchanged candidate and test-file digests, removing those caches and producing the summary. This did not rerun the green tests. The retained driver now performs that cleanup at normal exit; the three reverted-fix probes and existing mutation controls separately asserted absent caches in their temporary packages.

`reverted-fix.json` records three expected assertion failures, one per new regression, after replacing only the temporary runner with the exact prior candidate's runner. The product checkout is not reverted. `mutations.json` and the named mutation logs repeat the existing nine rejection controls; the two historical bite probes separately remove reuse or marker detection. `red-before-fix.log` also records the three tests failing before the repair was applied. No bytecode is copied into the mutation packages.

`corpus-inputs.json` pins the same three historical ranges used by the earlier implementation, with the new candidate. `corpus-reconciliation.json` separates L4's seven events from L3's existing cannot-judge history debt. `corpus-comparison.json` compares the event headlines and every L4 diagnostic with the previous candidate at those same ranges. It does not establish current remote tips or hosted activation.

`checks.json`, the named check logs, `doc-impact.log` and `doc-verdicts.json` record the package checks and every affected-document disposition. No ADR was added: this repairs the existing accepted once-per-event contract. `artifact.json` binds the unchanged ADR read at the candidate by digest. `disk-full-attempt/` preserves the interrupted first suite; its ENOSPC errors are environmental failures superseded by the completed rerun. No product push, PR write, RoboRev, release or adoption pin change was performed.

To reproduce without overwriting the durable records, copy this directory to scratch and use the exact candidate checkout as `<worktree>`. The recorded installed package root, workflow/task paths, local Spacedock root and three state-history inputs are required local dependencies declared by the dispatch and these scripts; substitute an equivalent available checkout explicitly on another machine. `Repo` and the mutation drivers create temporary fixture repositories; the candidate checkout's final clean status is recorded separately.

```sh
python3 -B run-tests.py <worktree>
python3 -B reverted-fix.py <worktree>
python3 -B mutations.py <worktree>
python3 -B run-corpus.py <worktree> corpus-inputs.json dev2
python3 -B run-corpus.py <worktree> corpus-inputs.json qnow
python3 -B run-corpus.py <worktree> corpus-inputs.json relay
python3 -B verify-corpus.py
python3 -B compare-corpus.py <prior-amendment-2-evidence-directory>
python3 -B checks.py <worktree>
```

The suite and required checks must exit 0. The reverted-fix and mutation drivers exit 0 only after observing their expected failing assertions. Each full corpus CLI exits 2 on pre-existing L3 ambiguity; the reconciliation must still show exactly 3/3/1 L4 events at the seven named commits, with unchanged diagnostics. AC-7 remains deferred until a containing release, the Captain's pin approval and an observed hosted state-push run.
