#!/bin/bash
set -euo pipefail
# Step 1: Export the exact candidate and the declared public state.
WT='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-held-and-closed-tasks-leave-the-design-queue'
STATE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state'
EVIDENCE='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/held-and-closed-tasks-leave-the-design-queue/validation'
CANDIDATE='455846c6d30d4ab650c1c4503bc591722231586d'
CHECK_ROOT="${CAPTAIN_SCRATCH:-$(mktemp -d /tmp/captain-held-check.XXXXXX)}"
mkdir -p "$CHECK_ROOT"
git -C "$WT" archive "$CANDIDATE" kc-dev-flow-2/scripts docs/dev2/README.md docs/dev2/_mods | tar -x -C "$CHECK_ROOT"
printf 'EXPORT %s %s\n' "$CANDIDATE" "$CHECK_ROOT"
# Step 2: Build isolated native query inputs from existing public held task files.
export SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock
python3 - "$CHECK_ROOT" "$STATE" "$EVIDENCE" <<'PY'
from pathlib import Path
import io,json,os,subprocess,sys,tarfile
root,source,ev=map(Path,sys.argv[1:])
rows=json.loads((ev/'held-live.json').read_text())['entities']
tracked=set(subprocess.check_output(['git','-C',str(source),'ls-tree','-r','--name-only','eae5ea47cec926f35d164f8a88d31579196d7634'],text=True).splitlines())
files=['README.md']+[r['slug']+'.md' if r['slug']+'.md' in tracked else r['slug']+'/index.md' for r in rows]
for prefix,names in [(root,files),(root/'one',['README.md','adoption-asks-which-extensions.md'])]:
    state=prefix/'docs/dev2/.spacedock-state';state.mkdir(parents=True,exist_ok=True)
    if prefix!=root:
        (prefix/'docs/dev2/README.md').write_bytes((root/'docs/dev2/README.md').read_bytes())
    data=subprocess.check_output(['git','-C',str(source),'archive','eae5ea47cec926f35d164f8a88d31579196d7634',*names])
    tarfile.open(fileobj=io.BytesIO(data)).extractall(state,filter='data')
    subprocess.run(['git','-C',str(prefix),'init','-q'],check=True)
    subprocess.run(['git','-C',str(state),'init','-q'],check=True)
print('NATIVE INPUTS 14 held tasks and one-task subset')
PY
# Step 3: Run the candidate's held behavior tests; expected eleven pass.
cd "$CHECK_ROOT"
PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest -q kc-dev-flow-2/scripts/test_pr_watch.py -k held
# Step 4: Recount the amended bound through the real Spacedock query.
# Expected: CURRENT 14/32/48 PASS, ONE 1/17/9 FAIL, script exit 1.
python3 -B "$EVIDENCE/captain-check.py" "$CHECK_ROOT" "$STATE"
