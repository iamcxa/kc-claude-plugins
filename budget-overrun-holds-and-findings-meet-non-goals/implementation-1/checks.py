import concurrent.futures, json, os, subprocess, sys
from pathlib import Path
root = Path(sys.argv[1]); out = Path('/tmp/budget-implementation')
commands = {name: ['python3', '-B', str(root / 'kc-dev-flow-2/scripts' / ('test_' + name + '.py'))] for name in ['role_triggers', 'design_surfaces', 'dispatch_stage', 'delivery_gate', 'pr_watch']}
commands['lint'] = ['python3', '-B', str(root / 'kc-dev-flow-2/scripts/lint-skills.py')]
commands['adr'] = ['python3', '-B', '/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1/scripts/adr_lint.py', 'docs/adr', '--since', 'e8664a72b0f904e5dda3c391d52ab3abaca876b4', '--require', '0077']
def run(item):
    name, command = item
    log = out / (name + '-final.log')
    with log.open('w') as target:
        result = subprocess.run(command, cwd=root, stdout=target, stderr=subprocess.STDOUT, env={**os.environ, 'SPACEDOCK_BIN': '/Users/kent/.local/bin/spacedock', 'PYTHONDONTWRITEBYTECODE':'1'})
    return dict(name=name, status='passed' if result.returncode == 0 else 'failed', exit=result.returncode, command=command, log=str(log))
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
    results=[]
    for result in pool.map(run, commands.items()):
        results.append(result); print(result['name'], result['exit'], flush=True)
        (out / 'checks.json').write_text(json.dumps(results, indent=2) + '\n')
sys.exit(any(r['exit'] for r in results))
