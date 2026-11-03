#!/bin/bash
set -euo pipefail
WT=${CAPTAIN_STEPS_WORKTREE:-/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-fo-tries-what-it-asks-the-captain}
EVIDENCE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$WT"
export PYTHONDONTWRITEBYTECODE=1
# Expected: all step, gate replay and mutation tests pass.
python3 -B -m unittest discover -s kc-dev-flow-2/scripts -p test_delivery_gate.py -k Captain
# Expected: exact approved workflow count and retained routing checks pass.
python3 -B kc-dev-flow-2/scripts/lint-skills.py
# Expected: the removed observer phrase is rejected in a disposable copy.
python3 -B "$EVIDENCE_DIR/falsifiers.py"
# Expected: 5781 to 5836 words (+55), 64 to 33 validation words, 86-word section, nine-word pass line.
python3 -B "$EVIDENCE_DIR/recount.py"
# Expected: twenty-two isolated mutations each make their designated check fail.
python3 -B "$EVIDENCE_DIR/mutations.py"
