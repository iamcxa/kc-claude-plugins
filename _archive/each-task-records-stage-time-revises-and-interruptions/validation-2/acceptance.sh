#!/bin/bash
# Four checks of the pinned candidate. Requires this checkout, Python 3 and git.
# No UI changed. Does not prove post-release timing or complete FO ask recording.
set -euo pipefail
WT=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-each-task-records-stage-time-revises-and-interruptions
STATE=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state
PKG=/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.39.1
EVIDENCE="$STATE/each-task-records-stage-time-revises-and-interruptions/validation-2"
HEAD_EXPECTED=188ba44f427a15bfff69d9d4e24b2446af0b69dc
BASE=8ce0eb6050c889b21baccf50fec35231bc888d66
SCRATCH=$(mktemp -d /tmp/stage-time-acceptance-2.XXXXXX)
trap 'rm -rf -- "$SCRATCH"; echo "removed $SCRATCH"' EXIT
export TMPDIR="$SCRATCH" PYTHONDONTWRITEBYTECODE=1

# 1. Export the exact reviewed bytes. Expected: the full candidate SHA below.
test "$(git -C "$WT" rev-parse HEAD)" = "$HEAD_EXPECTED"
mkdir "$SCRATCH/code"
git -C "$WT" archive "$HEAD_EXPECTED" | tar -x -C "$SCRATCH/code"
echo "STEP 1 PASS: $HEAD_EXPECTED"

# 2. Exercise the helper's git-backed fixture suite. Expected: 12 tests, OK.
cd "$SCRATCH/code"
python3 -B kc-dev-flow-2/scripts/test_task_timeline.py
echo 'STEP 2 PASS: helper suite'

# 3. Check repeated-stage time and the archived real case. Expected: 20/20/40; 30.3.
python3 -B "$EVIDENCE/probe_repeated_stage.py" "$SCRATCH/code"
python3 -B kc-dev-flow-2/scripts/task_timeline.py "$STATE" denied-command-denies-only-that-command --json > "$SCRATCH/real.json"
python3 - "$SCRATCH/real.json" <<'PY'
import json, sys
t = json.load(open(sys.argv[1]))
r = next(r for r in t['stages'] if r['stage'] == 'validation')
assert r['after_gate_min'] == 30.3, r
print('STEP 3 PASS: repeated split 20/20/40; real after-gate 30.3 minutes')
PY

# 4. Check the required decision record on the same head. Expected: exit 0.
cd "$WT"
python3 -B "$PKG/scripts/adr_lint.py" docs/adr --since "$BASE" --require 0080
test "$(git -C "$WT" rev-parse HEAD)" = "$HEAD_EXPECTED"
echo 'STEP 4 PASS: required ADR lint; acceptance passed'
