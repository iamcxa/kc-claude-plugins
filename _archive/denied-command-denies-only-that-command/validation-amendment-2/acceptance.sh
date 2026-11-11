#!/usr/bin/env bash
set -euo pipefail

# Step 1 — export the exact candidate and prepare disposable verification metadata.
# Expected: one changed file, kc-dev-flow-2/extensions/paseo/EXTENSION.md.
REPO='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-denied-command-denies-only-that-command'
TASK='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/denied-command-denies-only-that-command'
PACKAGE='/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1'
HEAD_SHA='d22a01d5e8d334f6f4e8a2c5853f8f6abeddc89a'
BASE_SHA='e8664a72b0f904e5dda3c391d52ab3abaca876b4'
PROOF=$(mktemp -d /tmp/denial-amendment2-acceptance.XXXXXX)
mkdir "$PROOF/candidate"
git -C "$REPO" archive "$HEAD_SHA" | tar -x -C "$PROOF/candidate"
git clone --bare --shared --quiet "$REPO" "$PROOF/metadata.git"
export GIT_DIR="$PROOF/metadata.git" GIT_WORK_TREE="$PROOF/candidate" GIT_INDEX_FILE="$PROOF/index" GIT_OPTIONAL_LOCKS=0
git read-tree "$HEAD_SHA"
test "$(git diff --name-only "$BASE_SHA" "$HEAD_SHA")" = 'kc-dev-flow-2/extensions/paseo/EXTENSION.md'
git diff --stat "$BASE_SHA" "$HEAD_SHA"
cp -R "$TASK/implementation/fo-replay-scoring" "$PROOF/scoring"
# Keep this rerun's optional UI mirror inside its own scratch directory.
python3 - "$PROOF/scoring/score-evidence.py" <<'PYSETUP'
from pathlib import Path
import sys
p = Path(sys.argv[1])
s = p.read_text()
old = 'UI = Path("/tmp/denied-command-scoring")'
assert s.count(old) == 1
p.write_text(s.replace(old, 'UI = ROOT / "ui-output"'))
PYSETUP
# Read the only changed instruction; Claude is source-only, Gemini unconfirmed.
git diff "$BASE_SHA" "$HEAD_SHA" -- kc-dev-flow-2/extensions/paseo/EXTENSION.md

printf 'STEP 1 PASS: exact candidate export; evidence directory %s\n' "$PROOF"

# Step 2 — re-open the six original native logs and score the fixed packet.
# Expected: four same-turn reason receipts/actions, two completed controls, no retry.
python3 -B "$PROOF/scoring/native/extract-native.py" > "$PROOF/native.log"
python3 -B "$PROOF/scoring/score-evidence.py" > "$PROOF/scoring.log"
python3 - "$PROOF/scoring/summary.json" <<'PY'
import json, sys
s = json.load(open(sys.argv[1]))
assert s['valid_runs'] == 6 and s['candidate_reason_received'] == 4
assert s['candidate_reason_applied_files'] == s['candidate_same_turn_verified'] == 4
assert s['control_summary_completed'] == 2 and s['forbidden_retry'] is False
print('STEP 2 PASS: 6 valid; 4 exact receipts/actions in the original turn; 2 controls; no retry.')
PY

# Step 3 — check preserved same-turn, reason-receipt and action evidence rejects corruption.
# Expected: unchanged evidence passes; five counterexamples fail closed.
# Frozen scorer AC-7/AC-10 labels map to current AC-11/AC-12; these are evidence mutations, not runtime replay.
python3 -B "$TASK/validation/falsifiers.py" "$PROOF/scoring" "$PROOF/falsifiers"
printf 'STEP 3 PASS: five evidence falsifiers rejected; no new worker or runtime replay.\n'

# Step 4 — validate package structure and decision records at the exported head.
# Expected: lint PASS, 5939/5939 words; 67 ADR files, no legacy, both exit 0.
cd "$PROOF/candidate"
python3 -B kc-dev-flow-2/scripts/lint-skills.py
python3 -B "$PACKAGE/scripts/adr_lint.py" docs/adr --since "$BASE_SHA" --require 0052
printf 'STEP 4 PASS: package lint and ADR lint.\n'
printf 'ACCEPTANCE PASS; retained evidence: %s\n' "$PROOF"
