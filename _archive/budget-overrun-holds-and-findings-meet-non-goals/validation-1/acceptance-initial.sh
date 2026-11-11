#!/usr/bin/env bash
set -euo pipefail
# Step 1: Export the exact candidate; no repository worktree is created or changed.
BUDGET_REPO=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-budget-overrun-holds-and-findings-meet-non-goals
BUDGET_HEAD=5bf7cf78866a2f0f6376c15b59fc400519c5ffeb
BUDGET_TMP=$(mktemp -d /tmp/budget-841-acceptance.XXXXXX)
git -C "$BUDGET_REPO" archive "$BUDGET_HEAD" | tar -x -C "$BUDGET_TMP"
export SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock
export PYTHONDONTWRITEBYTECODE=1
printf 'STEP 1: exported %s\n' "$BUDGET_HEAD"
# Step 2: Allow the cap; hold cap+1; count named repairs once; ignore invented amendments.
(
  cd "$BUDGET_TMP/kc-dev-flow-2/scripts"
  python3 -B -m unittest -v test_role_triggers.BudgetTest.test_total_dispatch_cap_counts_stages_and_named_followups_once test_role_triggers.BudgetTest.test_total_cap_counts_only_messages_with_a_named_header_symptom test_role_triggers.BudgetTest.test_amendment_needs_the_same_entry_verbatim_words
)
printf 'STEP 2: 3 budget boundary tests passed\n'
# Step 3: Exercise real dispatch: remove the held record, preserve results, resume only after an amendment.
(
  cd "$BUDGET_TMP/kc-dev-flow-2/scripts"
  python3 -B -m unittest -v test_dispatch_stage.DispatchStageTests.test_budget_hold_removes_record_and_skips_build_until_amended test_dispatch_stage.DispatchStageTests.test_total_cap_holds_before_build_and_keeps_existing_results
)
printf 'STEP 3: 2 real dispatch tests passed\n'
# Step 4: Reject missing Worth questions and check the 6008-word workflow with ADR 0077 present.
(
  cd "$BUDGET_TMP/kc-dev-flow-2/scripts"
  python3 -B -m unittest -v test_design_surfaces.WorthQuestionsTests.test_design_without_worth_questions_is_refused_even_with_fenced_example
)
(
  cd "$BUDGET_TMP"
  python3 -B kc-dev-flow-2/scripts/lint-skills.py
  python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1/scripts/adr_lint.py docs/adr --require 0077
)
printf 'STEP 4: missing-section rejection, workflow lint and ADR checks passed\n'
printf 'PASS: candidate %s; export retained at %s\n' "$BUDGET_HEAD" "$BUDGET_TMP"
