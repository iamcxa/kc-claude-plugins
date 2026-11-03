#!/bin/bash
set -euo pipefail
# Step 1: check out the exact candidate, detached. Expected: exact HEAD and integrated main.
WT='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-second-round-prompts-a-step-back'
STATE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state'
PACKAGE='/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0'
HEAD_SHA='0d8cb2b13be65d6cd8917d343797e8fa515e155f'
BASE_SHA='84e3e492e512efad6e8b5b5b9764e4b13eb8a445'
CHECKOUT=$(mktemp -d "$WT/.context/second-round-acceptance.XXXXXX")
git -C "$WT" worktree add --detach "$CHECKOUT" "$HEAD_SHA"
trap 'cd "$WT"; git -C "$WT" worktree remove "$CHECKOUT"' EXIT
cd "$CHECKOUT"
test "$(git -C "$CHECKOUT" rev-parse HEAD)" = "$HEAD_SHA"
git -C "$CHECKOUT" merge-base --is-ancestor "$BASE_SHA" "$HEAD_SHA"
printf 'STEP 1 PASS: exact candidate and integrated main\n'

# Step 2: two failed validations. Expected: one advisory with all three questions, exit 0.
python3 -B kc-dev-flow-2/scripts/role_triggers.py "$STATE" paseo-codex-dispatch-practice --rev e0dc64f886cf80e7579551a4002a05b4c603f1c9
printf 'STEP 2 PASS: exit 0\n'

# Step 3: two replacing amendments. Expected: one advisory with all three questions, exit 0.
python3 -B kc-dev-flow-2/scripts/role_triggers.py "$STATE" peers-paseo-rule-matches-practice --rev ff2063c539a2fbf8c446797d7051fc34c406aff9
printf 'STEP 3 PASS: exit 0\n'

# Step 4: third replacing amendment. Expected: chief-engineer owed with three questions, exit 1.
if python3 -B kc-dev-flow-2/scripts/role_triggers.py "$STATE" peers-paseo-rule-matches-practice --rev 7d203d562789a107d651f3169b6a89b153024d33; then
  printf 'FAIL: third occurrence did not hold\n'
  exit 1
else
  test "$?" -eq 1
fi
printf 'STEP 4 PASS: exit 1 is the expected hold\n'

# Step 5: exercise thresholds, idle, and merge with the real role checker.
# Expected: all three commands report OK; 9, 1, and 2 tests respectively.
python3 -B kc-dev-flow-2/scripts/test_role_triggers.py StepBackTest
python3 -B kc-dev-flow-2/scripts/test_pr_watch.py TasksTests.test_second_failed_validation_is_advisory_live_and_silent_archived
python3 -B kc-dev-flow-2/scripts/test_delivery_gate.py OwedRoleCallTests.test_second_failure_prints_questions_before_ask_without_holding_and_with_other_problems OwedRoleCallTests.test_third_failure_holds_until_the_call_is_committed
printf 'STEP 5 PASS: thresholds and both consumers\n'

# Step 6: decision record and unchanged standing instructions. Expected: 49 records, no diff, clean tree.
python3 "$PACKAGE/scripts/adr_lint.py" docs/adr --since origin/main --require 0026
git -C "$CHECKOUT" diff --stat origin/main -- kc-dev-flow-2/references/sd/workflow.md kc-dev-flow-2/references/sd/mods/kc-dev-flow-2.md
git -C "$CHECKOUT" diff --exit-code origin/main -- kc-dev-flow-2/references/sd/workflow.md kc-dev-flow-2/references/sd/mods/kc-dev-flow-2.md
test -z "$(git -C "$CHECKOUT" status --porcelain)"
printf 'STEP 6 PASS: ADR, standing text, clean candidate\n'

