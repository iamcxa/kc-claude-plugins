import json, os, sys, tempfile
from pathlib import Path
root=Path(sys.argv[1]);out=Path('/tmp/budget-worth-repair');out.mkdir(parents=True,exist_ok=True)
os.environ.update(SPACEDOCK_BIN='/Users/kent/.local/bin/spacedock',PYTHONDONTWRITEBYTECODE='1')
sys.path.insert(0,str(root/'kc-dev-flow-2/scripts'))
import design_surfaces as ds
import test_design_surfaces as t
rows=[]
for name,klass,kwargs in [('security',t.SecurityReviewTests,dict(review='',report=None)),('ui-design',t.DesignReviewTests,dict(review='',report=None)),('built-screen',t.BuiltScreenTests,dict(lines=''))]:
    case=klass('runTest');plain=kwargs.copy();plain['status']='validation' if name=='built-screen' else 'ideation';comment=plain.copy();comment['status']+=' # note'
    a,_=case.run_check(**plain);b,_=case.run_check(**comment)
    rows.append(dict(name=name,plain_errors=a,comment_errors=b))
with tempfile.TemporaryDirectory() as tmp:
    p=Path(tmp)/'task.md';p.write_text('---\nstatus: implementation\n---\n<!--\n## FO alignment\nSurfaces: none\nVisible change: none\n-->\n## Acceptance criteria\n**AC-1** result\n')
    rows.append(dict(name='hidden-FO',errors=ds.check_task(p)))
    p.write_text('---\nstatus: implementation\n---\n## FO alignment\nSurfaces: none\nVisible change: none\n<!--\n## Acceptance criteria\n**AC-1** result\n-->\n')
    rows.append(dict(name='hidden-AC',errors=ds.check_task(p)))
    p.write_text('---\nstatus: ideation # note\n---\n');rows.append(dict(name='scope-comment',result=ds.scope_hold(p)))
    seeds='## Scope\nNon-goals: migrations\nBudget: one cycle per stage\nStop condition: upstream\n'
    rows.append(dict(name='hidden-seed-closed',errors=ds.check_seed_fields('task.md','<!--\n'+seeds+'-->\n')))
    rows.append(dict(name='hidden-seed-unclosed',errors=ds.check_seed_fields('task.md','<!--\n'+seeds)))
    entries,_=ds.parse_amendments('<!--\n## Captain amendments\n### Amendment 1 — 2026-11-11, chat\nCaptain: 「yes」\nSupersedes: none\n-->'.splitlines())
    rows.append(dict(name='hidden-amendment',count=len(entries)))
assert json.loads(json.dumps(rows))==json.loads((out/'sibling-probes.json').read_text()),'an unowned sibling observation changed'
(out/'sibling-probes-after.json').write_text(json.dumps(rows,indent=2)+'\n')
print('PASS: 9 sibling observations unchanged; defects reported rather than repaired')
