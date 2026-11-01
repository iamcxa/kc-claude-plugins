from pathlib import Path
import subprocess,json
root=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-model-roster-per-repo/.validation3-candidate')
pkg=Path('/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.1')
workflow='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2'
state=Path(workflow)/'.spacedock-state';task=state/'model-roster-per-repo.md';out=Path('/tmp/model-roster-validation3')
base='9b32877f4b98583fa41ce090664f20b3ffcae122';head='cf8e5848654f03fa5c509751298e2f75d7c151ba'
commands=[('adr_lint.py',['docs/adr','--since',base]),('adr_lint.py',['docs/adr','--since',base,'--require','0047']),('number_guards.py',['check','--workflow-dir',workflow,'--task',str(task)]),('comment_ratio.py',[base,head,'--workflow-dir',workflow]),('design_surfaces.py',['check',str(task)]),('dispatch_records.py',[str(state/'model-roster-per-repo')]),('dispatch_records.py',['--names',str(state/'model-roster-per-repo/dispatch/validation-3.md')]),('doc_impact.py',[base,head])]
results=[]
for name,args in commands:
 cmd=['python3','-B',str(pkg/'scripts'/name),*args];p=subprocess.run(cmd,cwd=root,capture_output=True,text=True,timeout=90)
 results.append(dict(argv=cmd,exit=p.returncode,stdout=p.stdout,stderr=p.stderr));print(name,p.returncode,p.stdout,p.stderr,flush=True)
(out/'guards.json').write_text(json.dumps(results,indent=2)+'\n')
assert all(r['exit']==0 for r in results)
