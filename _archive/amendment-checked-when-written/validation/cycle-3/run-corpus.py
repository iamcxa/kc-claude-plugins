import json
from pathlib import Path
import subprocess
import sys

wt = Path(sys.argv[1]).resolve()
inputs = Path(sys.argv[2]).resolve()
name = sys.argv[3]
out = inputs.parent
row = next(r for r in json.loads(inputs.read_text()) if r['name'] == name)
candidate = subprocess.check_output(['git', '-C', '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-amendment-checked-when-written', 'rev-parse', 'HEAD'], text=True).strip()
assert candidate == row['candidate'], (candidate, row['candidate'])
argv = [sys.executable, '-B', str(wt / 'kc-dev-flow-2/scripts/laws_check.py'), row['state'],
        '--before', row['before'], '--after', row['after'], '--readme', row['readme']]
with (out / f'corpus-{name}.log').open('w') as log:
    result = subprocess.run(argv, stdout=log, stderr=subprocess.STDOUT)
(out / f'corpus-{name}-exit.json').write_text(json.dumps({**row, 'argv': argv, 'exit': result.returncode}, indent=2) + '\n')
assert result.returncode in (0, 1, 2), result.returncode
print(name, 'full CLI exit', result.returncode)
