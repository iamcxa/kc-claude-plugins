import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

WT = Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-diagnosis-rounds-count-toward-step-back')
OUT = Path('/tmp/opencode/diagnosis-rounds/review-1418')
ROOT = OUT / 'fixture'
env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
       'GIT_CONFIG_SYSTEM': os.devnull, 'GIT_AUTHOR_NAME': 't', 'GIT_AUTHOR_EMAIL': 't@t',
       'GIT_COMMITTER_NAME': 't', 'GIT_COMMITTER_EMAIL': 't@t'}
rows = []


def run(*args, expected=0, cwd=WT):
    command = list(map(str, args))
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True)
    row = {'command': shlex.join(command), 'cwd': str(cwd), 'exit': result.returncode,
           'stdout': result.stdout, 'stderr': result.stderr}
    rows.append(row)
    print('$ ' + row['command'])
    print(f'exit={result.returncode}')
    print(result.stdout, end='')
    print(result.stderr, end='')
    assert result.returncode == expected, row
    return result


ROOT.mkdir(exist_ok=False)
run('git', '--version')
run('git', '-C', ROOT, 'init', '-q', '-b', 'main')
archive = ROOT / '_archive/task'
(archive / 'dispatch').mkdir(parents=True)
(archive / 'index.md').write_text('---\nprofile: pilot\n---\n## FO alignment\nSurfaces: none\n')
for number in (2, 3, 4):
    (archive / f'dispatch/implementation-{number}.md').write_text('Dispatched: 2026-11-03\nSymptom: page freeze\n')
run('git', '-C', ROOT, 'add', '_archive')
run('git', '-C', ROOT, 'commit', '-qm', 'archived task')
nested = ROOT / 'nested'
nested.mkdir()
run('git', '-C', ROOT, 'mv', '_archive', 'nested/_archive')
run('git', '-C', ROOT, 'commit', '-qm', 'nested state')
run('git', '-C', nested, 'rev-parse', '--show-prefix')
run('git', '-C', nested, 'show', 'HEAD:./_archive/task/index.md')
run('git', '-C', nested, 'cat-file', '-e', 'HEAD:./_archive/task/index.md')
paths = run('git', '-C', nested, 'ls-tree', '-r', '--name-only', 'HEAD', '--', '_archive/task/dispatch/')
assert len(paths.stdout.splitlines()) == 3
for path in paths.stdout.splitlines():
    run('git', '-C', nested, 'show', f'HEAD:./{path}')
result = run(sys.executable, '-B', WT / 'kc-dev-flow-2/scripts/role_triggers.py', nested, 'task', expected=1)
assert '3 implementation dispatches on symptom "page freeze"' in result.stdout
run('git', '-C', nested, 'show', 'HEAD:_archive/task/index.md', expected=128)

mutant = OUT / 'mutant/kc-dev-flow-2/scripts'
mutant.mkdir(parents=True)
for name in ('role_triggers.py', 'test_role_triggers.py'):
    shutil.copyfile(WT / 'kc-dev-flow-2/scripts' / name, mutant / name)
path = mutant / 'role_triggers.py'
text = path.read_text()
assert text.count('f"{rev}:./{path}"') == 3
path.write_text(text.replace('f"{rev}:./{path}"', 'f"{rev}:{path}"'))
for cache in mutant.rglob('__pycache__'):
    shutil.rmtree(cache)
result = run(sys.executable, '-B', '-m', 'unittest', '-v',
             'test_role_triggers.SymptomRoundsTest.test_archived_folder_records_and_nested_state_checkout',
             expected=1, cwd=mutant)
assert 'FAILED (failures=1)' in result.stderr
(OUT / 'reproduction.json').write_text(json.dumps(rows, indent=2))
(OUT / 'tests.json').write_text(json.dumps([
    {'name': 'Original nested-checkout regression', 'status': 'passed', 'message': 'Unchanged candidate test passes'},
    {'name': 'Direct nested show, cat-file, ls-tree and role checker', 'status': 'passed', 'message': 'All reads succeed; three dispatches owe chief-engineer'},
    {'name': 'Remove ./ from revision paths', 'status': 'passed', 'message': 'Mutated nested test fails with exit 2 instead of 1'}
], indent=2))
print('Finding 1418 not reproduced; removing ./ produces the claimed failure and is caught by the existing test.')
