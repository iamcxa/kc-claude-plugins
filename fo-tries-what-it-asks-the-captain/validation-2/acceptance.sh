#!/bin/bash
set -euo pipefail
WT=${CAPTAIN_STEPS_WORKTREE:-/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-fo-tries-what-it-asks-the-captain}
export PYTHONDONTWRITEBYTECODE=1

# Step 1: Enter the candidate checkout. Expect the exact reviewed commit.
cd "$WT"
test "$(git -C "$WT" rev-parse HEAD)" = 128fe3e3fed70fa64ded8657f5a1b36933af3ced
git -C "$WT" rev-parse HEAD

# Step 2: Exercise step coverage and both historical replays. Expect 22 tests, OK.
python3 -B -m unittest discover -s kc-dev-flow-2/scripts -p test_delivery_gate.py -k Captain

# Step 3: Check the approved workflow rules. Expect 5836 of 5836 words and OK.
python3 -B kc-dev-flow-2/scripts/lint-skills.py

# Step 4: Check the reserved decision record. Expect 51 ADR files, 0 legacy; exit 0.
python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py docs/adr --since e1bee223c47a1cd534a665a47776b683375b34fc --require 0054

# Step 5: Show actual captured route-style output. Expect captain steps complete: 1 steps, 0 left to him.
python3 -B - <<'PY'
import datetime, subprocess, sys, tempfile
from pathlib import Path
gate=Path.cwd()/'kc-dev-flow-2/scripts/delivery_gate.py'
observed=subprocess.check_output(['/bin/bash','--noprofile','--norc','-c',"printf 'GET /health 200\\n'"],text=True).strip()
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
with tempfile.TemporaryDirectory() as tmp:
    record=Path(tmp)/'record.md';message=Path(tmp)/'message.md'
    record.write_text('Candidate: 128fe3e3fed70fa64ded8657f5a1b36933af3ced\n\n### Step 1\nAsked: Run the route smoke test.\n'+f'Ran: fresh shell, {stamp}\nObserved: {observed}\n')
    message.write_text('Run the route smoke test.\n```text\n'+observed+'\n```\n')
    done=subprocess.run(['python3','-B',str(gate),'steps',str(record),'--text-file',str(message)])
    sys.exit(done.returncode)
PY
