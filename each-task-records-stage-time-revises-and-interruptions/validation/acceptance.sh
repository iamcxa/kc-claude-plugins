#!/bin/bash
# Four steps; Git, Python 3 and this public state checkout are required. No UI changes.
set -euo pipefail
STAGE_TIME_REPO='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-each-task-records-stage-time-revises-and-interruptions'
STAGE_TIME_STATE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state'
STAGE_TIME_EVIDENCE="$STAGE_TIME_STATE/each-task-records-stage-time-revises-and-interruptions/validation"
STAGE_TIME_HEAD=a3266ec91c7d46d36864c471c0cc26b389130b3c

# Step 1: Export the exact candidate; expect an isolated directory, without changing the worktree.
STAGE_TIME_SCRATCH=$(mktemp -d /tmp/stage-time-acceptance.XXXXXX)
trap 'rm -rf "$STAGE_TIME_SCRATCH"; echo "removed $STAGE_TIME_SCRATCH"' EXIT
mkdir "$STAGE_TIME_SCRATCH/code" "$STAGE_TIME_SCRATCH/tmp"
git -C "$STAGE_TIME_REPO" archive "$STAGE_TIME_HEAD" | tar -x -C "$STAGE_TIME_SCRATCH/code"
export TMPDIR="$STAGE_TIME_SCRATCH/tmp"
export PYTHONDONTWRITEBYTECODE=1
cd "$STAGE_TIME_SCRATCH/code"

# Step 2: Existing helper suite; expect 11 tests, OK.
python3 -B kc-dev-flow-2/scripts/test_task_timeline.py

# Step 3: Three archived public tasks; expect archived_tasks=3, stage_rows=9, all_matched=true.
python3 -B "$STAGE_TIME_EVIDENCE/compare_archived.py" "$STAGE_TIME_SCRATCH/code" "$STAGE_TIME_STATE"

# Step 4: Two complete validation cycles; the correct before/wait/after split is 20/20/40.
# This rejected candidate prints 50/20/10 and exits 1. That is the observed failure, not a passing acceptance.
python3 -B "$STAGE_TIME_EVIDENCE/probe_repeated_stage.py" "$STAGE_TIME_SCRATCH/code"
