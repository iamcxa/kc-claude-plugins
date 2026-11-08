#!/usr/bin/env bash
set -euo pipefail
# Prerequisites: Python 3, Git, this repository's assigned checkout, its state
# checkout and installed kc-dev-flow-2 0.35.0, at the absolute paths below.
# No graphical screen changes. This checks deterministic behavior only; it does
# not validate a native observer's prose, hosted CI, RoboRev, or merge authority.
WT=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-observer-lists-unasked-merges
STATE=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state
PACKAGE=/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0
HEAD_SHA=b36fbeeec3a6699c0a82a021dc4ee0142410f6c8
BASE_SHA=139feeaee7ce037a0c6535568cd6bd103155cbae
PROOF="$STATE/observer-lists-unasked-merges/implementation"
RUN=$(mktemp -d /tmp/observer-captain-acceptance.XXXXXX)
mkdir -p "$RUN/candidate"

# Step 1: Export the exact candidate. Expected: its four changed paths.
test "$(git -C "$WT" rev-parse "$HEAD_SHA")" = "$HEAD_SHA"
git -C "$WT" archive "$HEAD_SHA" | tar -x -C "$RUN/candidate"
git -C "$WT" diff --name-only "$BASE_SHA" "$HEAD_SHA"

# Step 2: Replay the saved historical window. Expected: every AC-1 set, #727
# carried, and #727 with a changed head reported as a mismatch.
python3 -B "$PROOF/snapshot.py" "$RUN/candidate" "$STATE" "$RUN/snapshot"

# Step 3: Execute all 17 tests and five reverse mutations in empty temp dirs.
# Expected: baseline passes and all five mutations are rejected.
python3 -B "$PROOF/mutate.py" "$RUN/candidate" "$STATE" "$RUN/mutations"

# Step 4: Recount the pinned 54-window simulation. Expected: median 60, max 320.
python3 -B "$PROOF/recount.py" "$RUN/candidate/kc-dev-flow-2/scripts/merge_audit.py" "$STATE" "$RUN/words"

# Step 5: Run package lint and ADR lint on exported bytes, using read-only Git
# metadata. Expected: both exit 0; ADR lint checks 62 records with no legacy.
cd "$RUN/candidate"
python3 -B kc-dev-flow-2/scripts/lint-skills.py > "$RUN/lint.log" 2>&1
env GIT_DIR="$(git -C "$WT" rev-parse --absolute-git-dir)" GIT_WORK_TREE="$RUN/candidate" python3 -B "$PACKAGE/scripts/adr_lint.py" docs/adr --since "$BASE_SHA"
printf 'PASS: deterministic checks only; native observer report remains separately judged. Artifacts: %s\n' "$RUN"
