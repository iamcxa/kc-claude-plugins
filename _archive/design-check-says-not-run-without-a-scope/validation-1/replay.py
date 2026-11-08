import json
import os
from pathlib import Path
import subprocess
import sys

wt = Path(sys.argv[1])
root = Path(__file__).parent
task = root / 'relay/llms-teaches-versions.md'
candidate = wt / 'kc-dev-flow-2/scripts/design_surfaces.py'
guard = '    elif foreign:\n        return "not run", f"backlog briefing binds {bound.group(2)}, not this task file"\n'
source = candidate.read_text()
assert guard in source
mutant = root / 'replay-mutant.py'
mutant.write_text(source.replace(guard, '', 1))
rows = []
for label, script, expected in [('candidate', candidate, 0), ('base', root / 'base/kc-dev-flow-2/scripts/design_surfaces.py', 1), ('guard removed', mutant, 1)]:
    done = subprocess.run([sys.executable, '-B', str(script), 'check', str(task)], capture_output=True, text=True, env={**os.environ, 'PYTHONPATH': str(candidate.parent), 'PYTHONDONTWRITEBYTECODE': '1'})
    (root / ('relay-' + label.replace(' ', '-') + '.log')).write_text(done.stdout + done.stderr)
    assert done.returncode == expected, (label, done.stdout, done.stderr)
    if label == 'candidate':
        assert done.stdout.splitlines()[:2] == ['llms-teaches-versions.md: design surfaces presentable', 'scope check not run: backlog briefing binds llms-teaches-versions/review/backlog-gate.md, not this task file'], done.stdout
        assert 'Scope changed' not in done.stdout
    else:
        assert 'Scope changed after the backlog gate (01d0e0e4)' in done.stdout, done.stdout
    rows.append({'name': label, 'exit': done.returncode, 'words': len(done.stdout.split()), 'output': done.stdout})
(root / 'replay.json').write_text(json.dumps(rows, indent=2) + '\n')
print('Relay replay: candidate exit 0; base and removed guard exit 1 with the false Scope hold')
