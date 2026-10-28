#!/usr/bin/env bash
set -euo pipefail

# 1. Verify the pinned checkout and exact workflow budget.
WT='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-batch-reaches-each-gate-together'
PACKAGE='/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.1'
SD='/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3'
test "$(git -C "$WT" rev-parse HEAD)" = e4bd4d06a1538ed166205609002e5eef1ebf0983
git -C "$WT" rev-parse HEAD
cd "$WT" && python3 -B kc-dev-flow-2/scripts/lint-skills.py

# 2. Check the added architecture decision against the stacked base.
cd "$WT" && python3 -B "$PACKAGE/scripts/adr_lint.py" docs/adr --since ea84b08d4c726e33460609b2247599afb2d54c2b --require 0043

# 3. Verify proof-of-concept derivation retains the batch rule and skips ideation.
cd "$WT" && python3 -B kc-dev-flow-2/scripts/test_poc_readme.py

# 4. Exercise actual local gate and dispatch commands in disposable repositories.
cd "$WT" && SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock python3 -B kc-dev-flow-2/scripts/test_sd_dispatch.py --sd-plugin-root "$SD"

