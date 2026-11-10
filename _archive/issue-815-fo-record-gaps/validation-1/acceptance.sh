#!/usr/bin/env bash
set -euo pipefail
# Requires this declared checkout, Python 3, Git, tar, and kc-dev-flow-2 0.37.0.
# No browser surface changes. This checks the four record rules and lint only;
# it does not publish, merge, prove human reading, or post the issue reply.
TASK_REPO=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-issue-815-fo-record-gaps
TASK_PACKAGE=/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.37.0
TASK_FLOW=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2
TASK_HEAD=e608489c62fd387aeafaa5a1a6111ae59cd7d383
TASK_BASE=6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1
TASK_EXPORT=$(mktemp -d /tmp/issue815-acceptance.XXXXXX)

# Step 1: Export the exact candidate; expect the pinned SHA.
test "$(git -C "$TASK_REPO" rev-parse "$TASK_HEAD^{commit}")" = "$TASK_HEAD"
git -C "$TASK_REPO" archive "$TASK_HEAD" > "$TASK_EXPORT.tar"
tar -xf "$TASK_EXPORT.tar" -C "$TASK_EXPORT"
export GIT_DIR=$(git -C "$TASK_REPO" rev-parse --absolute-git-dir)
export GIT_WORK_TREE="$TASK_EXPORT"
export PYTHONDONTWRITEBYTECODE=1
printf 'Step 1 PASS: exported %s\n' "$TASK_HEAD"

# Step 2: Exercise valid and refused record forms; expect 32 tests, OK.
cd "$TASK_EXPORT/kc-dev-flow-2/scripts"
python3 -B -m unittest test_decision_ledger.OpenAttemptReasonTests test_design_surfaces.BuiltScreenTests test_dispatch_records.CoverageTests test_delivery_gate.TaskFolderCaptainTests test_delivery_gate.ReviewerDeclarationTests.test_captain_record_path_holds_question_and_check
printf 'Step 2 PASS: four record boundaries\n'

# Step 3: Check package instructions and word budget; expect 5933/5933, PASS.
cd "$TASK_EXPORT"
python3 -B kc-dev-flow-2/scripts/lint-skills.py
printf 'Step 3 PASS: package lint\n'

# Step 4: Check changed ADRs and required ADR 0073; expect 66 ADRs, 0 legacy.
python3 -B "$TASK_PACKAGE/scripts/adr_lint.py" docs/adr --since "$TASK_BASE" --require 0073 --root "$TASK_EXPORT"
printf 'Step 4 PASS: decision record\n'

# Step 5: Check comments and whitespace; expect 0.4%% <= 5.0%% and no diff errors.
python3 -B "$TASK_PACKAGE/scripts/comment_ratio.py" "$TASK_BASE" "$TASK_HEAD" --workflow-dir "$TASK_FLOW"
git -C "$TASK_EXPORT" diff --check "$TASK_BASE" "$TASK_HEAD"
printf 'Step 5 PASS: comment and whitespace checks\n'
