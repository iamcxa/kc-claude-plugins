# Merge-main implementation evidence

Candidate b8362fb901cd27bd367be1cd5b826f21fefad70e, merged main/base 8c8313823f353f631e2b7cca4559dd3e643f30a5; recorded 2026-11-09.

The original validation-1/acceptance.sh is unchanged and still pins its original candidate. acceptance.sh here is a copy changing only the candidate/base SHA pins. Both ran with bash --noprofile --norc and exited 0; only the copy demonstrates this merged head.

Full discovery ran from the assigned code worktree as:

```sh
env TMPDIR=/tmp SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s kc-dev-flow-2/scripts -p 'test_*.py'
```

The explicit local binary is Spacedock 0.27.2. Native model-free checks use the declared Spacedock plugin/mod root /Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3. The unchanged implementation-1/run_extra_checks.py and run_mutations.py take the code root and output directory as arguments. The latter clears bytecode caches before testing. combined_probe.py takes the same arguments and exercises matching-record merge questions with each of the five original inputs, plus the missing/matching/mismatched record transitions. These are local checks; RoboRev, hosted CI, publication and independent validation are FO-owned.
