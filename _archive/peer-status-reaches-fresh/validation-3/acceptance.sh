#!/bin/bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
# 1. Confirm exact product revision. Expected: 39fdbb28b411d44a323741f645c7c1d75c653be1.
WT='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-peer-status-reaches-fresh'
test "$(git -C "$WT" rev-parse HEAD)" = 39fdbb28b411d44a323741f645c7c1d75c653be1
git -C "$WT" rev-parse HEAD
# 2. Check decision records at the assigned stacked base. Expected: 45 ADR file(s) checked, 0 legacy; exit 0.
cd "$WT"
python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.1/scripts/adr_lint.py docs/adr --since 422caef5a9b115a14f8391836499520d9fba6d91
# 3. Reassess unchanged recorded outputs against corrected source attribution. Expected: four attribution PASS, three detected falsifiers, F5 cleared, PASSED within bounded evidence.
python3 -B "$(dirname "${BASH_SOURCE[0]}")/audit_source.py"
