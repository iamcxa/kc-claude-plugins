#!/bin/bash
set -euo pipefail
WT=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-counts-name-the-run-that-produced-them
STATE=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state
EVIDENCE="$STATE/counts-name-the-run-that-produced-them/validation/implementation-4"
PACKAGE=/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.36.0
export PYTHONDONTWRITEBYTECODE=1 SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock
test "$(git -C "$WT" rev-parse HEAD)" = 4a146449de8ad43f1eb67e59599215989c327645
cd "$WT"

# The historical entry completes unchanged; unsupported cells stay correctable.
python3 -B "$EVIDENCE/probe.py" "$WT" "$STATE/counts-name-the-run-that-produced-them/validation/validation-1/cycle-record.json"

# Retained learn and disclosure callers exercise the real command boundary.
cd "$WT/kc-dev-flow-2/scripts"
python3 -B -m unittest test_learning.LearningTests.test_evidence_count_refusal_leaves_pending_token_correctable test_delivery_gate.CountDisclosureTests

# The new amendment criterion remains valid under the installed workflow checker.
cd "$WT"
python3 -B "$PACKAGE/scripts/design_surfaces.py" check "$STATE/counts-name-the-run-that-produced-them.md"
