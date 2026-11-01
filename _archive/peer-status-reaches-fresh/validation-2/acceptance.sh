#!/bin/bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPYCACHEPREFIX="$(mktemp -d /tmp/peer-validation2-cache.XXXXXX)"
# 1. Confirm the reviewed revision. Expected: 39fdbb28b411d44a323741f645c7c1d75c653be1.
WT="/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-peer-status-reaches-fresh"
test "$(git -C "$WT" rev-parse HEAD)" = 39fdbb28b411d44a323741f645c7c1d75c653be1
git -C "$WT" rev-parse HEAD
cd "$WT"
# 2. Check routing and workflow budget. Expected: PASS; 5781 of 5781 words.
python3 -B kc-dev-flow-2/scripts/lint-skills.py
# 3. Exercise lint counterexamples. Expected: Ran 45 tests; OK.
python3 -B kc-dev-flow-2/scripts/test_lint_skills.py
# 4. Exercise worker dispatch contracts. Expected: all PASS; native execution explicitly not run.
python3 -B kc-dev-flow-2/scripts/test_sd_dispatch.py --sd-plugin-root /Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3
# 5. Check decision records at the assigned stacked base. Expected: 45 ADR file(s) checked, 0 legacy; exit 0.
python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.1/scripts/adr_lint.py docs/adr --since 422caef5a9b115a14f8391836499520d9fba6d91
# 6. Reproduce the bounded evidence audit. Expected: 8 queries, detected falsifiers, then REJECTED for two missing source revisions/links.
python3 -B "$(dirname "${BASH_SOURCE[0]}")/audit_evidence.py"
