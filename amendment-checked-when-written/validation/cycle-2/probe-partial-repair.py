import sys,json,tempfile
from pathlib import Path
out=Path(__file__).resolve().parent
sys.path.insert(0,str(out/'candidate/kc-dev-flow-2/scripts'))
from test_laws_check import Repo, task, laws
with tempfile.TemporaryDirectory(prefix='pr828-partial-repair-') as tmp:
    repo=Repo(Path(tmp)/'state')
    readme=Path(tmp)/'README.md';readme.write_text('---\nextensions: []\n---\n')
    record=task(body='''## Acceptance criteria
**AC-1** first.
**AC-2** second.
## Captain amendments
### Amendment 1 — 2026-11-10, chat
Captain: replace both criteria
Supersedes: AC-1, AC-2
''')
    start=repo.commit('record', t=record)
    moved=record.replace('**AC-1** first.', '**AC-1** Amended by Captain, amendment 1: new first.')+'\nSuperseded text:\n\n**AC-1** first.\n**AC-2** second.\n'
    introduced=repo.commit('move with reused ids',t=moved)
    first=laws(repo.path,'--before',start,'--after',introduced,'--readme',readme)
    repaired=moved.replace('**AC-1** Amended','**AC-3** Amended')
    partial=repo.commit('fix first live id only',t=repaired)
    second=laws(repo.path,'--before',introduced,'--after',partial,'--readme',readme)
    fully=repaired.replace('**AC-2** second.', '**AC-4** second.',1)
    complete=repo.commit('fix remaining id',t=fully)
    third=laws(repo.path,'--before',partial,'--after',complete,'--readme',readme)
    rows=[{'step':n,'exit':r[0],'output':r[1]} for n,r in [('introduced',first),('partial_repair',second),('complete_repair',third)]]
    (out/'partial-repair.json').write_text(json.dumps(rows,indent=2)+'\n')
    for r in rows:print(r['step'],r['exit'],r['output'])
