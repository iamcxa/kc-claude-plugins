import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

wt, out = Path(sys.argv[1]).resolve(), Path(__file__).resolve().parent
finalize = sys.argv[2:] == ['--finalize']
head = subprocess.check_output(['git', '-C', str(wt), 'rev-parse', 'HEAD'], text=True).strip()
assert head == (out / 'candidate.txt').read_text().strip()
pkg = wt / 'kc-dev-flow-2'
if not finalize:
    assert not list(pkg.rglob('*.pyc')), 'remove package bytecode caches before running'
paths = sorted(pkg.rglob('test_*.py'))
workflow = (wt / '.github/workflows/kc-dev-flow-2-tests.yml').read_text()
listed = set(re.findall(r'python3 (kc-dev-flow-2/\S*test_\S+\.py)', workflow))
assert {str(path.relative_to(wt)) for path in paths} == listed
env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'SPACEDOCK_BIN': '/Users/kent/.local/bin/spacedock'}
for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_COMMON_DIR'):
    env.pop(key, None)
rows = json.loads((out / 'tests.json').read_text()) if finalize else []
for path in ([] if finalize else paths):
    rel = str(path.relative_to(wt))
    command = [sys.executable, '-B', str(path)]
    if path.name == 'test_sd_dispatch.py':
        command += ['--sd-plugin-root', '/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3']
    log = out / (path.stem + '.log')
    with log.open('w') as stream:
        result = subprocess.run(command, cwd=wt, env=env, stdout=stream, stderr=subprocess.STDOUT)
    text = log.read_text()
    count = re.search(r'Ran (\d+) tests?', text)
    skipped = re.search(r'OK \(skipped=(\d+)\)', text)
    row = {'name': rel, 'status': 'passed' if result.returncode == 0 else 'failed',
           'exit': result.returncode, 'argv': command, 'log': log.name,
           'tests_run': int(count[1]) if count else None, 'skipped': int(skipped[1]) if skipped else 0,
           'candidate': head, 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    if result.returncode:
        row['message'] = text[-6000:]
    rows.append(row)
    (out / 'tests.json').write_text(json.dumps(rows, indent=2) + '\n')
    print(f'{rel}: exit {result.returncode}', flush=True)
assert {r['name'] for r in rows} == listed
for row in rows:
    assert row['candidate'] == head
    assert hashlib.sha256((wt / row['name']).read_bytes()).hexdigest() == row['source_sha256']
generated = list(pkg.rglob('*.pyc'))
for path in generated:
    path.unlink()
assert not list(pkg.rglob('*.pyc'))
summary = {'candidate': head, 'test_files': len(rows), 'failed_files': [r['name'] for r in rows if r['exit']],
           'unittest_cases': sum(r['tests_run'] or 0 for r in rows), 'skipped_cases': sum(r['skipped'] for r in rows),
           'bytecode_absent_at_start_and_exit': True, 'generated_bytecode_removed': [str(p.relative_to(wt)) for p in generated],
           'finalized_existing_receipts': finalize,
           'spacedock': subprocess.check_output(['/Users/kent/.local/bin/spacedock', '--version'], text=True).strip(),
           'sd_plugin_root': '/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3'}
(out / 'tests-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary), flush=True)
sys.exit(bool(summary['failed_files']))
