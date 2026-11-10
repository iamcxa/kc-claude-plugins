import json
from pathlib import Path
import subprocess
import sys

wt, out = Path(sys.argv[1]).resolve(), Path(__file__).resolve().parent
head = (out / 'candidate.txt').read_text().strip()
assert subprocess.check_output(['git', '-C', '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-amendment-checked-when-written', 'rev-parse', 'HEAD'], text=True).strip() == head
rows = []
for repo in json.loads((out / 'corpus-inputs.json').read_text()):
    after = subprocess.check_output(['git', '-C', repo['state'], 'rev-parse', 'HEAD'], text=True).strip()
    argv = [sys.executable, '-B', str(wt / 'kc-dev-flow-2/scripts/laws_check.py'), repo['state'],
            '--before', repo['after'], '--after', after, '--readme', repo['readme']]
    with (out / ('tail-' + repo['name'] + '.log')).open('w') as stream:
        result = subprocess.run(argv, stdout=stream, stderr=subprocess.STDOUT)
    text = (out / ('tail-' + repo['name'] + '.log')).read_text()
    lines = [line for line in text.splitlines() if line.startswith(('L4 ', 'violation: L4 '))]
    assert len([line for line in lines if line.startswith('L4 ')]) == 1, lines
    rows.append({'repository': repo['name'], 'candidate': head, 'before': repo['after'], 'after': after,
                 'argv': argv, 'exit': result.returncode, 'L4_lines': lines})
    (out / 'current-tail.json').write_text(json.dumps(rows, indent=2) + '\n')
    print(repo['name'], lines, flush=True)
