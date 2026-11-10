import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

wt, out = Path(sys.argv[1]).resolve(), Path(__file__).resolve().parent
head = (out / 'candidate.txt').read_text().strip()
assert subprocess.check_output(['git', '-C', str(wt), 'rev-parse', 'HEAD'], text=True).strip() == head
prior = 'd7502656c765e36ce3d24be8602862ccc2551254'
old = subprocess.check_output(['git', '-C', str(wt), 'show', prior + ':kc-dev-flow-2/scripts/design_surfaces.py'])
with tempfile.TemporaryDirectory(prefix='amendment-f3-reverted-') as tmp:
    pkg = Path(tmp)
    shutil.copytree(wt / 'kc-dev-flow-2/scripts', pkg / 'scripts', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    (pkg / 'references/sd').mkdir(parents=True)
    shutil.copy(wt / 'kc-dev-flow-2/references/sd/laws.md', pkg / 'references/sd/laws.md')
    (pkg / 'scripts/design_surfaces.py').write_bytes(old)
    assert not list(pkg.rglob('*.pyc'))
    argv = [sys.executable, '-B', '-m', 'unittest', 'test_laws_check.L4Test.test_tilde_example_does_not_supply_live_marker']
    with (out / 'reverted-f3-test.log').open('w') as stream:
        result = subprocess.run(argv, cwd=pkg / 'scripts', stdout=stream, stderr=subprocess.STDOUT,
                                env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    text = (out / 'reverted-f3-test.log').read_text()
    assert result.returncode == 1 and 'FAIL: test_tilde_example_does_not_supply_live_marker' in text and 'ERROR:' not in text, text
    assert not list(pkg.rglob('*.pyc'))
(out / 'reverted-f3.json').write_text(json.dumps({'candidate': head, 'reverted_to': prior,
    'reverted_source_sha256': hashlib.sha256(old).hexdigest(), 'bytecode_absent': True,
    'argv': argv, 'expected_exit': 1, 'actual_exit': result.returncode, 'expected_assertion_failure': True,
    'log': 'reverted-f3-test.log'}, indent=2) + '\n')
print('F3 regression fails with only its input-filter repair reverted; assertion failure, no errors, bytecode absent.')
