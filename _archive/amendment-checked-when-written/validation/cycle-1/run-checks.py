import os, json, subprocess, sys
from pathlib import Path
out=Path(__file__).resolve().parent
meta=json.loads((out/'identity.json').read_text())
candidate=out/'candidate'
package=Path('/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.37.0')
state=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state')
task=state/'amendment-checked-when-written.md'
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','GIT_DIR':meta['git_dir'],'GIT_WORK_TREE':str(candidate)}
commands={
 'lint':['python3','-B',str(candidate/'kc-dev-flow-2/scripts/lint-skills.py')],
 'adr-lint':['python3','-B',str(package/'scripts/adr_lint.py'),'docs/adr','--since',meta['base']],
 'comment-ratio':['python3','-B',str(package/'scripts/comment_ratio.py'),meta['base'],meta['head'],'--workflow-dir',str(state.parent)],
 'number-guards':['python3','-B',str(package/'scripts/number_guards.py'),'check','--workflow-dir',str(state.parent),'--task',str(task)],
 'doc-impact':['python3','-B',str(package/'scripts/doc_impact.py'),meta['base'],meta['head']],
 'task-design':['python3','-B',str(package/'scripts/design_surfaces.py'),'check',str(task)],
 'dispatch-records':['python3','-B',str(package/'scripts/dispatch_records.py'),str(state/'amendment-checked-when-written')],
 'role-triggers':['python3','-B',str(package/'scripts/role_triggers.py'),str(state),'amendment-checked-when-written'],
}
rows=[]
for name,cmd in commands.items():
    with (out/(name+'.log')).open('w') as log:
        result=subprocess.run(cmd,cwd=candidate,env=env,stdout=log,stderr=subprocess.STDOUT)
    rows.append({'name':name,'argv':cmd,'exit':result.returncode,'log':name+'.log'})
    print(name,result.returncode,flush=True)
(out/'checks.json').write_text(json.dumps(rows,indent=2)+'\n')
