#!/usr/bin/env bash
set -euo pipefail

# Step 1: Export the exact candidate; expect the printed SHA and export path.
repo=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-special-role-dispatch-records-built-by-script
candidate=3567082b0ec1eeb59346b2d82887a07bc5ffc2fb
validation_root=$(mktemp -d /tmp/pr827-acceptance.XXXXXX)
git -C "$repo" archive "$candidate" | tar -x -C "$validation_root"
cd "$validation_root"
export SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock
export PYTHONDONTWRITEBYTECODE=1
printf 'Candidate: %s\nExport: %s\n' "$candidate" "$validation_root"

# Step 2: Check committed output and commit-failure recovery; expect 2 tests, OK.
python3 -B kc-dev-flow-2/scripts/test_dispatch_stage.py \
  DispatchStageTests.test_role_commits_complete_record_before_printing_exact_inputs \
  DispatchStageTests.test_role_commit_failure_withholds_prompt_and_retry_reuses_committed_record

# Step 3: Check malformed notes, owed role, model floor and flags; expect 4 tests, OK.
python3 -B kc-dev-flow-2/scripts/test_dispatch_stage.py \
  DispatchStageTests.test_role_rejects_incomplete_scope_notes_without_prompt_or_record \
  DispatchStageTests.test_role_skips_build_and_pending_hold_while_a_chief_engineer_call_is_owed \
  DispatchStageTests.test_role_checks_the_opus_model_floor \
  DispatchStageTests.test_role_rejects_stage_only_flags_and_unknown_roles

# Step 4: Check raw CRLF/LF bytes and legacy LF compatibility; expect 5 tests, OK.
python3 -B kc-dev-flow-2/scripts/test_dispatch_stage.py \
  DispatchStageTests.test_role_crlf_inputs_keep_raw_bytes \
  DispatchStageTests.test_stage_crlf_inputs_keep_raw_bytes \
  DispatchStageTests.test_role_lf_inputs_keep_raw_bytes \
  DispatchStageTests.test_stage_lf_inputs_keep_raw_bytes \
  DispatchStageTests.test_lf_record_matches_legacy_input_reading
printf 'PASS: committed role prompt, refusals, recovery and CRLF/LF input bytes\n'
