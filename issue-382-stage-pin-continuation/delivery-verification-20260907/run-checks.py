"""One-off local PR integration checks; no model calls or publication."""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
WT = ROOT / 'checkout'
LOGS = ROOT / 'evidence'
LOGS.mkdir(exist_ok=False)
def git(*args):
    return subprocess.check_output(['git', '-C', str(WT), *args]).decode().strip()

tree = git('write-tree')
assert tree == '0df1c96914be6ed4222388b5d83b524176f3a488'
assert git('rev-parse', 'HEAD') == '1d4e95e0f38e53b525a0c7c272d0d55f0b37ddd2'
assert git('rev-parse', 'MERGE_HEAD') == '1d5139568122a3af97cbc28333171df3bc2e27be'
assert not git('diff', '--name-only')
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
for key in ('CLAUDE_CONFIG_DIR', 'ANTHROPIC_API_KEY', 'CLAUDE_CODE_OAUTH_TOKEN',
            'REPO_DIR_OVERRIDE', 'CLAUDE_PLUGIN_ROOT', 'CODEX_PLUGIN_ROOT'):
    env.pop(key, None)
checks = [
    ('full-contract', [sys.executable, 'scripts/kc-dev-flow-contract-test.py']),
    ('marketplace', ['bash', 'scripts/marketplace-verify.sh']),
    ('frontmatter', ['bash', 'scripts/skill-frontmatter-lint.sh']),
    ('scoped-ruff', [sys.executable, '-m', 'ruff', 'check', '--select', 'E4,E7,E9,F',
                     'kc-dev-flow/scripts/profile-contract-loader.py',
                     'kc-dev-flow/scripts/profile-contract-loader.test.py']),
    ('diff-check', ['git', 'diff', '--cached', '--check']),
]
results = []
for name, command in checks:
    print('START', name, flush=True)
    start = time.monotonic()
    with (LOGS / (name + '.log')).open('wb') as output:
        process = subprocess.Popen(command, cwd=WT, env=env, stdout=output,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        timed_out = False
        try:
            code = process.wait(timeout=240)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            code = 124
    raw = (LOGS / (name + '.log')).read_bytes()
    result = {'name': name, 'command': command, 'cwd': str(WT), 'exit': code,
              'seconds': time.monotonic() - start, 'timed_out': timed_out,
              'log_sha256': hashlib.sha256(raw).hexdigest()}
    results.append(result)
    (LOGS / (name + '.json')).write_text(json.dumps(result, indent=2) + '\n')
    print('END', name, code, round(result['seconds'], 3), flush=True)
    print(raw.decode(errors='replace')[-1800:], flush=True)
assert git('write-tree') == tree and not git('diff', '--name-only'), 'Tracked bytes changed during tests'
summary = {'main': git('rev-parse', 'HEAD'), 'pr_head': git('rev-parse', 'MERGE_HEAD'),
           'integration_tree': tree, 'model_calls': 0, 'ci_modified': False,
           'hosted_cost_per_pr': 'not measured', 'checks': results,
           'tracked_bytes_unchanged': True}
(LOGS / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
sys.exit(0 if all(row['exit'] == 0 for row in results) else 1)
