import concurrent.futures
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

root = Path(sys.argv[1])
out = Path(__file__).parent
workflow = (root / '.github/workflows/kc-dev-flow-2-tests.yml').read_text()
files = re.findall(r'run: python3 (kc-dev-flow-2/[^\s]+\.py)', workflow)
files += ['kc-dev-flow-2/scripts/test_observer_recovery.py']
files = [f for f in files if Path(f).name.startswith('test_')]
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', SPACEDOCK_BIN='/Users/kent/.local/bin/spacedock')

def run(file):
    command = [sys.executable, '-B', file]
    if file.endswith('test_sd_dispatch.py'):
        command += ['--sd-plugin-root', '/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3']
    log = out / (Path(file).parent.name + '-' + Path(file).stem + '.log')
    start = time.monotonic()
    with log.open('w') as sink:
        result = subprocess.run(command, cwd=root, env=env, stdout=sink, stderr=subprocess.STDOUT)
    content = log.read_text()
    counts = re.findall(r'Ran (\d+) tests? in', content)
    return dict(file=file, command=command, exit=result.returncode, seconds=time.monotonic()-start,
                tests=int(counts[-1]) if counts else None, log=str(log))

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(run, files))
(out / 'suite.json').write_text(json.dumps(results, indent=2))
report = ET.Element('testsuite', name='kc-dev-flow-2 package checks', tests=str(len(results)),
                    failures=str(sum(r['exit'] != 0 for r in results)))
for result in results:
    case = ET.SubElement(report, 'testcase', name=result['file'], time=str(result['seconds']))
    if result['exit']:
        ET.SubElement(case, 'failure', message=f"exit {result['exit']}").text = Path(result['log']).read_text()
ET.ElementTree(report).write(out / 'suite.xml', encoding='unicode')
print(json.dumps(dict(commands=len(results), failures=sum(r['exit'] != 0 for r in results),
                      unittest_cases=sum(r['tests'] or 0 for r in results))))
sys.exit(any(r['exit'] != 0 for r in results))
