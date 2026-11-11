import subprocess, os, json
from pathlib import Path
out=Path('/tmp/budget-validation-841/evidence'); root=out.parent/'candidate'
repo='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-budget-overrun-holds-and-findings-meet-non-goals'
workflow='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2'
task=workflow+'/.spacedock-state/budget-overrun-holds-and-findings-meet-non-goals.md'
package='/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1'
base='e8664a72b0f904e5dda3c391d52ab3abaca876b4'; head='5bf7cf78866a2f0f6376c15b59fc400519c5ffeb'
gitdir=subprocess.check_output(['git','-C',repo,'rev-parse','--absolute-git-dir'],text=True).strip()
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
checks=[
('adr',['python3','/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1/scripts/adr_lint.py','docs/adr','--since',base,'--require','0077'],{**env,'GIT_DIR':gitdir,'GIT_WORK_TREE':str(root)}),
('number-guards',['python3',package+'/scripts/number_guards.py','check','--repo',repo,'--workflow-dir',workflow,'--base',base,'--head',head,'--task',task],env),
('comment-ratio',['python3',package+'/scripts/comment_ratio.py',base,head,'--repo',repo,'--workflow-dir',workflow],env),
('doc-impact',['python3',package+'/scripts/doc_impact.py',base,head,'--repo',repo,'--json'],env),
('design-installed',['python3',package+'/scripts/design_surfaces.py','check',task],env),
('design-candidate',['python3',str(root/'kc-dev-flow-2/scripts/design_surfaces.py'),'check',task],env),
('dispatch-records',['python3',package+'/scripts/dispatch_records.py',task[:-3]],env)
]
rows=[]
for name,command,env in checks:
    log=out/(name+('.json' if name=='doc-impact' else '.log'))
    with log.open('w') as f: r=subprocess.run(command,cwd=root,env=env,stdout=f,stderr=subprocess.STDOUT)
    rows.append(dict(name=name,exit=r.returncode,command=command,log=log.name))
    print(name,r.returncode,flush=True)
(out/'required-checks.json').write_text(json.dumps(rows,indent=2)+'\n')
