"""Rerun the fixed changed-test set in disposable exports; leave the repository unchanged."""
import argparse
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--repo', type=Path, required=True)
ap.add_argument('--scratch', type=Path, required=True)
args = ap.parse_args()
repo = args.repo.resolve()
scratch = args.scratch.resolve()
scratch.mkdir(parents=True, exist_ok=False)
evidence = Path(__file__).resolve().parent
inventory = json.loads((evidence / 'inventory.json').read_text())
all_results = []
for group in inventory:
    if not group['tests']:
        continue
    pr = group['pr']
    export = scratch / f'pr-{pr}'
    export.mkdir()
    archive = subprocess.check_output(['git', '-C', str(repo), 'archive', group['merge_sha'],
                                       'kc-dev-flow-2', 'docs/adr', '.github/workflows/kc-dev-flow-2-tests.yml'])
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(export, filter='data')
    temp = export / 'run-tmp'
    temp.mkdir()
    ids = [Path(t['path']).stem + '.' + t['test'] for t in group['tests']]
    command = ['python3', '-B', '-m', 'unittest', '-v', *ids]
    run = subprocess.run(command, cwd=export / 'kc-dev-flow-2/scripts', capture_output=True, text=True,
                         env={**os.environ, 'TMPDIR': str(temp), 'PYTHONDONTWRITEBYTECODE': '1'})
    log = (run.stdout + run.stderr).replace(str(scratch), '<scratch>')
    (scratch / f'pr-{pr}-tests.log').write_text(log + f'\nExit: {run.returncode}\n')
    all_results.append(dict(pr=pr, selected=len(ids), exit=run.returncode))
    print(json.dumps(all_results[-1]), flush=True)
    if run.returncode:
        raise SystemExit(run.returncode)
state = scratch / 'blank-question-state'
state.mkdir()
(state / 'demo.md').write_text('---\ntitle: Demo\n---\n')
script = scratch / 'pr-870/kc-dev-flow-2/scripts/task_timeline.py'
probes = []
for label, flags in [('as-written-in-test', []), ('valid-owner-and-holds', ['--holds', 'task', '--by', 'test FO'])]:
    run = subprocess.run(['python3', '-B', str(script), str(state), 'demo', 'ask', '  ', *flags],
                         capture_output=True, text=True)
    probes.append(dict(case=label, exit=run.returncode,
                       stderr=run.stderr.replace(str(scratch), '<scratch>'),
                       record_written=(state / 'demo/asks.jsonl').exists()))
(scratch / 'blank-question-probe.json').write_text(json.dumps(probes, indent=2) + '\n')
(scratch / 'summary.json').write_text(json.dumps(all_results, indent=2) + '\n')
print('Blank question probe saved; compare the two error causes, not just exit codes.')
