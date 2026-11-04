import hashlib,json,sys
from pathlib import Path
E=Path(__file__).resolve().parent
S=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state')
def inspect(task,followup,answers):
    criteria=task.split('## Acceptance criteria\n',1)[1].split('\n## ',1)[0]
    assert '**AC-8** Amended by Captain, amendment 3:' in criteria
    assert '**AC-7**' not in criteria and '**AC-3**' not in criteria
    assert 'K 情境 3/6 記成已知限制' in criteria
    assert 'Supersedes: AC-7\nSuperseded text:\n**AC-7**' in task
    assert '### Amendment 2 — 2026-11-04' in task
    assert '先對上游 PR 驗、上游合併後再對 main 確認' in task
    assert 'status: backlog' in followup
    assert 'A count or measured number names the command and run that produced it' in followup
    assert '3 of 6 Claude runs' in followup
    assert len(answers)==9
    for row in answers:
        assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()==row['sha256']
    candidate=[r for r in answers if '-candidate-' in r['run']]
    base=[r for r in answers if '-base-' in r['run']]
    assert (sum(x['target_count_labelled'] for x in candidate),len(candidate))==(3,6)
    assert (sum(x['target_count_labelled'] for x in base),len(base))==(0,3)
task=(S/'claims-name-their-source.md').read_text()
followup=(S/'counts-name-the-run-that-produced-them.md').read_text()
answers=json.loads((E/'semantic-read.json').read_text())
inspect(task,followup,answers)
for label,t,f in [('missing follow-up',task,''),('hidden known limit',task.replace('K 情境 3/6 記成已知限制','K 情境全部通過'),followup)]:
    try: inspect(t,f,answers)
    except AssertionError: print(label+': rejected')
    else: raise AssertionError(label+' falsely accepted')
print('Amendments 2 and 3 applied; AC-3 and AC-7 withdrawn; follow-up filed.')
print('Manual target-count reading: candidate 3/6, base 0/3; saved answer hashes match.')
print('This checks the recorded accepted limit; it does not turn the old grader into a valid count test.')
