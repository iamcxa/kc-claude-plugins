import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

wt, out = Path(sys.argv[1]).resolve(), Path(__file__).resolve().parent
head = subprocess.check_output(['git', '-C', str(wt), 'rev-parse', 'HEAD'], text=True).strip()
assert head == (out / 'candidate.txt').read_text().strip()
prior = '72216e2e947e962737a17c6e61ef3800f9d639c4'
old = subprocess.check_output(['git', '-C', str(wt), 'show', prior + ':kc-dev-flow-2/scripts/laws_check.py'])
rows = []
with tempfile.TemporaryDirectory(prefix='amendment-f1-reverted-') as tmp:
    pkg = Path(tmp)
    shutil.copytree(wt / 'kc-dev-flow-2/scripts', pkg / 'scripts', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    (pkg / 'references/sd').mkdir(parents=True)
    shutil.copy(wt / 'kc-dev-flow-2/references/sd/laws.md', pkg / 'references/sd/laws.md')
    (pkg / 'scripts/laws_check.py').write_bytes(old)
    assert not list(pkg.rglob('*.pyc'))
    for n, test in enumerate(('test_partial_repair_adds_no_event', 'test_growth_reports_only_the_added_id',
                              'test_mixed_repair_and_addition_reports_only_the_added_id')):
        argv = [sys.executable, '-B', '-m', 'unittest', 'test_laws_check.L4Test.' + test]
        log = out / f'reverted-f1-{n}.log'
        with log.open('w') as stream:
            result = subprocess.run(argv, cwd=pkg / 'scripts', stdout=stream, stderr=subprocess.STDOUT,
                                    env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        text = log.read_text()
        assert result.returncode == 1 and 'FAIL: ' + test in text and 'ERROR:' not in text, text
        rows.append({'name': 'F1 revert: ' + test, 'status': 'passed', 'expected_exit': 1,
                     'actual_exit': result.returncode, 'log': log.name, 'argv': argv})
    assert not list(pkg.rglob('*.pyc'))
(out / 'reverted-f1.json').write_text(json.dumps({'candidate': head, 'runner_reverted_to': prior,
    'reverted_source_sha256': hashlib.sha256(old).hexdigest(), 'bytecode_absent': True, 'tests': rows}, indent=2) + '\n')
print('All three regressions fail with only the runtime fix reverted; no errors, bytecode absent.')
