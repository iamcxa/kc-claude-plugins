from pathlib import Path
import sys, re, json, subprocess
sys.path.insert(0,'/tmp/validate-pr750-b8a66e82/kc-dev-flow-2/scripts')
import test_dispatch_records as t
roots={'dev2':'/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state','relay':'/Users/kent/conductor/workspaces/subspace-relay/beirut-dev2/docs/dev2/.spacedock-state','web':'/Users/kent/conductor/workspaces/subspace-web/dev2-fo/docs/dev2/.spacedock-state','qnow':'/Users/kent/conductor/repos/qnow-adopt-dev2/docs/dev2/.spacedock-state'}
rows=[]
for case in t.SAVED_RULING_CASES:
    root=roots[case['corpus']]; slug=case['task']; rev=case['dispatch_commit']
    paths=[prefix+name for prefix in ('','_archive/') for name in (slug+'.md',slug+'/index.md')]
    def git(*args):
        return subprocess.run(['git','-C',root,*args],capture_output=True,text=True,check=True).stdout
    present=git('ls-tree','-r','--name-only',rev,'--',*paths).splitlines()
    assert len(present)==1
    text=git('show',rev+':'+present[0])
    actual=t.records.open_decisions(t.records.validation_reports(text)[-1])
    saved=t.records.open_decisions(t.records.validation_reports(case['body'])[-1])
    assert actual==saved,(slug,case['record'],actual,saved)
    for amendment in case['amendments']:
        assert amendment.strip() in text,slug
    folder=present[0][:-3] if present[0].endswith(slug+'.md') else present[0][:-9]
    record=git('show',rev+':'+folder+'/dispatch/'+case['record'])
    if 'record_text' in case:
        assert case['record_text']==record,(slug,case['record'])
    report=git('show',case['report_commit']+':'+present[0])
    assert t.records.open_decisions(t.records.validation_reports(report)[-1])==saved
    rows.append({'task':slug,'record':case['record'],'source':rev,'findings':actual,'exact_record_checked':'record_text' in case})
    if case['prototype']=='REFUSE':
        diff=git('diff',case['report_commit'],rev,'--',*paths)
        Path('/tmp/pr750-source-'+slug+'-'+case['record']+'.txt').write_text(record+'\n'+diff)
print(json.dumps(rows,indent=2))
print('PASS: 27 pinned source finding sets and supplied exact dispatch texts match Git snapshots')
