#!/usr/bin/env python3
"""Exercise the real seed subprocess through its only runtime exit-code consumer."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest import mock

parser = argparse.ArgumentParser()
parser.add_argument('--source', type=Path, required=True)
args = parser.parse_args()
scripts = args.source / 'kc-dev-flow-2/scripts'
sys.path.insert(0, str(scripts))
import pr_watch as watch

valid = '''## Scope
Non-goals: unrelated checks
Budget: 1 implementation and 2 validation cycles
Stop condition: task file resolves
## FO alignment
Surfaces: none
Visible change: none
## Design
### Worth questions
Asked: repair the entrance; without: directory crash; premise: bare names fail.
## Acceptance criteria
**AC-1**: task file resolves.
'''
rows = [{'slug': 'sample', 'current': 'backlog', 'readiness': 'needs-preparation'}]
readme = 'stages:\n  states:\n    - name: ideation\n'
actual_run = subprocess.run
results = []
with tempfile.TemporaryDirectory(prefix='consumer-') as temporary:
    task = Path(temporary) / 'sample.md'
    for name in ('valid', 'invalid-fields', 'invalid-encoding', 'missing', 'removed-after-read'):
        task.write_text(valid if name != 'invalid-fields' else valid.replace('Budget:', 'No-budget:'))
        if name == 'invalid-encoding':
            task.write_bytes(valid.encode() + b'\xff')
        if name == 'missing':
            task.unlink()
        exits = []
        def run(argv, **kwargs):
            if name == 'removed-after-read':
                task.unlink()
            done = actual_run(argv, **kwargs)
            exits.append(done.returncode)
            return done
        with mock.patch.object(watch.subprocess, 'run', side_effect=run):
            lines, errors = watch.seeds(rows, {'sample': task}, readme)
        if name == 'valid':
            assert exits == [0] and not lines and not errors, (name, exits, lines, errors)
        elif name in ('invalid-fields', 'invalid-encoding'):
            assert exits == [1] and len(lines) == 1 and not errors, (name, exits, lines, errors)
        else:
            assert exits == ([2] if name == 'removed-after-read' else []) and not lines and len(errors) == 1, (name, exits, lines, errors)
            assert 'report sample to the Captain' in errors[0]
        results.append({'name': name, 'status': 'passed', 'subprocess_exits': exits,
                        'seed_refusal_lines': len(lines), 'error_lines': len(errors)})
print(json.dumps(results, indent=2))
