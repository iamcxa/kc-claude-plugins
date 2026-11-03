import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

WT = Path(os.environ.get('CAPTAIN_STEPS_WORKTREE', '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-fo-tries-what-it-asks-the-captain'))
OUT = Path(__file__).resolve().parent
head = subprocess.check_output(['git','-C',str(WT),'rev-parse','HEAD'],text=True).strip()
commands = ["python3 -c 'print(1 + 1)'", f'python3 -B {WT}/kc-dev-flow-2/scripts/lint-skills.py']
body = f'Candidate: {head}\n\n'
message = ''
observed=[]
for i, command in enumerate(commands,1):
    run = subprocess.run(['/bin/bash','--noprofile','--norc','-c',command],cwd=WT,text=True,capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    assert run.returncode == 0, run.stderr
    timestamp=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    output=run.stdout.strip()
    body += f'### Step {i}\nAsked: {command}\nRan: {command}; fresh shell at {WT}, {timestamp}\nObserved: {output}\n\n'
    message += f'```sh\n{command}\n```\nObserved:\n```\n{output}\n```\n\n'
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

card = OUT/'captain-card.md'
card.write_text(f"```sh\n{commands[0]}\n```\n```text\n{observed[0]['output']}\n```\n")
card_record=OUT/'card-record.md'
card_record.write_text(f"Candidate: {head}\n\n### Step 1\nAsked: {commands[0]}\nRan: {commands[0]}; fresh shell, {observed[0]['time']}\nObserved: {observed[0]['output']}\n")
card_message=OUT/'card-message.md'
card_message.write_text(f"Run the card at {card}:13\n")
card_check=subprocess.run([sys.executable,'-B',str(WT/'kc-dev-flow-2/scripts/delivery_gate.py'),'steps',str(card_record),'--text-file',str(card_message)],cwd=WT,text=True,capture_output=True)
assert card_check.returncode==0, card_check.stdout+card_check.stderr
saved=json.loads((OUT/'positive-cli.json').read_text())
saved['named_card_check']={'exit':card_check.returncode,'output':card_check.stdout,'command':commands[0],'observed':observed[0]['output']}
assert observed[0]['output']=='2'
(OUT/'positive-cli.json').write_text(json.dumps(saved,indent=2)+'\n')

import shlex

emitter = OUT / 'emit_response.py'
emitter.write_text("print('GET /health 200')\n")
command = 'python3 -B ' + shlex.quote(str(emitter))
run = subprocess.run(['/bin/bash', '--noprofile', '--norc', '-c', command], cwd=WT,
                     text=True, capture_output=True, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
assert run.returncode == 0 and run.stdout.strip() == 'GET /health 200', run.stdout + run.stderr
timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
record = OUT / 'response-record.md'
message = OUT / 'response-message.md'
record.write_text(f'Candidate: {head}\n\n### Step 1\nAsked: {command}\nRan: {command}; fresh shell at {WT}, {timestamp}\nObserved: {run.stdout.strip()}\n')
shown = f'```sh\n{command}\n```\n```text\n{run.stdout.strip()}\n```\n'
message.write_text(shown)
args = [sys.executable, '-B', str(WT / 'kc-dev-flow-2/scripts/delivery_gate.py'), 'steps', str(record), '--text-file', str(message)]
passed = subprocess.run(args, cwd=WT, text=True, capture_output=True)
assert passed.returncode == 0, passed.stdout + passed.stderr
missing = OUT / 'unrecorded-path'
assert not missing.exists()
negative_message = OUT / 'response-with-unrecorded-path.md'
negative_message.write_text(shown + f'Inspect {missing}\n')
held = subprocess.run(args[:-1] + [str(negative_message)], cwd=WT, text=True, capture_output=True)
assert held.returncode == 1 and f'S4: missing path {missing}' in held.stdout, held.stdout + held.stderr
assert 'S4: missing path /health' not in held.stdout
(OUT / 'response-output-cli.json').write_text(json.dumps({
    'candidate': head, 'scope': 'Actual fresh-shell emission of a log line; no live HTTP endpoint was contacted',
    'command': command, 'exit': run.returncode, 'output': run.stdout.strip(), 'time': timestamp,
    'recorded_output_check': {'exit': passed.returncode, 'output': passed.stdout},
    'unrecorded_path_check': {'exit': held.returncode, 'output': held.stdout}}, indent=2) + '\n')
print('PASS: emitted GET /health 200 is accepted; an independent missing path is held')
