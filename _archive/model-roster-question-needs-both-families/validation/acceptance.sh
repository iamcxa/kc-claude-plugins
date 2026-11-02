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

