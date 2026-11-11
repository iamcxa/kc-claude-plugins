#!/usr/bin/env bash
set -euo pipefail

# Prerequisites: this local repo and Relay clone contain the named commits;
# Node >=22.13, npm, Python 3, Git and Spacedock 0.27.2 are installed; npm has network access.
# Covers the archive report, Story rule, unchanged consumer, import regression and ADR.
# Does not prove a release, adopter rollout, real FO archive message or full hosted CI.

# 1. Export the stacked candidate. Expected: the exact 01d23393... commit line.
REPO=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-story-done-reports-release-remaining
PACKAGE=/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1
RELAY_SOURCE=/Users/kent/conductor/repos/subspace-relay
HEAD=01d23393ebe5bfd63d8bcafc01859c3b146021d2
RUN=$(mktemp -d /tmp/story-progress-captain-v2.XXXXXX)
git -C "$REPO" rev-parse "$HEAD"
git -C "$REPO" archive "$HEAD" | tar -x -C "$RUN"

# 2. Install the locked dependencies. Expected: npm ci exits 0 and dependencies ready.
(cd "$RUN/kc-journey-map" && npm ci > "$RUN/npm-ci.log" 2>&1)
printf '%s\n' 'dependencies ready'

# 3. Check report, refs, limits and schema. Expected: 4 tests pass, none fail.
node --test --test-name-pattern='filed membership|archive report|report separates|journey-progress registers' "$RUN/kc-journey-map/lib/progress.test.mjs" "$RUN/kc-journey-map/lib/schemas.test.mjs"

# 4. Check Story admission, idle reminder, unchanged consumer and repaired import.
# Expected: 2, 1, 122 and 1 tests OK, respectively.
python3 -B "$RUN/kc-dev-flow-2/scripts/test_design_surfaces.py" JourneyStoryTests
python3 -B "$RUN/kc-dev-flow-2/scripts/test_pr_watch.py" TasksTests.test_real_seed_subprocess_names_a_map_task_missing_its_story_record
python3 -B "$RUN/kc-dev-flow-2/extensions/release-acceptance/test_release_acceptance.py"
python3 -B "$RUN/kc-dev-flow-2/scripts/test_laws_check.py" ExitContractTest.test_check_exiting_2_exits_2_naming_the_cause

# 5. Replay the native archive. Expected: 0/1 and 0/4 become 1/1 and 1/4; PR #999 appears.
git clone --shared --no-checkout "$RELAY_SOURCE" "$RUN/relay" > "$RUN/clone.log" 2>&1
git -C "$RUN/relay" checkout --detach 0fce82296710d7bf3b89c2871adefd71db2e2957 >> "$RUN/clone.log" 2>&1
git -C "$RUN/relay" remote set-url origin https://github.com/spacedock-dev/subspace-relay.git
mkdir -p "$RUN/relay/docs/dev2/.spacedock-state"
git -C "$RELAY_SOURCE" archive 77f5bb4e0e286467ec7078038e8bb9d680baddde | tar -x -C "$RUN/relay/docs/dev2/.spacedock-state"
node "$RUN/kc-journey-map/lib/journey-progress.mjs" "$RUN/relay/docs/journey/spacedock-review.yaml" --workflow-dir "$RUN/relay/docs/dev2" --report inbox-home
spacedock status --workflow-dir "$RUN/relay/docs/dev2" --set inbox-home status=done pr=pr-merge:999 > "$RUN/archive-set.log"
node "$RUN/kc-journey-map/lib/journey-progress.mjs" "$RUN/relay/docs/journey/spacedock-review.yaml" --workflow-dir "$RUN/relay/docs/dev2" --report inbox-home

# 6. Require ADR 0076. Expected: ADR lint passed; acceptance complete.
GIT_META=$(git -C "$REPO" rev-parse --absolute-git-dir)
GIT_DIR="$GIT_META" GIT_WORK_TREE="$RUN" GIT_INDEX_FILE="$RUN/validation.index" git read-tree "$HEAD"
(cd "$RUN" && GIT_DIR="$GIT_META" GIT_WORK_TREE="$RUN" GIT_INDEX_FILE="$RUN/validation.index" python3 -B "$PACKAGE/scripts/adr_lint.py" docs/adr --since fd1caa475f85483cf5c4031a1e58656ff5d3eaff --require 0076)
printf 'acceptance complete: %s\n' "$RUN"
