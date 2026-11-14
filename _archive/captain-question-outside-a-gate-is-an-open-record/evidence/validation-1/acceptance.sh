#!/usr/bin/env bash
set -euo pipefail
# 1. Export the exact candidate. Requires Python 3, git, tar, the assigned local clone and the pinned 0.41.0 package.
task_repo='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-captain-question-outside-a-gate-is-an-open-record'
scratch='/tmp/dev2/kc-claude-plugins-3042bb224e995ded/captain-question-outside-a-gate-is-an-open-record/validation-1'
python3 - <<'PY'
import pathlib,sys
sys.path.insert(0,'/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0/scripts')
import scratch
folder=pathlib.Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/captain-question-outside-a-gate-is-an-open-record')
scratch.claim_root(folder,folder,'validation-1')
PY
case_dir=$(mktemp -d "$scratch/captain.XXXXXX")
trap 'rm -rf "$case_dir"' EXIT
mkdir -p "$case_dir/product" "$case_dir/state"
git -C "$task_repo" archive 3d65ebd7a456bcb05fd94ce754a79735bdcbcf39 | tar -x -C "$case_dir/product"
tool="$case_dir/product/kc-dev-flow-2/scripts/task_timeline.py"
printf '%s\n' '---' 'title: Example' '---' > "$case_dir/state/demo.md"
printf '%s\n' 'step 1: candidate exported'

# 2. Ask through the shipped command. Expected key demo#1 and owner Acceptance FO.
python3 -B "$tool" "$case_dir/state" demo ask 'Proceed?' --by 'Acceptance FO' --holds acceptance
python3 -B "$tool" "$case_dir/state" --open --json > "$case_dir/open.json"
python3 - "$case_dir/open.json" <<'PY'
import json,sys
rows=json.load(open(sys.argv[1]))
assert len(rows)==1 and rows[0]['key']=='demo#1' and rows[0]['by']=='Acceptance FO' and rows[0]['state']=='open'
print('step 2: one open question, correct key and owner')
PY

# 3. Record the answer. Expected no open questions, then reask refused with exit 2.
python3 -B "$tool" "$case_dir/state" demo answer 'demo#1' --words Yes
python3 -B "$tool" "$case_dir/state" --open --json > "$case_dir/closed.json"
python3 - "$case_dir/closed.json" <<'PY'
import json,sys
assert json.load(open(sys.argv[1]))==[]
print('step 3: no open questions after answer')
PY
if python3 -B "$tool" "$case_dir/state" demo reask 'demo#1'; then
  printf '%s\n' 'ERROR: closed question reopened'
  exit 1
else
  result=$?
  test "$result" -eq 2
  printf '%s\n' 'step 3: reask refused with exit 2'
fi

# 4. Use the README's plain list on a new open question.
# Expected a line containing demo#2, Acceptance FO, acceptance and Next question?
# At the reviewed head this exposes the failure (KeyError: question).
python3 -B "$tool" "$case_dir/state" demo ask 'Next question?' --by 'Acceptance FO' --holds acceptance
python3 -B "$tool" "$case_dir/state" --open
