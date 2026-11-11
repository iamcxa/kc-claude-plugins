#!/usr/bin/env bash
set -euo pipefail

# Step 1: export both exact candidates. Expected: the two pinned SHA lines.
REPO=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-story-done-reports-release-remaining
DEV2_REPO=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-story-done-reports-release-remaining-dev2
PACKAGE=/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1
RELAY_SOURCE=/Users/kent/conductor/repos/subspace-relay
RUN=$(mktemp -d /tmp/story-progress-captain.XXXXXX)
git -C "$REPO" archive fd1caa475f85483cf5c4031a1e58656ff5d3eaff | tar -x -C "$RUN"
git -C "$REPO" archive fa485f008562f00ebf91deed19e58ea52bb4b4dc kc-dev-flow-2 docs/adr | tar -x -C "$RUN"
printf '%s\n' fd1caa475f85483cf5c4031a1e58656ff5d3eaff fa485f008562f00ebf91deed19e58ea52bb4b4dc

# Step 2: use the declared, preinstalled candidate dependencies. Expected: dependencies available.
# Prerequisite: npm ci was completed in REPO/kc-journey-map; Node >=22.13 and Spacedock 0.27.2 are on PATH.
test -d "$REPO/kc-journey-map/node_modules/yaml"
cmp "$REPO/kc-journey-map/package-lock.json" "$RUN/kc-journey-map/package-lock.json"
ln -s "$REPO/kc-journey-map/node_modules" "$RUN/kc-journey-map/node_modules"
printf '%s\n' 'dependencies available'

# Step 3: exercise report, ref, bounds and schema controls. Expected: 4 tests pass.
node --test --test-name-pattern='filed membership|archive report|report separates|journey-progress registers' "$RUN/kc-journey-map/lib/progress.test.mjs" "$RUN/kc-journey-map/lib/schemas.test.mjs"

# Step 4: exercise both story forms, idle reminder and whole-document consumer. Expected: 2, 1, and 122 tests OK.
python3 -B "$RUN/kc-dev-flow-2/scripts/test_design_surfaces.py" JourneyStoryTests
python3 -B "$RUN/kc-dev-flow-2/scripts/test_pr_watch.py" TasksTests.test_real_seed_subprocess_names_a_map_task_missing_its_story_record
python3 -B "$RUN/kc-dev-flow-2/extensions/release-acceptance/test_release_acceptance.py"

# Step 5: replay an archive through real Spacedock. Expected: 0/1 and 0/4 become 1/1 and 1/4; PR #999 appears.
mkdir -p "$RUN/relay"
git -C "$RELAY_SOURCE" archive 0fce82296710d7bf3b89c2871adefd71db2e2957 | tar -x -C "$RUN/relay"
mkdir -p "$RUN/relay/docs/dev2/.spacedock-state"
git -C "$RELAY_SOURCE" archive 77f5bb4e0e286467ec7078038e8bb9d680baddde | tar -x -C "$RUN/relay/docs/dev2/.spacedock-state"
git -C "$RUN/relay" init -q
git -C "$RUN/relay" remote add origin https://github.com/spacedock-dev/subspace-relay.git
node "$RUN/kc-journey-map/lib/journey-progress.mjs" "$RUN/relay/docs/journey/spacedock-review.yaml" --workflow-dir "$RUN/relay/docs/dev2" --report inbox-home
spacedock status --workflow-dir "$RUN/relay/docs/dev2" --set inbox-home status=done pr=pr-merge:999 > "$RUN/archive-set.log"
node "$RUN/kc-journey-map/lib/journey-progress.mjs" "$RUN/relay/docs/journey/spacedock-review.yaml" --workflow-dir "$RUN/relay/docs/dev2" --report inbox-home

# Step 6: require the approved decision record. Expected: ADR lint passed and acceptance complete.
(cd "$RUN" && GIT_DIR="$(git -C "$DEV2_REPO" rev-parse --absolute-git-dir)" GIT_WORK_TREE="$RUN" python3 -B "$PACKAGE/scripts/adr_lint.py" docs/adr --since e8664a72b0f904e5dda3c391d52ab3abaca876b4 --require 0076)
printf 'acceptance complete: %s\n' "$RUN"
