import ast,json,re,subprocess,sys
from pathlib import Path
wt=Path('<home>/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-captain-question-outside-a-gate-is-an-open-record');state=Path('<home>/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state');scratch=Path('/tmp/dev2/kc-claude-plugins-3042bb224e995ded/captain-question-outside-a-gate-is-an-open-record/implementation-1')
source=json.loads((state/'captain-question-outside-a-gate-is-an-open-record/evidence/ideation-1/day-2026-11-13.json').read_text())
written=json.loads((state/'captain-question-outside-a-gate-is-an-open-record/evidence/ideation-1/written.json').read_text())
indices=[3,1,1,2,None,1,None,None,None,1,None,None,1,2]
def quotes(text):
    out=[];depth=0;start=0
    for i,c in enumerate(text):
        if c=='「':
            if depth==0:start=i+1
            depth+=1
        elif c=='」' and depth:
            depth-=1
            if depth==0:out.append((text[start:i],start-1,i+1))
    return out
proof=[]
for i,(old,n) in enumerate(zip(written,indices),1):
    task=old['tasks'][0]
    src=next(e for e in source if e['src']==old['src'] and e['task']==task and (n is None or e.get('n')==n))
    raw=src['question'] if n is not None else src['text']
    if n is not None:
        chunks=quotes(raw)
        question=chunks[0][0] if len(chunks)==1 and chunks[0][1]==0 and chunks[0][2]==len(raw) else raw
        needle=raw
    else:
        tail=raw.partition('answering')[2]
        chunks=quotes(tail)
        assert chunks,(i,raw)
        question=chunks[0][0]
        # Retain the scope/selected-option text attached to the bound question.
        if 'whose stated scope was' in tail:question+='\nStated scope: '+chunks[1][0]
        elif '; the chosen option read' in tail:question+='\nChosen option: '+chunks[1][0]
        needle=chunks[0][0]
    paths=[f'{t}.md' for t in old['tasks']]+[f'_archive/{t}.md' for t in old['tasks']]
    rows=subprocess.check_output(['git','-C',str(state),'log','--reverse','--format=%H %aI','-S',needle,'--',*paths],text=True).splitlines()
    found=None
    for row in rows:
        sha,date=row.split(' ',1)
        for path in paths:
            run=subprocess.run(['git','-C',str(state),'show',f'{sha}:{path}'],capture_output=True,text=True)
            if run.returncode==0 and needle in run.stdout:
                # Both question and the Captain's answer must be present in that record.
                captain=src.get('captain') if n is not None else raw.partition(', answering')[0]
                if (raw in run.stdout) if n is None else (captain in run.stdout):
                    found=(sha,date,path);break
        if found:break
    assert found,(i,task,needle)
    sha,date,path=found
    assert date[:10]=='2026-11-13',(i,date)
    proof.append(dict(replay=f'replay-{i}',tasks=old['tasks'],source_kind=old['src'],amendment=n,source_record=raw,question=question,captain_answer=quotes(src.get('captain',raw))[0][0],recorded_answer_commit=sha,recorded_answer_at=date,source_path=path,old_answer_at=old['recorded']))
(scratch/'fixture-reconciliation.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2))
for row in proof:print(row['replay'],row['recorded_answer_at'],len(row['question']),row['recorded_answer_commit'][:9],row['source_path'])
