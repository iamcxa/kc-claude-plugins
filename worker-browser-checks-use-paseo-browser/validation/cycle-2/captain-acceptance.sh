#!/usr/bin/env bash
set -euo pipefail
TASK_REPO='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-worker-browser-checks-use-paseo-browser'
TASK_FOLDER='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/worker-browser-checks-use-paseo-browser'
TASK_PACKAGE='/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0'
TASK_BASE=139feeaee7ce037a0c6535568cd6bd103155cbae
TASK_HEAD=fef21735308e7e807d04a93a5506de5284dde436
TASK_RUN=$(mktemp -d /tmp/paseo-captain-810-amended.XXXXXX)

# 1. Export the exact candidate; expected candidate fef21735308e7e807d04a93a5506de5284dde436.
test "$(git -C "$TASK_REPO" rev-parse "$TASK_HEAD")" = "$TASK_HEAD"
git -C "$TASK_REPO" archive "$TASK_HEAD" | tar -x -C "$TASK_RUN"
printf 'candidate %s\n' "$TASK_HEAD"

# 2. Read the entry and guide; expected conditional pointer, 1112/228 words and no protected-file diff.
rg '^Add to scope notes:' "$TASK_RUN/kc-dev-flow-2/extensions/paseo/EXTENSION.md"
cat "$TASK_RUN/kc-dev-flow-2/extensions/paseo/browser.md"
wc -w "$TASK_RUN/kc-dev-flow-2/extensions/paseo/EXTENSION.md" "$TASK_RUN/kc-dev-flow-2/extensions/paseo/browser.md"
git -C "$TASK_REPO" diff --exit-code "$TASK_BASE" "$TASK_HEAD" -- kc-dev-flow-2/references/sd/workflow.md kc-dev-flow-2/scripts/lint-skills.py kc-dev-flow-2/scripts/dispatch_records.py

# 3. Replay existing assertions and falsifiers on copied evidence; expected 34 passed, failed 0.
mkdir -p "$TASK_RUN/task"
cp -R "$TASK_FOLDER/implementation" "$TASK_RUN/task/implementation"
cp "$TASK_FOLDER.md" "$TASK_RUN/task.md"
bash --noprofile --norc "$TASK_RUN/task/implementation/acceptance.sh" "$TASK_REPO"

# 4. Exercise the real dispatch consumer and lint; expected 115 tests OK (1 skip), lint exit 0.
(cd "$TASK_RUN" && python3 -B kc-dev-flow-2/scripts/test_dispatch_records.py)
(cd "$TASK_RUN" && python3 -B kc-dev-flow-2/scripts/lint-skills.py) > "$TASK_RUN/lint.log" 2>&1
printf 'lint exit 0\n'

# 5. Check decision records with read-only Git object access; expected 62 files, 0 legacy, exit 0.
TASK_GIT_DIR=$(git -C "$TASK_REPO" rev-parse --absolute-git-dir)
(cd "$TASK_RUN" && GIT_DIR="$TASK_GIT_DIR" GIT_WORK_TREE="$TASK_RUN" GIT_OPTIONAL_LOCKS=0 python3 -B "$TASK_PACKAGE/scripts/adr_lint.py" docs/adr --since "$TASK_BASE")
printf 'adr-lint exit 0\n'
printf 'Amended static/replay checks passed. Historical browser runs remain at 20eb8255daf0f1267a8c0dd16daf0705a7cf82ba.\n'
printf 'No live browser run, login success, unattended Paseo default, cross-host guarantee or delivery is covered. Scratch: %s\n' "$TASK_RUN"
