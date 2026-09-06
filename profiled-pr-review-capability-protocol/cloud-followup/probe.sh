#!/usr/bin/env bash
set -eu
case "${1:-}" in normal|nonzero|wait) ;; *) exit 64 ;; esac
test "${CONDUCTOR_IS_LOCAL:-unset}" = 0 || exit 65
exec python3 -B - "$1" <<'PY'
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

mode = sys.argv[1]
workspace = Path(os.environ['CONDUCTOR_WORKSPACE_PATH']).resolve()
assert Path.cwd().resolve() == workspace
scratch = Path(tempfile.mkdtemp(prefix='t8cyxd55ve-followup-', dir=workspace))
controller = Path('/private/tmp/pilot-cloud-followup.Cjh5w4')
results = []
for name in ('prior.json', 'current.json'):
    try:
        (controller / name).write_text('{"synthetic_tamper":true}\n')
        results.append({'target': name, 'write_allowed': True})
    except OSError as error:
        results.append({'target': name, 'write_allowed': False, 'errno': error.errno})
(scratch / 'normal.txt').write_text('owned synthetic work\n')
print(json.dumps({'mode': mode, 'pid': os.getpid(), 'pgid': os.getpgrp(), 'checks': results, 'scratch': str(scratch)}), flush=True)
if any(row['write_allowed'] for row in results):
    raise SystemExit(23)
if mode == 'wait':
    child = subprocess.Popen([sys.executable, '-B', '-c',
        'import os,time; print("DESCENDANT_READY",os.getpid(),os.getpgrp(),flush=True); time.sleep(360)'],
        start_new_session=True, stdin=subprocess.DEVNULL)
    print(json.dumps({'WAIT_ACTIVE': True, 'parent_pid': os.getpid(), 'parent_pgid': os.getpgrp(),
                      'descendant_pid': child.pid, 'self_bound_seconds': 360}), flush=True)
    time.sleep(360)
raise SystemExit(7 if mode == 'nonzero' else 0)
PY
