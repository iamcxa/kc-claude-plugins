#!/usr/bin/env bash
# Read-only product checks; scratch exports and replay logs stay under /tmp.
set -euo pipefail
TASK_REPO='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-worker-browser-checks-use-paseo-browser'
TASK_EVIDENCE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/worker-browser-checks-use-paseo-browser/implementation'
TASK_PACKAGE='/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0'
TASK_BASE=139feeaee7ce037a0c6535568cd6bd103155cbae
TASK_HEAD=90192bb64db4614de9a7a94cc782ee5fa44748db
TASK_RUN=$(mktemp -d /tmp/paseo-captain-810.XXXXXX)

# 1. Export the exact candidate. Expected: candidate 90192bb64db4614de9a7a94cc782ee5fa44748db.
test "$(git -C "$TASK_REPO" rev-parse "$TASK_HEAD")" = "$TASK_HEAD"
git -C "$TASK_REPO" archive "$TASK_HEAD" | tar -x -C "$TASK_RUN"
printf 'candidate %s\n' "$TASK_HEAD"

# 2. Observe the instruction and count. Expected: final browser pointer; 1116 and 235 words; no protected-file diff.
git -C "$TASK_REPO" show "$TASK_HEAD:kc-dev-flow-2/extensions/paseo/EXTENSION.md" | grep '^Add to scope notes:'
wc -w "$TASK_RUN/kc-dev-flow-2/extensions/paseo/EXTENSION.md" "$TASK_RUN/kc-dev-flow-2/extensions/paseo/browser.md"
git -C "$TASK_REPO" diff --exit-code "$TASK_BASE" "$TASK_HEAD" -- kc-dev-flow-2/references/sd/workflow.md kc-dev-flow-2/scripts/lint-skills.py kc-dev-flow-2/scripts/dispatch_records.py

# 3. Replay the implementation's existing checks and falsifiers on copied evidence. Expected: 27 checks, passed, failed 0.
cp -R "$TASK_EVIDENCE" "$TASK_RUN/evidence"
bash --noprofile --norc "$TASK_RUN/evidence/acceptance.sh" "$TASK_REPO"

# 4. Run the actual instruction consumer and package lint from the export. Expected: 1 test OK and lint exit 0.
(cd "$TASK_RUN/kc-dev-flow-2/scripts" && python3 -B test_dispatch_records.py ExtensionInstructionTests.test_every_shipped_instruction_is_read_from_its_extension_file)
(cd "$TASK_RUN" && python3 -B kc-dev-flow-2/scripts/lint-skills.py) > "$TASK_RUN/lint.log" 2>&1
printf 'lint exit 0\n'

# 5. Check decision records using read-only Git object access. Expected: 62 ADR file(s) checked, 0 legacy; exit 0.
TASK_GIT_DIR=$(git -C "$TASK_REPO" rev-parse --absolute-git-dir)
(cd "$TASK_RUN" && GIT_DIR="$TASK_GIT_DIR" GIT_WORK_TREE="$TASK_RUN" GIT_OPTIONAL_LOCKS=0 python3 -B "$TASK_PACKAGE/scripts/adr_lint.py" docs/adr --since "$TASK_BASE")
printf 'adr-lint exit 0\n'
printf 'Static/replay checks passed; AC-4 remains Needs decision: successful run explicitly named tools.\n'
printf 'No live browser run, credentials, publication, or cross-host guarantee is covered. Scratch: %s\n' "$TASK_RUN"

