from pathlib import Path
import hashlib
import json
import shutil
import subprocess

p = Path(__file__).resolve().parent
i = json.loads((p / 'identity.json').read_text())
state = Path(i['state'])
d = Path((p / 'durable-path.txt').read_text().strip())
task = state / 'amendment-checked-when-written.md'
assert subprocess.check_output(['git', '-C', str(state), 'branch', '--show-current'], text=True).strip() == 'spacedock-state/dev2'
assert subprocess.check_output(['git', '-C', i['worktree'], 'rev-parse', 'HEAD'], text=True).strip() == i['candidate']
assert not subprocess.check_output(['git', '-C', i['worktree'], 'status', '--porcelain'], text=True).strip()
assert json.loads((p / 'tests-summary.json').read_text())['failed_files'] == []
assert (p / 'stage-report.md').exists()
original = task.read_bytes()
expected = json.loads((p / 'criterion-move.json').read_text())['task_sha256']
assert hashlib.sha256(original).hexdigest() == expected, 'task changed since validation; re-read before appending'
(p / 'task-before-report.json').write_text(json.dumps({'sha256': expected, 'bytes': len(original), 'lines': len(original.splitlines())}, indent=2) + '\n')
for f in p.iterdir():
    if f.is_file() and f.name not in ('durable-path.txt',):
        shutil.copy2(f, d / f.name)
manifest = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(d.iterdir()) if f.is_file() and f.name != 'manifest.json'}
(d / 'manifest.json').write_text(json.dumps({'candidate': i['candidate'], 'files': manifest}, indent=2) + '\n')
report = (p / 'stage-report.md').read_bytes()
task.write_bytes(original + b'\n' + report)
assert task.read_bytes()[:len(original)] == original
assert task.read_bytes().split(b'---', 2)[:2] == original.split(b'---', 2)[:2]
print('Evidence copied:', len(manifest), 'files; appended', len(report.splitlines()), 'report lines; previous bytes preserved.')
