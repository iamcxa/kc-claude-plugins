# Authorized repair of review 1864

Candidate: `d2d5bec640f0a61d3e044877b8443cdfdc03faa7`; parent: `0c68231ca9147a9833846b47a36e2fc27846cf66`.
Only `kc-dev-flow-2/scripts/state_guard.py` and `kc-dev-flow-2/scripts/test_state_guard.py` change in the repair commit.

The old guard returns no scanned bytes when Git emits no text hunks, and ignores identifiers in paths. The repair scans the full changed blob when there are no hunks, matches raw path bytes, retains same-blob rename entries and skips content scanning when object ids are equal. Existing `safe_name()` handles diagnostics. No live hook is installed and all classes still default to warn.

`red-source.json` pins the old guard and newly injected test bytes. `red.json` and `red.log` show both new regression methods fail on that old guard (14 subcases, zero harness errors). `green.json` and `green.log` show all 13 guard tests pass with no skip. The four mutation logs independently remove the no-hunk fallback, path matching, same-blob rename routing and unchanged-content protection; each makes its named real-hook test fail. All mutation copies omit caches and use `python3 -B`.

The no-hunk cases cover an explicit 64-byte Git size threshold, global `* -diff`, old NUL/new UTF-8 and old UTF-16/new UTF-8. The normal default large-file threshold was not measured. Path cases cover a new folder, basename and R100 rename, with clean content and matched-text-free refusal output. Additional tests preserve archive renames of old text/gzip/binary blobs, warn mode and deletion behavior.

`acceptance/results.json` and `acceptance/commands.json` retain the fresh AC-3/AC-5 real commit and push replay, accepted clean pushes, scan of remote paths and blob history, fresh-clone missing-hook detection, mode changes, shared hooks and product-worktree isolation. Push refusal fixtures create their unpushed commits before installing the guard; no bypass flag is used. All lists and remotes are synthetic and local.

To rerun the green guard suite at the exact candidate from its checkout:

```sh
python3 -B -m unittest discover -s kc-dev-flow-2/scripts -p test_state_guard.py
```

To rerun the red check, export `kc-dev-flow-2` from the parent commit with `git archive` into a fresh dispatch-owned scratch directory, replace only its `scripts/test_state_guard.py` with the candidate's test file, and run these two methods from its scripts directory:

```sh
python3 -B -m unittest test_state_guard.StateGuardTests.test_no_hunk_changed_text_refuses_commit_and_push test_state_guard.StateGuardTests.test_path_identifiers_refuse_new_and_renamed_files
```

That red command must exit 1 with 14 failures, not import/setup errors. The retained `red-source.json` supplies both hashes for verification.

From this evidence folder, rerun the mutation and acceptance scripts with the candidate code checkout and fresh dispatch-owned output folders as explicit arguments:

```sh
python3 -B mutations.py <candidate-code-checkout> <dispatch-scratch>/mutations
python3 -B acceptance.py <candidate-code-checkout> <dispatch-scratch>/acceptance
```

Required repository checks ran at this candidate: repository `lint-skills.py`; ADR lint since `c2f035b6612f5edb42220576b3414e993531ffd6` requiring 0087; fresh number guard; comment ratio 1.1% below 5%; all exit 0. Logs and per-document impact verdicts are retained here. Original writer/digest evidence remains at the prior candidate; it was not rerun as part of this two-file repair. RoboRev and hosted CI remain with FO. CI cost per PR was not measured; CI configuration is unchanged.
