#!/usr/bin/env bash
set -euo pipefail

# Step 1: export exactly the reviewed bytes; expect the full candidate SHA.
WT='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-budget-overrun-holds-and-findings-meet-non-goals'
EVIDENCE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/budget-overrun-holds-and-findings-meet-non-goals/validation-2'
HEAD_SHA='6da9a765ee04e1e2c7836517ba01f75b0ea91d73'
CAPTAIN_TMP=$(mktemp -d "${TMPDIR:-/tmp}/pr841-captain.XXXXXX")
trap 'rm -rf -- "$CAPTAIN_TMP"' EXIT
mkdir "$CAPTAIN_TMP/candidate" "$CAPTAIN_TMP/rejected"
git -C "$WT" archive "$HEAD_SHA" | tar -x -C "$CAPTAIN_TMP/candidate"
git -C "$WT" archive 5bf7cf78866a2f0f6376c15b59fc400519c5ffeb | tar -x -C "$CAPTAIN_TMP/rejected"
export PYTHONDONTWRITEBYTECODE=1 SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock
printf 'Step 1: candidate %s\n' "$HEAD_SHA"

# Step 2: both bypasses now refuse; the real section passes; reader errors refuse.
printf 'Step 2: missing/commented headings = 1, visible control = 0\n'
python3 -B "$EVIDENCE/worth-probe.py" "$CAPTAIN_TMP/candidate" "$CAPTAIN_TMP/rejected" "$CAPTAIN_TMP/observations"

# Step 3: real dispatch holds, keeps results, and resumes after a covering amendment.
printf 'Step 3: real dispatch boundary; expect 3 tests OK\n'
cd "$CAPTAIN_TMP/candidate/kc-dev-flow-2/scripts"
python3 -B -m unittest -v \
  test_dispatch_stage.DispatchStageTests.test_budget_line_and_spent_cycles_are_printed_before_build \
  test_dispatch_stage.DispatchStageTests.test_budget_hold_removes_record_and_skips_build_until_amended \
  test_dispatch_stage.DispatchStageTests.test_total_cap_holds_before_build_and_keeps_existing_results

# Step 4: reject unapproved raises and count only named repair follow-ups.
printf 'Step 4: authority and message count; expect 3 tests OK\n'
python3 -B -m unittest -v \
  test_role_triggers.BudgetTest.test_amendment_needs_the_same_entry_verbatim_words \
  test_role_triggers.BudgetTest.test_total_cap_counts_only_messages_with_a_named_header_symptom \
  test_role_triggers.BudgetTest.test_old_first_stage_record_never_opts_in_with_later_headers

# Step 5: old records permit the merge ask; new over-budget records refuse it.
printf 'Step 5: old merge ask passes; new merge ask holds\n'
cp "$EVIDENCE/merge-transition-probe.py" "$CAPTAIN_TMP/merge-transition-probe.py"
python3 -B "$CAPTAIN_TMP/merge-transition-probe.py" "$CAPTAIN_TMP/candidate"
printf 'PASS: five acceptance steps completed; temporary export will be removed.\n'
