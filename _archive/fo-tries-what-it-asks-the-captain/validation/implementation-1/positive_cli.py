import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

WT = Path(os.environ.get('CAPTAIN_STEPS_WORKTREE', '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-fo-tries-what-it-asks-the-captain'))
OUT = Path(__file__).resolve().parent
head = subprocess.check_output(['git','-C',str(WT),'rev-parse','HEAD'],text=True).strip()
commands = ["python3 -c 'print(\"fixture ready\")'", f'python3 -B {WT}/kc-dev-flow-2/scripts/lint-skills.py']
body = f'Candidate: {head}\n\n'
message = ''
observed=[]
for i, command in enumerate(commands,1):
    run = subprocess.run(['/bin/bash','--noprofile','--norc','-c',command],cwd=WT,text=True,capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    assert run.returncode == 0, run.stderr
    timestamp=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    output=run.stdout.strip()
    body += f'### Step {i}\nAsked: {command}\nRan: {command}; fresh shell at {WT}, {timestamp}\nObserved: {output}\n\n'
    message += f'```sh\n{command}\n```\nObserved:\n```text\n{output}\n```\n\n'
    observed.append({'command':command,'exit':run.returncode,'output':output,'time':timestamp})
body += '### Step 3\nAsked: Review this candidate\nRan: none — his release judgment\nOnly he can: approve the candidate — his release judgment\n'
message += 'Review this candidate\nOnly he can approve the candidate — his release judgment\n'
record=OUT/'positive-record.md'
text=OUT/'positive-message.md'
record.write_text(body)
text.write_text(message)
run = subprocess.run([sys.executable,'-B',str(WT/'kc-dev-flow-2/scripts/delivery_gate.py'),'steps',str(record),'--text-file',str(text)],cwd=WT,text=True,capture_output=True)
assert (run.returncode,run.stdout)==(0,'captain steps complete: 3 steps, 1 left to him\n'), (run.returncode,run.stdout,run.stderr)
(OUT/'positive-cli.json').write_text(json.dumps({'candidate':head,'runs':observed,'steps_check':{'exit':run.returncode,'output':run.stdout}},indent=2)+'\n')
print(run.stdout,end='')
