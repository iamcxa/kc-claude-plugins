import concurrent.futures
import json
import os
from pathlib import Path
import re
import subprocess
import time

root = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-validation-gate-requires-the-question-check/.context/validation-767-detached')
out = Path('/tmp/validation-767-evidence')
out.mkdir(exist_ok=True)
workflow = (root / '.github/workflows/kc-dev-flow-2-tests.yml').read_text()
scripts = re.findall(r'run: (?:SPACEDOCK_BIN="[^"\n]+" )?python3 (kc-dev-flow-2/[^\s]+\.py)', workflow)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', SPACEDOCK_BIN='/Users/kent/.local/bin/spacedock')

def run(script):
    command = ['python3', '-B', script]
    if script.endswith('/test_sd_dispatch.py'):
        command += ['--sd-plugin-root', '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-validation-gate-requires-the-question-check/.context/validation-767-detached/.context/sd-pinned']
    start = time.monotonic()
    result = subprocess.run(command, cwd=root, env=env, text=True, capture_output=True, timeout=900)
    log = out / (script.replace('/', '_') + '.log')
    log.write_text(result.stdout + result.stderr)
    record = dict(script=script, command=command, exit=result.returncode, seconds=round(time.monotonic()-start, 2), log=str(log))
    print(json.dumps(record), flush=True)
    return record

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    records = list(pool.map(run, scripts))
(out / 'ci-results.json').write_text(json.dumps(records, indent=2))
print(f'SUMMARY: {sum(r["exit"] == 0 for r in records)}/{len(records)} commands passed', flush=True)
raise SystemExit(any(r['exit'] for r in records))
