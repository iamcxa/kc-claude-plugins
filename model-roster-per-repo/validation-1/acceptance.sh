#!/bin/bash
set -euo pipefail
# 1. Create an isolated checkout and verify the exact candidate.
ROSTER_SOURCE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-model-roster-per-repo'
ROSTER_HEAD='a8536dc5239edc3db6c1b76cb3bb7e1ce0433088'
ROSTER_BASE='9f065b01f1c6d6561793a168f584075edb85bf1f'
ROSTER_CHECK="$(mktemp -d "$ROSTER_SOURCE/.context/roster-acceptance.XXXXXX")/candidate"
git -C "$ROSTER_SOURCE" worktree add --detach "$ROSTER_CHECK" "$ROSTER_HEAD"
cd "$ROSTER_CHECK"
test "$(git -C "$ROSTER_CHECK" rev-parse HEAD)" = "$ROSTER_HEAD"
# 2. Check the shipped package and its fixed workflow reading budget.
python3 -B kc-dev-flow-2/scripts/lint-skills.py
# 3. Exercise the real resolver and existing dispatch transport without models.
TMPDIR=/tmp SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock time -p python3 -B kc-dev-flow-2/scripts/test_sd_dispatch.py --sd-plugin-root /Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3 --keep
# 4. Check the added decision record against the stacked base.
python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.1/scripts/adr_lint.py docs/adr --since "$ROSTER_BASE" --require 0047
# 5. Observe absence at this exact code checkout.
python3 -B kc-dev-flow-2/scripts/model_roster.py resolve --code-root "$ROSTER_CHECK" --stage validation
# 6. Confirm no product edits and remove only this disposable checkout.
test -z "$(git -C "$ROSTER_CHECK" status --porcelain)"
cd /tmp
git -C "$ROSTER_SOURCE" worktree remove "$ROSTER_CHECK"
rmdir "${ROSTER_CHECK%/candidate}"
