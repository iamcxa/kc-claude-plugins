import sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1])/'kc-dev-flow-2/scripts'))
from test_laws_check import Repo, task, laws
with tempfile.TemporaryDirectory(prefix='pr828-repair-') as tmp:
    repo=Repo(Path(tmp)/'state')
    readme=Path(tmp)/'README.md'; readme.write_text('---\nextensions: []\n---\n')
    record=task(body='''## Acceptance criteria
**AC-1** first.
**AC-2** second.
## Captain amendments
### Amendment 1 — 2026-11-10, chat
Captain: replace both criteria
Supersedes: AC-1, AC-2
''')
    before=repo.commit('record',t=record)
    moved=record.replace('**AC-1** first.','**AC-1** Amended by Captain, amendment 1: new first.')+'\nSuperseded text:\n\n**AC-1** first.\n**AC-2** second.\n'
    event=repo.commit('move with two reused ids',t=moved)
    code,text=laws(repo.path,'--before',before,'--after',event,'--readme',readme)
    assert code==1 and 'reused ids: AC-1, AC-2' in text
    repair=repo.commit('fix AC-1 only',t=moved.replace('**AC-1** Amended','**AC-3** Amended'))
    code,text=laws(repo.path,'--before',event,'--after',repair,'--readme',readme)
    print('Partial repair CLI exit:',code)
    print(text, end='')
    if code != 0 or 'violation: L4' in text:
        print('FAIL AC-3: a repair with no new reused id re-reports the existing AC-2 defect')
        raise SystemExit(1)
    print('PASS AC-3: partial repair introduces no new defect')
