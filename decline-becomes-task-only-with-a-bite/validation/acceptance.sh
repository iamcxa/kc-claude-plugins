#!/usr/bin/env bash
# Four local acceptance steps. Requires the named repo/state, Python 3.11+, Git, bash,
# Spacedock CLI 0.27.2 on PATH, and the named kc-dev-flow-2 / Spacedock plugin installs.
# No user-visible screen changed. This reruns local behavior and checks retained
# model reports; it does not launch a model, publish, merge, or adopt the workflow.
set -euo pipefail
repo='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-decline-becomes-task-only-with-a-bite'
state='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state'
package='/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0'
sd='/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3'
evidence='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/decline-becomes-task-only-with-a-bite/validation'
head='ae7750375bc19e482f829edc9a041d95fb280693'
base='ba055b8a7a55a787ac989c4cef52d07dd75661ad'

# 1. Export the exact candidate. Expected: STEP 1 PASS with the dispatched full SHA.
candidate="$(mktemp -d /tmp/pr800-captain.XXXXXX)"
git -C "$repo" archive "$head" | tar -x -C "$candidate"
test "$(git -C "$repo" rev-parse HEAD)" = "$head"
echo "STEP 1 PASS: exported $head"

# 2. Exercise the rule, pins, three archived declines, mutations,
#    ADR lint and number/design guards. Expected: 10 deterministic groups passed.
cd "$candidate"
python3 -B "$evidence/acceptance.py" "$candidate" "$state" "$package" "$sd" --skip-native
echo "STEP 2 PASS: deterministic behavior and negative controls"

# 3. Check the path workaround and the required literal ADR command.
#    Expected: workaround PASS; 62 ADR file(s) checked, 0 legacy; exit 0.
python3 -B "$evidence/workaround.py" "$candidate" "$package"
env GIT_DIR='/Users/kent/Project/kc-claude-workspace/kc-claude-plugins/.git/worktrees/spacedock-ensign-decline-becomes-task-only-with-a-bite' GIT_WORK_TREE="$candidate" GIT_OPTIONAL_LOCKS=0 \
  python3 -B "$package/scripts/adr_lint.py" docs/adr --since "$base"
echo "STEP 3 PASS: ADR record and unchanged supersession assertion"

# 4. Verify the recorded fresh Sonnet model runs and actual observer contrast.
#    Expected: AC-7 PASS, retained variability LIMIT, AC-5 PASS; exit 0.
python3 -B "$evidence/verify-recordings.py"
echo "STEP 4 PASS: recorded model evidence; no new model run"
