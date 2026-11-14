# Independent validation evidence

Candidate 5e9afd496a6901cc788252a77d84f355acbf0015; base c2f035b6612f5edb42220576b3414e993531ffd6. See ../../validation/report.md for REJECTED verdict and F1. Public metadata and synthetic fixtures only; no copied archived task/report/reviewer bodies. Logs normalize local paths. SHA256SUMS is produced by scratch close.

Run ../../validation/acceptance.sh exactly as the report states. It is self-contained for the declared local checkout and creates/removes an archive export; its green behavioral result does not clear the missing contract instruction.

For detailed evidence reproduction, copy these .py helpers into a new task-owned scratch root. Set PRODUCT_WORKTREE to a fresh git-archive export of the candidate, SOURCE_REPO to the assigned git worktree, STATE_ROOT to the task's state checkout, SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock (observed 0.27.2), PROBE_RUN=repair-final-, TMPDIR to a directory under scratch, and PYTHONDONTWRITEBYTECODE=1. Run python3 -B with round2_probe.py replay, round2_probe.py rounds, goal_and_mutation.py, candidate_mutations.py, shared_guards.py, mutations.py, contract_mutations.py, then late_head.py. Run round2_probe.py live only with read-only GitHub access; no external writes occur. The replays use public archived inputs at provenance.json's state commit. Do not copy generated repository/task bodies into evidence.

The original implementation helpers were reused rather than designing a new general harness. Adaptations: candidate source is an export; STATE_ROOT/SOURCE_REPO are explicit because an archive has no Git parents; the prior mutation locator now names question rather than the removed facts_question. late_head.py is the smallest required later-step counterexample. The blind-reader directory came from a fresh context given only the contract. Its 22 questions have individual dispositions.

Initial network denial and the number-guard wrong-cwd retry are disclosed in the report; only numbers-exact-head.log supplies fresh exact-candidate number proof. All earlier outputs remain as observations, not silently promoted to candidate evidence.
