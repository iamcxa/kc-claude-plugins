import json,subprocess,sys
from pathlib import Path
wt=Path(sys.argv[1]);ev=Path(sys.argv[2]);pkg=Path(sys.argv[3]);state=Path(sys.argv[4])
c=wt/'.validation-3-consumer'; p=wt/'.validation-3-producer';workflow=state.parent;task=state/'release-walk-due-trigger.md'
py=[sys.executable,'-B'];base='origin/main'
checks=[
('lint',c,py+['kc-dev-flow-2/scripts/lint-skills.py']),
('adr',c,py+[str(pkg/'scripts/adr_lint.py'),'docs/adr','--since',base,'--require','0056']),
('adr-dispatch-path',c,py+['/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0/scripts/adr_lint.py','docs/adr','--since',base,'--require','0056']),
('numbers-main',c,py+[str(pkg/'scripts/number_guards.py'),'check','--repo',str(c),'--workflow-dir',str(workflow),'--task',str(task),'--base',base]),
('comments',c,py+[str(pkg/'scripts/comment_ratio.py'),base,'HEAD','--workflow-dir',str(workflow)]),
('doc-impact',c,py+[str(pkg/'scripts/doc_impact.py'),base,'HEAD']),
('design-surfaces',c,py+[str(pkg/'scripts/design_surfaces.py'),'check',str(task)]),
('dispatch',c,py+[str(pkg/'scripts/dispatch_records.py'),str(state/'release-walk-due-trigger')]),
('diff-check',c,['git','-C',str(c),'diff','--check',base+'...HEAD']),
('scope-main',c,['git','-C',str(c),'diff','--name-only',base+'...HEAD']),
('producer-adr',p,py+[str(pkg/'scripts/adr_lint.py'),'docs/adr','--since',base]),
('producer-comments',p,py+[str(pkg/'scripts/comment_ratio.py'),base,'HEAD','--workflow-dir',str(workflow)]),
('producer-doc-impact',p,py+[str(pkg/'scripts/doc_impact.py'),base,'HEAD']),
('producer-diff-check',p,['git','-C',str(p),'diff','--check',base+'...HEAD']),
('producer-scope',p,['git','-C',str(p),'diff','--name-only',base+'...HEAD']),
]
results=[]
for name,cwd,cmd in checks:
 r=subprocess.run(cmd,cwd=cwd,text=True,capture_output=True)
 (ev/(name+'.log')).write_text(r.stdout+r.stderr)
 results.append(dict(name=name,command=cmd,cwd=str(cwd),exit=r.returncode,log=name+'.log'))
 print(name,r.returncode,flush=True)
(ev/'checks.json').write_text(json.dumps(results,indent=2))
