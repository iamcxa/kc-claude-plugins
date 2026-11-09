# Local implementation evidence

Recorded on 2026-11-09 at candidate 6f2fe8f33de15cf4e9283bf9dfed185a5691ed57; base e7c9381f2ae7f11bc715a6f11a3e000b9b807e1e.

From the assigned code worktree, full discovery ran as:

```sh
env TMPDIR=/tmp SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s kc-dev-flow-2/scripts -p 'test_*.py'
```

The local Spacedock binary is 0.27.2; the explicit plugin/mod root used by run_extra_checks.py is 0.27.3. These are declared machine prerequisites, not hosted CI evidence. run_mutations.py accepts the code root and an output directory, clears package bytecode caches, and records actual baseline/mutant return codes and output in mutation-observations.json. baseline-regressions.log is the intentionally failing run against the unchanged base script with the new regression tests. Other logs are candidate checks; extra-checks.json records their commands/exits.
