#!/bin/bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPYCACHEPREFIX="$(mktemp -d /tmp/peer-validation-cache.XXXXXX)"
# 1. Confirm the reviewed revision. Expected: 1df246fa992ce0864348c2ffe67d93e80ad0a4b8.
WT="/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-peer-status-reaches-fresh"
test "$(git -C "$WT" rev-parse HEAD)" = 1df246fa992ce0864348c2ffe67d93e80ad0a4b8
git -C "$WT" rev-parse HEAD
cd "$WT"
# 2. Check package routing and unchanged workflow budget. Expected: PASS; 5781 of 5781 words.
python3 -B kc-dev-flow-2/scripts/lint-skills.py
# 3. Check lint counterexamples. Expected: Ran 45 tests; OK.
python3 -B kc-dev-flow-2/scripts/test_lint_skills.py
# 4. Check worker dispatch contracts. Expected: all PASS; native execution listed as not run.
python3 -B kc-dev-flow-2/scripts/test_sd_dispatch.py --sd-plugin-root /Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3
# 5. Check decision records at the stacked base. Expected: 45 ADR file(s) checked, 0 legacy; exit 0.
python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.1/scripts/adr_lint.py docs/adr --since 422caef5a9b115a14f8391836499520d9fba6d91
# 6. Read the bounded evidence audit. Expected: Cold core 8 queries, falsifiers detected, then REJECTED for the retained gaps.
python3 -B "$(dirname "${BASH_SOURCE[0]}")/audit_evidence.py"
