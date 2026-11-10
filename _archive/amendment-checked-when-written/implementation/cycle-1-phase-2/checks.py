import json
from pathlib import Path
import subprocess
import sys

wt, out = Path(sys.argv[1]).resolve(), Path(__file__).resolve().parent
pkg = Path('/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.37.0')
wf = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2')
base = '6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1'
head = (out / 'candidate.txt').read_text().strip()
assert subprocess.check_output(['git', '-C', str(wt), 'rev-parse', 'HEAD'], text=True).strip() == head
checks = {
    'lint': [sys.executable, '-B', str(wt / 'kc-dev-flow-2/scripts/lint-skills.py')],
    'adr-lint': [sys.executable, '-B', str(pkg / 'scripts/adr_lint.py'), 'docs/adr', '--since', base],
    'number-guards': [sys.executable, '-B', str(pkg / 'scripts/number_guards.py'), 'check', '--workflow-dir', str(wf), '--task', str(wf / '.spacedock-state/amendment-checked-when-written.md')],
    'comment-ratio': [sys.executable, '-B', str(pkg / 'scripts/comment_ratio.py'), base, 'HEAD', '--workflow-dir', str(wf)],
    'task-design': [sys.executable, '-B', str(wt / 'kc-dev-flow-2/scripts/design_surfaces.py'), 'check', str(wf / '.spacedock-state/amendment-checked-when-written.md')],
    'role-triggers': [sys.executable, '-B', str(pkg / 'scripts/role_triggers.py'), str(wf / '.spacedock-state'), 'amendment-checked-when-written'],
    'doc-impact': [sys.executable, '-B', str(pkg / 'scripts/doc_impact.py'), base, head],
}
rows = []
for name, argv in checks.items():
    with (out / (name + '.log')).open('w') as stdout, (out / (name + '.err')).open('w') as stderr:
        result = subprocess.run(argv, cwd=wt, stdout=stdout, stderr=stderr)
    rows.append({'name': name, 'argv': argv, 'exit': result.returncode, 'candidate': head})
    print(name, result.returncode, flush=True)
(out / 'checks.json').write_text(json.dumps(rows, indent=2) + '\n')
sys.exit(any(r['exit'] for r in rows))
