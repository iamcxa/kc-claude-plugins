"""Independently recount the actual base and candidate reading at each affected moment."""
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

worktree, base, output = sys.argv[1:]
root = Path(worktree)
out = Path(output)
files = ['references/sd/workflow.md', 'references/sd/mods/kc-dev-flow-2.md',
         'skills/validation/principles.md', 'skills/evaluate-learning/SKILL.md',
         'scripts/pr_watch.py', 'scripts/design_surfaces.py', 'scripts/lint-skills.py']


def previous(path):
    return subprocess.check_output(['git', '-C', '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-counts-name-the-run-that-produced-them', 'show', base + ':kc-dev-flow-2/' + path], text=True)


rows = []
for path in files:
    before, after = previous(path), (root / 'kc-dev-flow-2' / path).read_text()
    rows.append(dict(path=path, before=len(before.split()), after=len(after.split()), identical=before == after))
probe = '''import json,sys
import test_delivery_gate as t
data = {}
for name, result in [('question-zero', t.QuestionTests().ask('Approve it?')), ('question-unchecked', t.QuestionTests().ask('2 tests passed.'))]:
    data[name] = dict(exit=result[0], text=result[1], words=len(result[1].split()))
result=t.run_check()
data['check-zero']=dict(exit=result.code,text=result.out,words=len(result.out.split()))
result=t.run_check(text='2 tests passed.')
data['check-unchecked']=dict(exit=result.code,text=result.out,words=len(result.out.split()))
print(json.dumps(data))'''
observed = {}
for label in ('base', 'candidate'):
    with tempfile.TemporaryDirectory(prefix='counts-words-', dir=root / '.context') as temp:
        scripts = Path(temp) / 'kc-dev-flow-2/scripts'
        shutil.copytree(root / 'kc-dev-flow-2/scripts', scripts, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        if label == 'base':
            for name in ('delivery_gate.py', 'test_delivery_gate.py'):
                (scripts / name).write_text(previous('scripts/' + name))
        done = subprocess.run([sys.executable, '-B', '-c', probe], cwd=scripts, capture_output=True, text=True, check=True)
        observed[label] = json.loads(done.stdout)
        for name, data in observed[label].items():
            (out / (label + '-' + name + '.log')).write_text(data['text'])
            assert data['exit'] == 0, data
print(json.dumps(dict(script='words.py', script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                     run=datetime.datetime.now(datetime.timezone.utc).isoformat(), base=base,
                     candidate='90f43f801be3d03ebd7d98d1a41ad78801aea54d',
                     files=rows, observed=observed), indent=2))
