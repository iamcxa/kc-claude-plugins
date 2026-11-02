# Captain acceptance: exact PR #765 candidate

Prerequisites: the existing repository named below contains both pinned commits; Python 3, Git, Bash and the declared installed kc-dev-flow-2 0.34.0 package are available. No network or worker launch is required. This is a CLI/workflow change with no graphical UI.

Run the following five steps together in a fresh Bash shell. They completed in under five minutes in this validation. Step 1 makes a detached checkout; step 5 removes it. If a step fails, stop and retain its checkout for diagnosis.

Expected observations:
1. Exact head `57321c0b4e9006c2a80c72b4afb1aa368e1ec2a2`; STEP 1 PASS.
2. Roster subprocess replay PASS and STEP 2 PASS; negative inputs are refused.
3. Empty assigned-base workflow diff; lint PASS; 49 ADR files checked, 0 legacy; STEP 3 PASS.
4. Version parity: all plugins consistent; STEP 4 PASS.
5. No tracked or untracked candidate changes; temporary checkout removed; STEP 5 PASS.

```bash
#!/usr/bin/env bash
set -euo pipefail
# Step 1: create an isolated checkout of the reviewed head.
ROSTER_SOURCE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-model-roster-question-needs-both-families'
ROSTER_HEAD=57321c0b4e9006c2a80c72b4afb1aa368e1ec2a2
ROSTER_BASE=562b1a87198d97bb2ae1d87b72884e390b20e146
ROSTER_PACKAGE='/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0'
ROSTER_CHECK=$(mktemp -d "$ROSTER_SOURCE/.context/roster-acceptance.XXXXXX")
git -C "$ROSTER_SOURCE" worktree add --detach "$ROSTER_CHECK" "$ROSTER_HEAD"
test "$(git -C "$ROSTER_CHECK" rev-parse HEAD)" = "$ROSTER_HEAD"
printf 'STEP 1 PASS: exact candidate %s\n' "$ROSTER_HEAD"

# Step 2: exercise question, committed resolution, effort mapping, and family cases.
python3 -B - "$ROSTER_CHECK" <<'PY'
import sys, tempfile, shutil
from pathlib import Path
root = Path(sys.argv[1])
sys.path.insert(0, str(root / "kc-dev-flow-2/scripts"))
import test_sd_dispatch as check
fixture = Path(tempfile.mkdtemp(prefix="roster-acceptance-fixtures-"))
try:
    check.exercise_model_roster(fixture / "roster")
finally:
    shutil.rmtree(fixture)
print("STEP 2 PASS: eight prerequisite combinations; three models and six efforts; wrong pairs refused; absent roster unchanged")
PY

# Step 3: check the task's stack diff, package lint, and reserved decision record.
git -C "$ROSTER_CHECK" diff --exit-code "$ROSTER_BASE" "$ROSTER_HEAD" -- kc-dev-flow-2/references/sd/workflow.md
(cd "$ROSTER_CHECK" && python3 -B kc-dev-flow-2/scripts/lint-skills.py)
(cd "$ROSTER_CHECK" && python3 "$ROSTER_PACKAGE/scripts/adr_lint.py" docs/adr --since "$ROSTER_BASE" --require 0050)
printf 'STEP 3 PASS: stack workflow unchanged; lint and ADR 0050 pass\n'

# Step 4: verify release metadata parity.
(cd "$ROSTER_CHECK" && bash scripts/version-parity-check.sh)
printf 'STEP 4 PASS: release metadata parity\n'

# Step 5: verify no tracked edits and remove this checkout.
test -z "$(git -C "$ROSTER_CHECK" status --porcelain)"
git -C "$ROSTER_SOURCE" worktree remove "$ROSTER_CHECK"
printf 'STEP 5 PASS: candidate unchanged; temporary checkout removed\n'
```

The exact script above is also saved as acceptance.sh. Validator invocation (only the destination log is outside the script):
```bash
env -i HOME=/Users/kent PATH=/Users/kent/.pyenv/versions/3.11.14/bin:/Users/kent/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin bash --noprofile --norc '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-model-roster-question-needs-both-families/.context/validation-57321c0b-evidence/acceptance.sh' > '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-model-roster-question-needs-both-families/.context/validation-57321c0b-evidence/acceptance-output.txt' 2>&1
```

Observed exit: 0. All five PASS markers are in acceptance-output.txt. This fixture does not prove real worker settings/completion, merge ancestry, the literal origin/main workflow diff, RoboRev, or released #762 adoption.

