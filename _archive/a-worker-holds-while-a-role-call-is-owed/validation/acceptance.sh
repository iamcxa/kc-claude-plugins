#!/usr/bin/env bash
# Five local acceptance steps for PR 823. No user-visible screen changes.
# Requires git, tar, python3, the named source checkout, adopted package and Spacedock binary.
# Does not run Codex, prove state-report commits, or grant merge/adoption authority.
set -euo pipefail
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR
WT=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-a-worker-holds-while-a-role-call-is-owed
ADOPTED=/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.36.0
HEAD_SHA=42455f093facfc96edf6cd0357f26be1c858b262
BASE_SHA=f980a097bf15d8d1382c039949c6b9aefc5439c8
export PYTHONDONTWRITEBYTECODE=1
export SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock

# 1. Export the pinned candidate. Expected: STEP 1 PASS and the exact full SHA.
test "$(git -C "$WT" rev-parse HEAD)" = "$HEAD_SHA"
test -z "$(git -C "$WT" status --porcelain)"
OUT=$(mktemp -d /tmp/pr823-acceptance.XXXXXX)
mkdir -p "$OUT/candidate"
git -C "$WT" archive -o "$OUT/candidate.tar" "$HEAD_SHA"
tar -xf "$OUT/candidate.tar" -C "$OUT/candidate"
printf 'STEP 1 PASS: %s; export=%s\n' "$HEAD_SHA" "$OUT/candidate"

# 2. Check committed calls and the pending third record. Expected: 3 tests, OK.
cd "$OUT/candidate/kc-dev-flow-2/scripts"
python3 -B -m unittest \
  test_role_triggers.SymptomRoundsTest.test_worker_start_holds_the_three_recorded_states_until_both_calls_are_committed \
  test_role_triggers.SymptomRoundsTest.test_pending_third_record_holds_and_the_committed_worker_read_agrees \
  test_role_triggers.SymptomRoundsTest.test_pending_replaces_one_record_and_does_not_read_the_task_from_disk
printf 'STEP 2 PASS: hold, release, pending and committed-only reads\n'

# 3. Exercise real dispatch refusal/release. Expected: 6 tests, OK, no skips.
python3 -B -m unittest \
  test_dispatch_stage.DispatchStageTests.test_implementation_refuses_an_owed_call_before_build_and_a_call_releases_it \
  test_dispatch_stage.DispatchStageTests.test_validation_refuses_an_owed_call_before_build_and_a_call_releases_it \
  test_dispatch_stage.DispatchStageTests.test_ideation_builds_even_when_a_call_is_owed \
  test_dispatch_stage.DispatchStageTests.test_the_third_dispatch_counts_before_it_is_committed \
  test_dispatch_stage.DispatchStageTests.test_an_unresolvable_committed_task_holds_on_exit_two \
  test_dispatch_stage.DispatchStageTests.test_a_missing_role_checker_refuses_before_build
printf 'STEP 3 PASS: dispatch stage, pending and exit-2 boundaries\n'

# 4. Check the skill route and unchanged startup budget. Expected: PASS; 5931 of 5931 words.
cd "$OUT/candidate"
python3 -B kc-dev-flow-2/scripts/lint-skills.py
git -C "$WT" diff --exit-code "$BASE_SHA" "$HEAD_SHA" -- \
  kc-dev-flow-2/references/sd/workflow.md kc-dev-flow-2/scripts/lint-skills.py kc-dev-flow-2/README.md
printf 'STEP 4 PASS: workflow, README and budget unchanged\n'

# 5. Check the amended and cited decision records. Expected: 64 ADR files checked, exit 0.
# Read-only git metadata supplies history to an otherwise git-free export.
GIT_DIR=$(git -C "$WT" rev-parse --absolute-git-dir) \
GIT_WORK_TREE="$OUT/candidate" GIT_OPTIONAL_LOCKS=0 \
  python3 -B "$ADOPTED/scripts/adr_lint.py" docs/adr --since "$BASE_SHA" --require 0026 0049 0070
printf 'STEP 5 PASS: ADR lint exit 0\n'
printf 'LOCAL ACCEPTANCE PASSED. Saved model-replay evidence is assessed separately in the validation report.\n'
