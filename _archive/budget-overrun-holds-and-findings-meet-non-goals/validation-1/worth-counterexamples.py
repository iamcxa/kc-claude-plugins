import json, os, subprocess, sys
from pathlib import Path
root=Path('/tmp/budget-validation-841/candidate');out=root.parent/'evidence'
os.environ['SPACEDOCK_BIN']='/Users/kent/.local/bin/spacedock';os.environ['PYTHONDONTWRITEBYTECODE']='1'
sys.path.insert(0,str(root/'kc-dev-flow-2/scripts'))
import test_dispatch_stage as d
fixture=d.DispatchStageTests('test_budget_line_and_spent_cycles_are_printed_before_build');fixture.setUp()
rows=[]
try:
    original=fixture.entity.read_text()
    design='\n## PRFAQ\nA bounded CLI result.\n\n```mermaid\nflowchart LR\n A[Input] --> B[Result]\n```\n\n## Acceptance criteria\n**AC-1** Bounded result. Evidence: one CLI run.\n'
    for name,status,addition in [('missing','ideation',''),('commented-status','ideation # ready for review',''),('hidden-heading','ideation','<!--\n### Worth questions\n-->\n'),('visible-heading','ideation','### Worth questions\nAsked: bounded result; without: unavailable; premise: needed, test CLI.\n')]:
        text=original.replace('status: ideation','status: '+status)+design.replace('A bounded CLI result.','A bounded CLI result.\n'+addition)
        fixture.entity.write_text(text);fixture.commit_task()
        native=fixture.call(['/Users/kent/.local/bin/spacedock','status','--workflow-dir',fixture.workflow,'--read',fixture.slug,'--json'])
        check=fixture.call([sys.executable,'-B',root/'kc-dev-flow-2/scripts/design_surfaces.py','check',fixture.entity],expected=None)
        rows.append(dict(name=name,text=text,native=json.loads(native.stdout),checker_exit=check.returncode,checker_output=check.stdout+check.stderr))
        print(name,'exit',check.returncode,check.stdout.strip(),flush=True)
    (out/'worth-counterexamples.json').write_text(json.dumps(rows,indent=2)+'\n')
finally:fixture.doCleanups()
