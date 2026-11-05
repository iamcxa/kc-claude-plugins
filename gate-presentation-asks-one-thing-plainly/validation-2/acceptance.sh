#!/usr/bin/env bash
# Requirements: Python 3, Git, this declared repository/state history, and the installed ADR checker.
# Scope: CLI reminders, recorded approvals, five historical cases, reason declarations and ADR structure.
# Does not prove live chat fidelity, model reliability, installed activation, remote review, merge or release.
set -euo pipefail

# Step 1: export the exact candidate; expected: the printed SHA is 2493d57a17dcbe08489918b208c9bd5019450772.
WT='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-gate-presentation-asks-one-thing-plainly'
STATE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state'
PACKAGE='/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0'
CANDIDATE=2493d57a17dcbe08489918b208c9bd5019450772
BASE=a7c0bdbe0ae0f111780f6d3b7254ed4ad67befcd
CHECK=$(mktemp -d /tmp/gate-presentation-acceptance-2493d57.XXXXXX)
git -C "$WT" archive "$CANDIDATE" | tar -x -C "$CHECK"
printf 'candidate %s\n' "$CANDIDATE"
cd "$CHECK"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$CHECK/kc-dev-flow-2/scripts"

# Step 2: exercise approval, withdrawal, reminder and both ledger features; expected: 28 tests, OK.
python3 -B -m unittest test_delivery_gate.BoundApprovalTests test_design_surfaces.AskFormTests test_decision_ledger -v

# Step 3: replay all five historical answers; expected: 1 test, OK, and five saved cases.
# This exact read-only redirect supplies the Git history absent from an archive; candidate source stays unchanged.
export GATE_PRESENTATION_STATE="$STATE" GATE_PRESENTATION_BASE="$BASE" GATE_PRESENTATION_EVIDENCE="$CHECK/evidence"
export VALIDATION_SOURCE_REPO="$WT" VALIDATION_EXPORT="$CHECK"
python3 -B - <<'PY'
import json, os, subprocess, unittest
from pathlib import Path
original = subprocess.check_output
def read_history(command, *args, **kwargs):
    if len(command) > 4 and command[:3] == ['git', '-C', os.environ['VALIDATION_EXPORT']] and command[3] == 'show':
        command = ['git', '-C', os.environ['VALIDATION_SOURCE_REPO'], *command[3:]]
    return original(command, *args, **kwargs)
subprocess.check_output = read_history
suite = unittest.defaultTestLoader.loadTestsFromName('test_delivery_gate.HistoricalBoundQuestionTests')
result = unittest.TextTestRunner(verbosity=2).run(suite)
assert result.wasSuccessful()
rows = json.loads((Path(os.environ['GATE_PRESENTATION_EVIDENCE']) / 'historical-replays.json').read_text())
assert len(rows) == 5
print('historical cases: 5')
PY

# Step 4: check ADR 0062 and number reservations against the pinned current-main base; expected: 59 ADRs, zero legacy, PASS: no findings.
# Git metadata is read from the existing checkout; no git worktree or config is created or changed.
GIT_DIR=$(git -C "$WT" rev-parse --absolute-git-dir) GIT_WORK_TREE="$CHECK" python3 -B "$PACKAGE/scripts/adr_lint.py" docs/adr --since "$BASE" --require 0062 --root "$CHECK"
python3 -B "$PACKAGE/scripts/number_guards.py" check --repo "$WT" --workflow-dir "$STATE/.." --task "$STATE/gate-presentation-asks-one-thing-plainly.md" --base "$BASE" --head "$CANDIDATE"

# Step 5: compare the workflow bytes and finish; expected: cmp is silent and acceptance PASS is printed.
git -C "$WT" show "$BASE:kc-dev-flow-2/references/sd/workflow.md" | cmp - kc-dev-flow-2/references/sd/workflow.md
printf 'acceptance PASS; exported candidate and historical evidence: %s\n' "$CHECK"
