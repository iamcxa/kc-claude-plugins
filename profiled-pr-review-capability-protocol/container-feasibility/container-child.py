import json
import os
from pathlib import Path
import subprocess
import sys
import time

work = Path('/work')
config = json.loads((work / 'input.json').read_text())
owner = Path(config['owner'])
prior = owner / 'pilot-runs/2-control/receipt.json'


def attempt(label, action):
    try:
        action()
        return {'case': label, 'write_allowed': True}
    except OSError as error:
        return {'case': label, 'write_allowed': False, 'errno': error.errno}


def mutate(path):
    path.chmod(0o600)
    value = json.loads(path.read_text())
    value['wallclock_ms'] = 1
    path.write_text(json.dumps(value))


def ancestor():
    base = owner.parent
    moved = base.with_name(base.name + '-moved')
    base.rename(moved)
    try:
        mutate(moved / 'owner/pilot-runs/2-control/receipt.json')
    finally:
        moved.rename(base)


if '--descendant' in sys.argv:
    result = attempt('independent-group-prior-write', lambda: mutate(prior))
    result.update(pid=os.getpid(), pgid=os.getpgrp())
    (work / 'descendant.json').write_text(json.dumps(result))
    time.sleep(15)
    sys.exit(0)

(work / 'new-owner-alias').symlink_to(owner, target_is_directory=True)
checks = [
    attempt('current-preplant', lambda: (owner / 'pilot-runs/1-control/receipt.json').write_text(json.dumps(config['planted']))),
    attempt('prior-overwrite-chmod', lambda: mutate(prior)),
    attempt('ancestor-rename-restore', ancestor),
    attempt('traversal', lambda: mutate(work / '..' / str(prior).lstrip('/'))),
    attempt('new-symlink', lambda: mutate(work / 'new-owner-alias/pilot-runs/2-control/receipt.json')),
    attempt('new-hardlink', lambda: os.link(prior, work / 'new-hardlink.json')),
    attempt('protected-unlink', lambda: (owner / 'sentinel').unlink()),
    attempt('protected-directory-rename', lambda: owner.rename(work / 'moved-owner')),
    attempt('protected-directory-unlink', lambda: (owner / 'empty').rmdir()),
    attempt('workspace-write', lambda: (work / 'normal.txt').write_text('normal')),
    attempt('output-write', lambda: (work / 'output.txt').write_text('output')),
    attempt('temp-write', lambda: Path('/tmp/normal.txt').write_text('temp')),
]
subprocess.run(['/bin/bash', '-c', 'test "$(printf nested)" = nested'], check=True)
descendant = subprocess.Popen([sys.executable, '/work/child.py', '--descendant'], start_new_session=True)
deadline = time.monotonic() + 3
while not (work / 'descendant.json').exists() and time.monotonic() < deadline:
    time.sleep(.02)
assert (work / 'descendant.json').exists(), 'descendant did not execute'
details = json.loads((work / 'descendant.json').read_text())
assert details['pgid'] != os.getpgrp()
assert descendant.poll() is None, 'descendant not alive during observation'
(work / 'child.json').write_text(json.dumps({
    'checks': checks, 'pid': os.getpid(), 'pgid': os.getpgrp(), 'uid': os.getuid(),
    'python': sys.version, 'descendant_alive_at_observation': True,
    'credential_env_present': any(key in os.environ for key in ('ANTHROPIC_API_KEY', 'GITHUB_TOKEN', 'GH_TOKEN')),
}))
if config['mode'] == 'timeout':
    time.sleep(15)
print(json.dumps({'synthetic': True}), flush=True)
sys.exit(7 if config['mode'] == 'failure' else 0)
