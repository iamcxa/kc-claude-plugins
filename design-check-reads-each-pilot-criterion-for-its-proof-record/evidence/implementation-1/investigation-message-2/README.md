# Investigation message 2

report.md contains the findings and authority assessment. Candidate 9dd03d805 is unchanged. Each synthetic CLI case, exact command, exit and output path is in repro.json. Corpus comparison output contains counts only.

To rebuild the tested probes in dispatch scratch, copy this evidence folder's scripts and patches there, export the full public candidate tree as reference/ using git archive 9dd03d805, and run python3 -B build_probes.py. Target directories must not already exist. The archived patches were rebuilt from a fresh export and their checker/test bytes matched the tested sources (rebuild-check.json). Then run reproduce.py, run_candidate_regression.py and the commands in commands.json. The last runner is expected to fail on the unchanged candidate in eight subcases.

For compare.py, populate corpora/<label>/ with tracked flat and _archive/*.md state files from read-only state snapshots. Private source mapping, revisions, files and per-file results are deliberately not archived; obtain the authorized source mapping from FO and reproduce from those state checkouts. The fresh sample has 246/155/100 files, matching the earlier 501-file counts; byte identity to the deleted private sample is not claimed.

The SD integration harness needs the full exported repository docs/ as well as kc-dev-flow-2/, Spacedock CLI 0.27.2 and the active Spacedock plugin root 0.28.0. Unit checks use Python 3.15.0. No model was dispatched by these harnesses.

The +4/-0 span prototype is insufficient. The +5/-1 raw reader violates fenced-record exclusion. The +21/-1 proof-reader proposal preserves that exclusion; its complete regression/fixture proposal totals +38/-2 and remains unapplied pending separate FO repair authorization.
