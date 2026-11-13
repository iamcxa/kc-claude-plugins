#!/bin/bash
set -euo pipefail
# Requires this public repository and state checkout, Python 3 with PyYAML/pytest, Git, tar, wc, and Spacedock.
WT='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-held-and-closed-tasks-leave-the-design-queue'
STATE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state'
EVIDENCE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/held-and-closed-tasks-leave-the-design-queue/validation-2'
CANDIDATE='455846c6d30d4ab650c1c4503bc591722231586d'
FROZEN_STATE='eae5ea47cec926f35d164f8a88d31579196d7634'
CHECK_ROOT="${CAPTAIN_SCRATCH:-$(mktemp -d /tmp/captain-held-v2.XXXXXX)}"
OUTPUT="${CAPTAIN_EVIDENCE:-$CHECK_ROOT/results}"
mkdir -p "$CHECK_ROOT" "$OUTPUT" "$CHECK_ROOT/tmp"
export TMPDIR="$CHECK_ROOT/tmp" PYTHONDONTWRITEBYTECODE=1 SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock
# Step 1: Export the exact candidate. Expected: EXPORT followed by the full candidate.
git -C "$WT" archive "$CANDIDATE" kc-dev-flow-2/scripts docs/dev2/README.md docs/dev2/_mods | tar -x -C "$CHECK_ROOT"
printf 'EXPORT %s\n' "$CANDIDATE"
# Step 2: Export the frozen fourteen public held tasks; use the native Spacedock query later.
python3 - "$CHECK_ROOT" "$STATE" "$EVIDENCE" "$FROZEN_STATE" <<'PY'
from pathlib import Path
import io,json,subprocess,sys,tarfile
root,source,ev=map(Path,sys.argv[1:4]);rev=sys.argv[4]
rows=json.loads((ev/'held-live.json').read_text())['entities']
tracked=set(subprocess.check_output(['git','-C',str(source),'ls-tree','-r','--name-only',rev],text=True).splitlines())
files=['README.md']+[r['slug']+'.md' if r['slug']+'.md' in tracked else r['slug']+'/index.md' for r in rows]
state=root/'docs/dev2/.spacedock-state';state.mkdir(parents=True)
data=subprocess.check_output(['git','-C',str(source),'archive',rev,*files])
tarfile.open(fileobj=io.BytesIO(data)).extractall(state,filter='data')
for path in (root,state):subprocess.run(['git','-C',str(path),'init','-q'],check=True)
print('NATIVE INPUTS 14 public held tasks')
PY
# Step 3: Exercise held behavior. Expected: 11 tests pass.
cd "$CHECK_ROOT"
python3 -B -m pytest -q kc-dev-flow-2/scripts/test_pr_watch.py -k held --junitxml="$OUTPUT/held-tests.xml"
# Step 4: Count actual output and reject one-word-over-bound counterexamples.
# Expected: ONE 17/21 PASS, CURRENT 32/34 PASS, LARGER 145/145 PASS; three REJECTED counterexamples.
python3 -B "$EVIDENCE/measure.py" --candidate "$CHECK_ROOT" --workflow "$CHECK_ROOT/docs/dev2" --scratch "$CHECK_ROOT/measure" --output "$OUTPUT"
printf 'PASS: exact candidate held behavior and amendment-4 counts\n'
# An automated validation keeps its declared root until evidence is committed.
# Interactive callers get automatic cleanup of only the mktemp directory this script owns.
if [ -z "${CAPTAIN_SCRATCH:-}" ]; then rm -rf -- "$CHECK_ROOT"; fi

