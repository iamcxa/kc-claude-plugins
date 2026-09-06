#!/usr/bin/env bash
set -eu
case "${1:-}" in normal|nonzero|timeout) ;; *) exit 64 ;; esac
test "${CONDUCTOR_IS_LOCAL:-unset}" = 0 || exit 65
command -v python3 >/dev/null || exit 69
exec python3 -B - "$1" <<'PY'
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

mode = sys.argv[1]
controller = Path('/private/tmp/pilot-cloud-controller.3eDzbW')
prior = controller / 'prior.json'
workspace = Path.cwd().resolve()
configured = os.environ.get('CONDUCTOR_WORKSPACE_PATH')
if not configured or Path(configured).resolve() != workspace:
    raise SystemExit('refuse: terminal must be at exact cloud workspace root')
scratch = Path(tempfile.mkdtemp(prefix='t8cyxd55ve-cloud-probe-', dir=workspace))


def attempt(label, operation):
    try:
        operation()
        return {'case': label, 'write_allowed': True}
    except OSError as error:
        return {'case': label, 'write_allowed': False, 'errno': error.errno}


def overwrite():
    prior.chmod(0o600)
    prior.write_text('{"fixture":"t8cyxd55ve-cloud-controller-only","wallclock_ms":1}\n')


checks = [
    attempt('prior-overwrite', overwrite),
    attempt('current-preplant', lambda: (controller / 'current.json').write_text('{"forged":true}\n')),
    attempt('workspace-write', lambda: (scratch / 'normal.txt').write_text('synthetic work\n')),
]
descendant_code = r'''
import json, os, pathlib, sys, time
scratch, prior = map(pathlib.Path, sys.argv[1:])
try:
    prior.chmod(0o600)
    prior.write_text('{"fixture":"t8cyxd55ve-cloud-controller-only","wallclock_ms":1}\n')
    result = {'write_allowed': True}
except OSError as error:
    result = {'write_allowed': False, 'errno': error.errno}
result.update(pid=os.getpid(), pgid=os.getpgrp())
(scratch / 'descendant.json').write_text(json.dumps(result))
for count in range(45):
    (scratch / 'heartbeat.json').write_text(json.dumps({'synthetic_tick': count}))
    time.sleep(1)
'''
descendant = subprocess.Popen(
    [sys.executable, '-B', '-c', descendant_code, str(scratch), str(prior)],
    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    start_new_session=True, close_fds=True,
)
deadline = time.monotonic() + 3
while not (scratch / 'descendant.json').exists() and time.monotonic() < deadline:
    time.sleep(.02)
result = {
    'untrusted_synthetic_output': True, 'mode': mode, 'scratch': str(scratch),
    'checks': checks, 'pid': os.getpid(), 'pgid': os.getpgrp(),
    'descendant_alive': descendant.poll() is None,
    'descendant': json.loads((scratch / 'descendant.json').read_text()) if (scratch / 'descendant.json').exists() else None,
    'command_available': {name: shutil.which(name) is not None for name in ('bash', 'python3', 'conductor')},
    'agent_tool_permissions': 'UNVERIFIED: terminal cannot inventory agent RunLocalCommand or MCP grants',
    'controller_write_credential_authority': 'UNVERIFIED: no real credentials inspected or exercised',
}
(scratch / 'result.json').write_text(json.dumps(result))
print(json.dumps(result), flush=True)
if mode == 'timeout':
    time.sleep(45)
raise SystemExit(7 if mode == 'nonzero' else 0)
PY
