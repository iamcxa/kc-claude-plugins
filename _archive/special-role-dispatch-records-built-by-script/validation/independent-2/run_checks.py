import json, os, re, shlex, subprocess
from pathlib import Path

root = Path('/tmp/pr827-independent-2/candidate')
out = Path('/tmp/pr827-independent-2/evidence')
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', SPACEDOCK_BIN='/Users/kent/.local/bin/spacedock')
commands = re.findall(r'^        run: (python3 .*)$', (root / '.github/workflows/kc-dev-flow-2-tests.yml').read_text(), re.M)
commands = [c.replace('python3 ', 'python3 -B ', 1).replace('"$GITHUB_WORKSPACE/.sd-plugin-root"', '/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3') for c in commands]
commands.append('python3 -B kc-dev-flow-2/scripts/test_observer_recovery.py')
results = []
for cmd in commands:
    name = Path(shlex.split(cmd)[2]).stem
    log = out / (name + '.log')
    with log.open('w') as stream:
        p = subprocess.run(shlex.split(cmd), cwd=root, env=env, stdout=stream, stderr=subprocess.STDOUT)
    text = log.read_text()
    count = re.search(r'Ran (\d+) tests?', text)
    skips = re.search(r'skipped=(\d+)', text)
    row = dict(name=cmd, status='passed' if p.returncode == 0 else 'failed', exit=p.returncode, file=str(log), cases=int(count[1]) if count else 0, skipped=int(skips[1]) if skips else 0)
    results.append(row)
    (out / 'checks.json').write_text(json.dumps(results, indent=2) + '\n')
    print(name, p.returncode, flush=True)
