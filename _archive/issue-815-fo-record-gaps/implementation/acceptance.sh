#!/usr/bin/env bash
set -euo pipefail
TASK_WT=$1
TASK_PACKAGE=$2
TASK_WORKFLOW=$3
TASK_OUT=$4
mkdir -p "$TASK_OUT"
test "$(git -C "$TASK_WT" rev-parse HEAD)" = e608489c62fd387aeafaa5a1a6111ae59cd7d383
cd "$TASK_WT/kc-dev-flow-2/scripts"
python3 -B -m unittest test_decision_ledger.OpenAttemptReasonTests test_design_surfaces.BuiltScreenTests test_dispatch_records.CoverageTests test_delivery_gate.TaskFolderCaptainTests test_delivery_gate.ReviewerDeclarationTests.test_captain_record_path_holds_question_and_check > "$TASK_OUT/acceptance-tests.log" 2>&1
cd "$TASK_WT"
python3 -B kc-dev-flow-2/scripts/lint-skills.py > "$TASK_OUT/lint.log" 2>&1
python3 -B "$TASK_PACKAGE/scripts/adr_lint.py" docs/adr --since 6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1 --require 0073 > "$TASK_OUT/adr.log" 2>&1
python3 -B "$TASK_PACKAGE/scripts/comment_ratio.py" 6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1 HEAD --workflow-dir "$TASK_WORKFLOW" > "$TASK_OUT/comments.log" 2>&1
git -C "$TASK_WT" diff --check 6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1 HEAD
