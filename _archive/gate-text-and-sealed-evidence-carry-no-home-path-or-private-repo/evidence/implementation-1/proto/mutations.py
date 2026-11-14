"""Invalidate the approved mechanisms in disposable source copies; require failures."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

code, root, output = map(Path, sys.argv[1:4])
root.mkdir(parents=True, exist_ok=True)
scripts = code / 'kc-dev-flow-2/scripts'
original = (scripts / 'state_guard.py').read_text()
mutants = {'discard_headers': original.replace("return b'\\n'.join(contents)", 'return data'),
           'discard_inner_headers': original.replace('                contents.append(data)\n', '').replace("return b'\\n'.join(contents)", "return b'\\n'.join([*contents, data])"),
           'replay_only_tip': original.replace('commits = list(dict.fromkeys(commits))', 'commits = list(dict.fromkeys(commits))[-1:]')}
results = []
for name, source in mutants.items():
    target = root / name
    target.mkdir()
    (target / 'state_guard.py').write_text(source)
    shutil.copyfile(scripts / 'test_state_guard.py', target / 'test_state_guard.py')
    shutil.rmtree(target / '__pycache__', ignore_errors=True)
    test = ('test_push_scans_every_commit_even_after_deletion' if name == 'replay_only_tip'
            else 'test_gzip_header_identifiers_refuse_and_clean_gzip_commits')
    p = subprocess.run([sys.executable, '-B', '-m', 'unittest',
                        'test_state_guard.StateGuardTests.' + test],
                       cwd=target, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'), capture_output=True, text=True)
    assert p.returncode == 1, p.stderr
    (output / (name + '.log')).write_text((p.stdout + p.stderr).replace(str(Path.home()), '~'))
    results.append(dict(name=name, expected_failure=True, exit=p.returncode))
text = (code / 'kc-dev-flow-2/skills/validation/principles.md').read_text()
sentence = 'It writes a path under the home directory as `~/…`, an unquoted word of its own, and names no private repository; a retained script takes its paths as arguments rather than holding them, because sealing rewrites the home directory inside it.'
check = root / 'check_rule.py'
check.write_text('import pathlib, sys\nassert ' + repr(sentence) + ' in " ".join(pathlib.Path(sys.argv[1]).read_text().split())\n')
for name, content, expected in (('rule_present', text, 0), ('rule_removed', ' '.join(text.split()).replace(sentence, ''), 1)):
    target = root / (name + '.md')
    target.write_text(content)
    p = subprocess.run([sys.executable, '-B', check, target], capture_output=True, text=True)
    assert p.returncode == expected
    results.append(dict(name=name, expected_exit=expected, exit=p.returncode))
(output / 'mutations.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps(results, indent=2))
