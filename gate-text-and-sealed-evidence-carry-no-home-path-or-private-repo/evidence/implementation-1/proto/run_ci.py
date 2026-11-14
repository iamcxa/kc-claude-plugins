"""Run each Python entry listed by this candidate's CI workflow, retaining output."""
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import xml.etree.ElementTree as ET

code, scratch, output = map(Path, sys.argv[1:4])
env = dict(os.environ, SPACEDOCK_BIN=sys.argv[4], PYTHONDONTWRITEBYTECODE='1')
temporary = scratch / 'ci-tmp'
temporary.mkdir(parents=True, exist_ok=True)
env['TMPDIR'] = str(temporary)
workflow = (code / '.github/workflows/kc-dev-flow-2-tests.yml').read_text()
entries = re.findall(r'^\s+run: (.*python3 .*)$', workflow, re.M)
results = []
suite = ET.Element('testsuite', name='CI Python entries')
for index, entry in enumerate(entries, 1):
    raw = entry.replace('$HOME/.local/bin/spacedock', sys.argv[4]).replace('$GITHUB_WORKSPACE/.sd-plugin-root', str(scratch / 'sd-plugin-root'))
    argv = shlex.split(raw)
    call_env = env.copy()
    if argv[0].startswith('SPACEDOCK_BIN='):
        call_env['SPACEDOCK_BIN'] = argv.pop(0).split('=', 1)[1]
    p = subprocess.run(argv, cwd=code, env=call_env, text=True, capture_output=True, timeout=600)
    log = output / ('ci-' + str(index).zfill(2) + '.log')
    log.write_text((p.stdout + p.stderr).replace(str(Path.home()), '~'))
    result = dict(name=entry, status='passed' if p.returncode == 0 else 'failed', exit=p.returncode, log=log.name)
    results.append(result)
    case = ET.SubElement(suite, 'testcase', name=entry)
    if p.returncode:
        ET.SubElement(case, 'failure', message='exit ' + str(p.returncode)).text = log.name
    (output / 'ci.json').write_text(json.dumps(results, indent=2) + '\n')
    print(str(index) + '/' + str(len(entries)) + ' ' + result['status'] + ' ' + entry, flush=True)
suite.set('tests', str(len(results)))
suite.set('failures', str(sum(r['exit'] != 0 for r in results)))
ET.ElementTree(suite).write(output / 'ci.xml', encoding='unicode')
sys.exit(int(any(r['exit'] for r in results)))
