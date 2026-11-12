# Reproduce this local evidence

Use the exact candidate and base in provenance.json. This trial used Python 3.11.14, Git, the dispatch-selected /Users/kent/.local/bin/spacedock (0.27.2), and the loaded Spacedock 0.28.0 source root. Those host-specific inputs are explicit; the local runner does not install them or reproduce hosted CI. run_suite.py records that selected launcher in its child environment.

All recorded criterion and mutation commands are in commands.json, mutation-results.json and suite-results.json. The first suite wrapper omitted the existing python3 -B timeline line; its standalone successful run is included in the final 29-entry list, with a complete/unique mapping to the workflow. The wrapper regex is corrected for a future full run.

Preserve committed evidence. For a fresh mutation run, use a new empty scratch path and a fresh output directory TASK/implementation/NEW_RUN; this task layout is required by run_mutations.py's lookup of TASK/evidence/run_probe.py. Use the same three private adopter state roots as external command inputs; raw private outputs must remain in memory and only count summaries are retained. The criterion runner may be invoked separately without adopter inputs to replay the public synthetic fixture.

The original scratch paths were removed after evidence commit. The implementation and probe worktrees, and /tmp/impl-design-surfaces-task-dir-crash-pr.md, are intentionally retained for the First Officer.
