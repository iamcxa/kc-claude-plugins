#!/usr/bin/env bash
# Verify the exact candidate through observable command-line behavior; no UI changed.
set -euo pipefail

# Step 1: Export the pinned candidate without creating a worktree. Expect the head below.
REPO=${1:-/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-delivery-check-resolves-links-from-the-task}
HEAD=97dceebedd68108ef8e67fa5455f1e578c910ad6
HERE=$(cd "$(dirname "$0")" && pwd)
RUN_DIR=$(mktemp -d /tmp/delivery-links-acceptance.XXXXXX)
mkdir -p "$RUN_DIR/candidate" "$RUN_DIR/evidence"
git -C "$REPO" archive "$HEAD" | tar -x -C "$RUN_DIR/candidate"
export PYTHONDONTWRITEBYTECODE=1
printf 'Step 1 PASS: exported %s\n' "$HEAD"

# Step 2: Run the actual question and steps entrances. Expect seven tests and OK.
cd "$RUN_DIR/candidate/kc-dev-flow-2/scripts"
python3 -B -m unittest test_delivery_gate.TaskFolderCaptainTests test_delivery_gate.CaptainStepsTests.test_relative_markdown_card_is_read_by_the_real_cli
printf 'Step 2 PASS: seven entrance tests\n'

# Step 3: Reintroduce six errors in disposable copies. Expect six passed falsifiers.
python3 -B "$HERE/mutations.py" "$RUN_DIR/candidate" "$RUN_DIR/evidence"
printf 'Step 3 PASS: six assertion-killed mutations\n'

# Step 4: Check the workflow word budget. Expect lint exit zero and 5939 / 5939.
cd "$RUN_DIR/candidate"
python3 -B kc-dev-flow-2/scripts/lint-skills.py
printf 'Step 4 PASS: workflow lint\n'
printf 'Evidence: %s\n' "$RUN_DIR"
