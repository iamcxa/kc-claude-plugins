#!/bin/bash
set -euo pipefail

# Step 1: Name the installed tools and exact source; expect all assertions to pass.
TASK_SOURCE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-delivery-check-before-ask-is-provable'
TASK_STATE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state'
PACKAGE='/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.36.0'
SPACEDOCK='/Users/kent/.local/bin/spacedock'
HEAD_SHA='85f9a65928958f78a4eaf12b3ce38ca4e25e2ab0'
BASE_SHA='e7c9381f2ae7f11bc715a6f11a3e000b9b807e1e'
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ACCEPTANCE_DIR="$(mktemp -d /tmp/pr817-acceptance.XXXXXX)"
test "$(git -C "$TASK_SOURCE" rev-parse "$HEAD_SHA")" = "$HEAD_SHA"
test -x "$SPACEDOCK"
echo 'PASS step 1: pinned head and declared local dependencies'

# Step 2: Export both revisions without creating a git worktree.
mkdir -p "$ACCEPTANCE_DIR/candidate" "$ACCEPTANCE_DIR/base"
git -C "$TASK_SOURCE" archive "$HEAD_SHA" | tar -x -C "$ACCEPTANCE_DIR/candidate"
git -C "$TASK_SOURCE" archive "$BASE_SHA" | tar -x -C "$ACCEPTANCE_DIR/base"
echo 'PASS step 2: candidate and base exported'

# Step 3: Exercise the command holds and reference output; expect 8 tests, OK.
cd "$ACCEPTANCE_DIR/candidate"
python3 -B kc-dev-flow-2/scripts/test_delivery_gate.py DeliveryCheckBeforeQuestionTests
echo 'PASS step 3: eight delivery-before-question tests'

# Step 4: Exercise native binding, falsifiers, historical replay and independent counts.
python3 -B "$SCRIPT_DIR/verify-export.py" "$ACCEPTANCE_DIR/candidate" "$TASK_STATE" "$ACCEPTANCE_DIR/replay" "$SPACEDOCK" "$TASK_SOURCE"
python3 -B "$SCRIPT_DIR/independent-checks.py" "$ACCEPTANCE_DIR/candidate" "$ACCEPTANCE_DIR/base" "$ACCEPTANCE_DIR/independent" "$PACKAGE"
echo 'PASS step 4: native reference, historical replay and all AC falsifiers'

# Step 5: Check word budget and required decision record; expect exit 0.
python3 -B kc-dev-flow-2/scripts/lint-skills.py
TASK_GIT_DIR="$(git -C "$TASK_SOURCE" rev-parse --absolute-git-dir)"
GIT_DIR="$TASK_GIT_DIR" GIT_WORK_TREE="$ACCEPTANCE_DIR/candidate" python3 "$PACKAGE/scripts/adr_lint.py" docs/adr --since "$BASE_SHA" --require 0071
echo 'PASS step 5: workflow budget and ADR 0071'
echo "Evidence: $ACCEPTANCE_DIR"

