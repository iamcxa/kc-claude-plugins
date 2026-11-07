# Implementation evidence

Candidate: f429f0fac40511c6480fd92e2cccd4c0e94b2454
Base: 139feeaee7ce037a0c6535568cd6bd103155cbae

`results/tests.json` records each executed command and exit status. `results/proof/proof.json` records the candidate, mutation and historical replay expectations. Logs preserve the original executed paths; the same scripts are retained here for reruns. Scratch exports were removed after each probe; `python3 -B` and cache clearing isolate mutation runs.

Run the retained acceptance script with the following six arguments: assigned product worktree, installed kc-dev-flow-2 package root, active Spacedock plugin root, workflow directory, task file, and an empty operator-owned output directory. Example from the task's assigned worktree:

```bash
bash --noprofile --norc <this-folder>/acceptance.sh <repo> <package> <sd-plugin-root> <workflow> <task-file> <output-directory>
```

The acceptance wrapper deliberately exits 1 while the required installed-package checker still reports the original false positive. Candidate checks and all five accepted criteria pass; this package-check discrepancy requires FO disposition and is not a clean required-check result. `results/receipt.json` proves the installed checker matches base bytes and records candidate identity.

No product branch push or PR creation was performed. PR title and body are retained in `pr.md` and the requested `/tmp/impl-adr-lint-tells-supersession-assertion-from-pointer-pr.md`. RoboRev and remote CI are FO-owned and were not run. CI cost per PR was not measured; no CI configuration changed.
