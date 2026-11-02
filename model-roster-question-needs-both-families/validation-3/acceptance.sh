#!/usr/bin/env bash
set -euo pipefail
# Step 1: create an isolated checkout of the reviewed head.
ROSTER_SOURCE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-model-roster-question-needs-both-families'
ROSTER_HEAD=c2643dae831f9685166b7cd564d8d885e88a3f21
ROSTER_BASE=e891e83582ac10936ffd67fb083b530b009ad847
ROSTER_PACKAGE='/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0'
ROSTER_CHECK=$(mktemp -d "$ROSTER_SOURCE/.context/roster-acceptance3.XXXXXX")
git -C "$ROSTER_SOURCE" worktree add --detach "$ROSTER_CHECK" "$ROSTER_HEAD"
test "$(git -C "$ROSTER_CHECK" rev-parse HEAD)" = "$ROSTER_HEAD"
printf 'STEP 1 PASS: exact candidate %s\n' "$ROSTER_HEAD"

# Step 2: exercise question, committed resolution, effort mapping, and family cases.
python3 -B - "$ROSTER_CHECK" <<'PY'
import sys, tempfile, shutil
from pathlib import Path
root = Path(sys.argv[1])
sys.path.insert(0, str(root / "kc-dev-flow-2/scripts"))
import test_sd_dispatch as check
fixture = Path(tempfile.mkdtemp(prefix="roster-acceptance-fixtures-", dir=root.parent))
try:
    check.exercise_extension_lists(fixture / "extensions")
    check.exercise_model_roster(fixture / "roster")
finally:
    shutil.rmtree(fixture)
print("STEP 2 PASS: shared extension-list callers; eight prerequisite combinations; three models and six efforts; wrong pairs refused; absent roster unchanged")
PY

# Step 3: check merged-parent ancestry, literal origin/main equality, lint and ADR 0050.
git -C "$ROSTER_CHECK" merge-base --is-ancestor 52e8eba7bf3746fd93d9132548a8163c66a7a26b "$ROSTER_BASE"
git -C "$ROSTER_CHECK" merge-base --is-ancestor "$ROSTER_BASE" "$ROSTER_HEAD"
test "$(git -C "$ROSTER_CHECK" rev-parse origin/main)" = "$ROSTER_BASE"
git -C "$ROSTER_CHECK" diff --exit-code origin/main "$ROSTER_HEAD" -- kc-dev-flow-2/references/sd/workflow.md
(cd "$ROSTER_CHECK" && python3 -B kc-dev-flow-2/scripts/lint-skills.py)
(cd "$ROSTER_CHECK" && python3 "$ROSTER_PACKAGE/scripts/adr_lint.py" docs/adr --since "$ROSTER_BASE" --require 0050)
printf 'STEP 3 PASS: merged parents; origin/main workflow unchanged; lint and ADR 0050 pass\n'

# Step 4: inspect the retained FO native record and verify release metadata parity.
python3 - '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/model-roster-question-needs-both-families/native-runs/final/receipts.json' <<'PYRECEIPTS'
import json, sys
from datetime import datetime
rows = json.load(open(sys.argv[1]))
expected = {'8c33c57f': ('claude-opus-5-5', 'high'), '575a60c6': ('claude-opus-5-5', 'low'), '84db4474': ('gpt-6.1-sol', 'xhigh'), '45f8566a': ('gpt-6-astra', 'xhigh')}
assert set(rows) == set(expected)
for child, (model, effort) in expected.items():
    row = rows[child]
    assert model in row['models'] and row['efforts'] == [effort]
    assert row['send_tool_calls'] == 0
    assert any(e['event'] == 'finished' and datetime.fromisoformat(e['session_time']) > datetime.fromisoformat(row['last_transcript_time']) for e in row['inbound'])
    if model == 'claude-opus-5-5':
        assert row['process_flags'] == [f'--thinking adaptive --effort {effort} --model {model}']
    print(f'FO RECORD: {child} {model}/{effort}; later finished receipt; no child send')
print('FO RECORD PASS: high differs from low; all four later completions. This reads retained evidence; it does not spawn agents.')
PYRECEIPTS

(cd "$ROSTER_CHECK" && bash scripts/version-parity-check.sh)
printf 'STEP 4 PASS: retained FO record and release metadata parity\n'

# Step 5: verify no tracked edits and remove this checkout.
test -z "$(git -C "$ROSTER_CHECK" status --porcelain)"
git -C "$ROSTER_SOURCE" worktree remove "$ROSTER_CHECK"
printf 'STEP 5 PASS: candidate unchanged; temporary checkout removed\n'

