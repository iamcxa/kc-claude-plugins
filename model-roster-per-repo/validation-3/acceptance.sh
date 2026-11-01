#!/bin/bash
set -euo pipefail
# 1. Create a disposable exact-head checkout; expect detached cf8e5848.
ROSTER_SOURCE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-model-roster-per-repo'
ROSTER_HEAD='cf8e5848654f03fa5c509751298e2f75d7c151ba'
ROSTER_BASE='9b32877f4b98583fa41ce090664f20b3ffcae122'
ROSTER_CHECK="$(mktemp -d "$ROSTER_SOURCE/.roster-acceptance3.XXXXXX")/candidate"
git -C "$ROSTER_SOURCE" worktree add --detach "$ROSTER_CHECK" "$ROSTER_HEAD"
cd "$ROSTER_CHECK"
test "$(git -C "$ROSTER_CHECK" rev-parse HEAD)" = "$ROSTER_HEAD"
# 2. Check package instructions; expect PASS and workflow 5781/5781 words.
python3 -B kc-dev-flow-2/scripts/lint-skills.py
# 3. Exercise real resolver and model-free dispatch; expect all assertions pass.
TMPDIR=/tmp SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock time -p python3 -B kc-dev-flow-2/scripts/test_sd_dispatch.py --sd-plugin-root /Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3 --keep
# 4. Check the decision record against pinned main; expect 45 ADRs, zero legacy.
python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.1/scripts/adr_lint.py docs/adr --since "$ROSTER_BASE" --require 0047
# 5. Observe absent roster with a real author; expect retained Sol/high author, null validator, unverified family.
python3 -B kc-dev-flow-2/scripts/model_roster.py resolve --code-root "$ROSTER_CHECK" --stage validation --author-record /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/model-roster-per-repo/dispatch/implementation-4.md
# 6. Check untouched candidate and remove this disposable checkout; expect exit 0.
test -z "$(git -C "$ROSTER_CHECK" status --porcelain)"
cd /tmp
git -C "$ROSTER_SOURCE" worktree remove "$ROSTER_CHECK"
rmdir "${ROSTER_CHECK%/candidate}"
