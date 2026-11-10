#!/bin/bash
set -euo pipefail
WT=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-counts-name-the-run-that-produced-them
EVIDENCE=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/counts-name-the-run-that-produced-them/validation/validation-2
TASK=/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/counts-name-the-run-that-produced-them.md
PACKAGE=/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.36.0
HEAD=4a146449de8ad43f1eb67e59599215989c327645
export PYTHONDONTWRITEBYTECODE=1 SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock

# Step 1: export the exact candidate. Expect the full pinned revision.
CHECKOUT=$(mktemp -d /tmp/pr822-captain.XXXXXX)
git -C "$WT" archive "$HEAD" | tar -x -C "$CHECKOUT"
mkdir -p "$CHECKOUT/.context"
printf 'Exported %s\n' "$HEAD"

# Step 2: unchanged historical citation completes; wrong counts remain correctable.
python3 -B "$EVIDENCE/probe.py" "$CHECKOUT" "$EVIDENCE/cycle-record.json"

# Step 3: retained refusal, disclosure and forwarding checks. Expect OK.
cd "$CHECKOUT/kc-dev-flow-2/scripts"
python3 -B -m unittest test_learning.LearningTests.test_evidence_count_refusal_leaves_pending_token_correctable test_learning.LearningTests.test_completed_legacy_counts_remain_readable test_delivery_gate.CountDisclosureTests test_poc_readme.DeriveTests.test_delivery_recipe_holds_nonzero_and_forwards_checked_summary_in_both_routes

# Step 4: the amended criteria are presentable. Expect exit 0.
cd "$CHECKOUT"
python3 -B "$PACKAGE/scripts/design_surfaces.py" check "$TASK"
printf 'Acceptance passed for %s\n' "$HEAD"
