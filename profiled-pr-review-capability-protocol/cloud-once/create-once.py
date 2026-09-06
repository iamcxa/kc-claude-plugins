import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

root = Path(__file__).resolve().parent
assert hashlib.sha256((root / 'prior.json').read_bytes()).hexdigest() == '66fdc5c16581f9e7f2d84356eacdfe7b89b05f64e430b1e5cf2aa6472393af97'
assert not (root / 'current.json').exists()
marker = root / 'creation-attempt.json'
with marker.open('x') as stream:
    json.dump({'controller_pid': os.getpid(), 'started_monotonic': time.monotonic(),
               'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}, stream)
command = ['conductor', '--json', 'workspace', 'create', '--project-id',
           '8f58f9d4-cb71-443a-b64d-c2a225248c7b', '--branch', 'main',
           '--name', 't8cyxd55ve-cloud-isolation-once', '--session-name', 'Synthetic isolation once',
           '--agent', 'claude', '--model', 'opus-5-1m', '--effort', 'medium']
result = subprocess.run(command, capture_output=True, text=True, timeout=25)
(root / 'creation-response.json').write_text(json.dumps({'command': command, 'exit': result.returncode,
    'stdout': result.stdout, 'stderr': result.stderr, 'finished_monotonic': time.monotonic(),
    'finished_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}, indent=2))
print(result.stdout, flush=True)
print('CREATE_EXIT', result.returncode, flush=True)
raise SystemExit(result.returncode)
