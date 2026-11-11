#!/usr/bin/env python3
"""Run unchanged workflow test commands on one exported tree; save every result."""
import json, os, re, shlex, subprocess, sys
from pathlib import Path

tree, scratch, evidence, label = map(Path, sys.argv[1:5])
label = str(label)
workflow = tree / '.github/workflows/kc-dev-flow-2-tests.yml'
commands = re.findall(r'^        run: (.*python3.*)$', workflow.read_text(), re.M)
assert len(commands) == 28, len(commands)
results = []
for index, raw in enumerate(commands, 1):
    native = 'test_dispatch_stage.py' in raw or 'test_sd_dispatch.py' in raw or 'test_observer_recovery.py' in raw
    command = raw[raw.index('python3'):].replace('"$GITHUB_WORKSPACE/.sd-plugin-root"', shlex.quote(str(scratch / 'sd-root')))
    argv = shlex.split(command)
    argv[0] = sys.executable
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', TMPDIR=str(scratch / 'temp'), PATH='/usr/bin:/bin')
    env.pop('SPACEDOCK_BIN', None)
    if native:
        env['PATH'] = str(scratch / 'sd-bin') + ':' + env['PATH']
        env['SPACEDOCK_BIN'] = str(scratch / 'sd-bin/spacedock')
    done = subprocess.run(argv, cwd=tree, env=env, capture_output=True, text=True, timeout=300)
    name = Path(argv[1]).stem
    log = f'{label}-{index:02}-{name}.log'
    (evidence / log).write_text(done.stdout + done.stderr)
    result = {'name':name, 'source_command':raw, 'command':argv, 'cwd':str(tree), 'path':env['PATH'], 'native':native, 'exit':done.returncode, 'status':'passed' if done.returncode == 0 else 'failed', 'log':log}
    results.append(result)
    (evidence / f'{label}-workflow.json').write_text(json.dumps(results, indent=2) + '\n')
    print(f'{label} {index}/28 {name}: {done.returncode}', flush=True)
print('WORKFLOW PASS' if all(r['exit'] == 0 for r in results) else 'WORKFLOW FAIL', flush=True)
sys.exit(any(r['exit'] != 0 for r in results))
