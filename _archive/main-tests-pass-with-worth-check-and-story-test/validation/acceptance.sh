#!/bin/bash
set -euo pipefail

# 1. Verify the declared checkout, current main and installed tools.
REPO='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-main-tests-pass-with-worth-check-and-story-test'
HEAD='9b9be172c7cb2453ae74a79f10322344bf9ab32f'
BASE='571a7bd8a24ce08fac149fbcc91c4561610834c7'
PACKAGE='/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1'
PYTHON="$(command -v python3)"
SD='/Users/kent/.local/bin/spacedock'
test "$(git -C "$REPO" rev-parse HEAD)" = "$HEAD"
git -C "$REPO" fetch origin main
test "$(git -C "$REPO" rev-parse origin/main)" = "$BASE"
"$SD" --version | /usr/bin/grep '^spacedock 0.27.2$'
echo 'Step 1 PASS: exact candidate, current main and Spacedock 0.27.2.'

# 2. Export immutable commits into a disposable directory.
CHECK_DIR="$(mktemp -d /tmp/pr846-captain.XXXXXX)"
trap 'rm -rf -- "$CHECK_DIR"; echo "Removed: $CHECK_DIR"' EXIT
mkdir "$CHECK_DIR/candidate" "$CHECK_DIR/base" "$CHECK_DIR/temp"
git -C "$REPO" archive "$HEAD" | tar -xf - -C "$CHECK_DIR/candidate"
git -C "$REPO" archive "$BASE" | tar -xf - -C "$CHECK_DIR/base"
export TMPDIR="$CHECK_DIR/temp" PYTHONDONTWRITEBYTECODE=1
echo 'Step 2 PASS: candidate and base exported; source checkout unchanged.'

# 3. Run the unchanged Story tests and whole suite with both PATH variants.
for CHECK_PATH in /usr/bin:/bin /Users/kent/.local/bin:/usr/bin:/bin; do
  env -u SPACEDOCK_BIN PATH="$CHECK_PATH" "$PYTHON" -B "$CHECK_DIR/candidate/kc-dev-flow-2/scripts/test_design_surfaces.py" JourneyStoryTests
  env -u SPACEDOCK_BIN PATH="$CHECK_PATH" "$PYTHON" -B "$CHECK_DIR/candidate/kc-dev-flow-2/scripts/test_design_surfaces.py"
done
echo 'Step 3 PASS: 2 Story tests and 226 suite tests, 4 existing optional skips, in each mode.'

# 4. Exercise real native-stage refusal and check the decision records.
SPACEDOCK_BIN="$SD" "$PYTHON" -B "$CHECK_DIR/candidate/kc-dev-flow-2/scripts/test_dispatch_stage.py" DispatchStageTests.test_worth_requirement_uses_native_stage_for_yaml_status_values DispatchStageTests.test_unreadable_native_stage_does_not_make_design_presentable
(cd "$REPO" && "$PYTHON" -B "$PACKAGE/scripts/adr_lint.py" docs/adr --since "$BASE" --require 0048 0076 0077)
echo 'Step 4 PASS: 2 native tests; 70 decision records checked.'

# 5. Prove the original failure on the unmodified base.
for CHECK_PATH in /usr/bin:/bin /Users/kent/.local/bin:/usr/bin:/bin; do
  set +e
  env -u SPACEDOCK_BIN PATH="$CHECK_PATH" "$PYTHON" -B "$CHECK_DIR/base/kc-dev-flow-2/scripts/test_design_surfaces.py" JourneyStoryTests.test_design_compares_story_record_to_counted_field_only_in_map_workflows > "$CHECK_DIR/base.log" 2>&1
  RESULT=$?
  set -e
  test "$RESULT" -eq 1
  /usr/bin/grep 'FAILED (failures=1)' "$CHECK_DIR/base.log"
done
echo 'Step 5 PASS: original failure reproduced in both modes.'
echo 'ACCEPTANCE PASS'

