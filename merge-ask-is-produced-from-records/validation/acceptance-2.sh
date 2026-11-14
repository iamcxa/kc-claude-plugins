#!/usr/bin/env bash
set -euo pipefail
# Step 1: Export the exact candidate; requires git, tar, Python 3, and the named local checkout.
TASK_SCRATCH=/tmp/dev2/kc-claude-plugins-3042bb224e995ded/merge-ask-is-produced-from-records/validation-2
mkdir -p "$TASK_SCRATCH"
ACCEPT_EXPORT=$(mktemp -d "$TASK_SCRATCH/acceptance.XXXXXX")
trap 'rm -rf "$ACCEPT_EXPORT"' EXIT
SOURCE_REPO=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-merge-ask-is-produced-from-records
CANDIDATE=a5657edd6531916cd01f659b888feaa021219ead
git -C "$SOURCE_REPO" archive "$CANDIDATE" | tar -x -C "$ACCEPT_EXPORT"
cd "$ACCEPT_EXPORT"
mkdir -p "$ACCEPT_EXPORT/.tmp"
export TMPDIR="$ACCEPT_EXPORT/.tmp" PYTHONDONTWRITEBYTECODE=1
printf 'Exported %s\n' "$CANDIDATE"
# Step 2: Contract, held-record, and six paired regression cases. Expected: 14 tests, OK.
python3 -B kc-dev-flow-2/scripts/test_delivery_gate.py ObservedFactsTests RecordRouteParityTests
# Step 3: The POC recipe consumes the same record contract. Expected: 9 tests, OK.
python3 -B kc-dev-flow-2/scripts/test_poc_readme.py
# Step 4: Repository lint and workflow budget. Expected: exit 0 and ACCEPTANCE PASSED.
python3 -B kc-dev-flow-2/scripts/lint-skills.py
printf 'ACCEPTANCE PASSED\n'
