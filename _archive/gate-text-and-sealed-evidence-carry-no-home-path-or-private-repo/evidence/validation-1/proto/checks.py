"""Run the dispatched validation checks and retain scrubbed command receipts."""
import json
import os
from pathlib import Path
import subprocess
import sys

code, package, workflow, task, output = map(lambda v:Path(v).resolve(), sys.argv[1:6])
base = sys.argv[6]
output.mkdir(parents=True, exist_ok=True)
head = subprocess.check_output(['git','-C',str(code),'rev-parse','HEAD'],text=True).strip()
commands = [
 ('role-triggers', [package/'scripts/role_triggers.py', task.parent, task.name]),
 ('adr-lint', [package/'scripts/adr_lint.py', 'docs/adr', '--since', base]),
 ('doc-impact', [package/'scripts/doc_impact.py', base, head]),
 ('comment-ratio', [package/'scripts/comment_ratio.py', base, head, '--workflow-dir', workflow]),
 ('design-surfaces', [package/'scripts/design_surfaces.py', 'check', task.with_suffix('.md')]),
 ('dispatch-records', [package/'scripts/dispatch_records.py', task]),
 ('lint', [code/'kc-dev-flow-2/scripts/lint-skills.py']),
]
results = []
for name, command in commands:
    argv = [sys.executable, '-B', *map(str, command)]
    r = subprocess.run(argv, cwd=code, text=True, capture_output=True, timeout=120)
    clean = lambda s:s.replace(str(Path.home()), '~')
    (output/(name+'.log')).write_text(clean(r.stdout+r.stderr))
    results.append(dict(name=name, exit=r.returncode, command=[clean(s) for s in argv], log=name+'.log'))
    (output/'checks.json').write_text(json.dumps(results, indent=2)+'\n')
    print(f'{name}: exit {r.returncode}', flush=True)
sys.exit(int(any(r['exit'] for r in results)))
