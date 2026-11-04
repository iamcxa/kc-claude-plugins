import datetime,hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
E=Path(__file__).resolve().parent
C=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-claims-name-their-source/.context/validation-777-cycle2')
S=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state')
P=Path('/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0')
H='f79711ca8d6325c1c14781342cf23855dd62b10a'
B='128fe3e3fed70fa64ded8657f5a1b36933af3ced'
records=[]
def run(name,argv,expected=0,cwd=C):
    r=subprocess.run(argv,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
    (E/(name+'.log')).write_text(r.stdout)
    records.append(dict(name=name,argv=argv,cwd=str(cwd),date=datetime.datetime.now(datetime.timezone.utc).isoformat(),exit=r.returncode,expected=expected))
    assert r.returncode==expected,(name,r.stdout)
    return r.stdout
run('adr-lint-dispatch-package',['python3','/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py','docs/adr','--since','origin/main','--require','0055'])
run('number-guards-trunk-diagnostic',['python3',str(P/'scripts/number_guards.py'),'check','--repo',str(C),'--workflow-dir',str(S.parent),'--task',str(S/'claims-name-their-source.md'),'--base','origin/main','--head',H],1)
with tempfile.TemporaryDirectory(dir=C/'.context') as tmp:
    d=Path(tmp)/'adr';shutil.copytree(C/'docs/adr',d)
    next(d.glob('0055-*.md')).unlink()
    run('adr-missing-falsifier',['python3',str(P/'scripts/adr_lint.py'),str(d),'--require','0055'],1)
wf='kc-dev-flow-2/references/sd/workflow.md'
base=subprocess.check_output(['git','-C',str(C),'show',B+':'+wf],text=True)
candidate=(C/wf).read_text()
phrase="Each number or factual claim in a gate summary or PR body names the command that produced it and the date, or the report it repeats as `<whose> report, not run`, and is not stated as settled. In a message to the Captain, a claim carries the same source after the sentence that answers him."
assert candidate.count(phrase)==1
count_check={'expected_raise':55,'observed_raise':len(candidate.split())-len(base.split()),'deleted_rule_raise':len(candidate.replace(phrase,'').split())-len(base.split())}
assert count_check['observed_raise']==55 and count_check['deleted_rule_raise']!=55
(E/'count-falsifier.json').write_text(json.dumps(count_check,indent=2)+'\n')
for label,text in [('base',base),('candidate',candidate)]:
    r=subprocess.run(['wc','-w'],input=text,text=True,capture_output=True,check=True)
    (E/('wc-'+label+'.log')).write_text(r.stdout)
semantic=[]
root=S/'claims-name-their-source/validation'
for folder in ['implementation-2','implementation-3']:
    for answer in sorted((root/folder/'runs').glob('K-*/answer.txt')):
        lines=answer.read_text().splitlines()
        row={'run':answer.parent.name,'path':str(answer),'sha256':hashlib.sha256(answer.read_bytes()).hexdigest(),'target_count_labelled':answer.parent.name in ['K-candidate-claude-1-normal','K-candidate-claude-5-normal','K-candidate-claude-6-normal'],'method':'Independent manual reading of target-count bullet and governing heading, not the preregistered grader'}
        target=next(i for i,x in enumerate(lines) if 'S6' in x)
        row['context']='\n'.join(lines[max(0,target-4):target+3])
        semantic.append(row)
(E/'semantic-read.json').write_text(json.dumps(semantic,indent=2)+'\n')
for number in [777,773]:
    r=subprocess.run(['gh','pr','view',str(number),'--repo','iamcxa/kc-claude-plugins','--json','number,state,headRefOid,baseRefName,isDraft,url,mergeCommit,statusCheckRollup'],text=True,capture_output=True,check=True)
    (E/f'pr-{number}.json').write_text(r.stdout)
dispositions=json.loads((root/'implementation-1/doc-dispositions.json').read_text())
listed=[x.split('\t')[0] for x in (E/'doc-impact.log').read_text().splitlines() if '\t' in x]
assert set(listed)==set(dispositions)
(E/'doc-dispositions.json').write_text(json.dumps(dispositions,indent=2)+'\n')
(E/'extra-checks.json').write_text(json.dumps(records,indent=2)+'\n')
print('ADR deletion, source deletion, document coverage, saved answer reading and provider identities checked.')
