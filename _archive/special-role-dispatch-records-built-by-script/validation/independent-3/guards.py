import os, json, subprocess
from pathlib import Path
home=Path('/tmp/pr827-independent-3')
out=home/'evidence'
repo='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-special-role-dispatch-records-built-by-script'
wf='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2'
task='/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/special-role-dispatch-records-built-by-script.md'
base='d8dbfcb1051d7c696aca139ed9ade332ee85abaf'
head='39a76c68836f471fc0c42c18eab12641196860ed'
package='/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.37.0'
gitdir=subprocess.check_output(['git','-C',repo,'rev-parse','--absolute-git-dir'],text=True).strip()
env=dict(os.environ, GIT_DIR=gitdir,GIT_WORK_TREE=str(home/'candidate'),PYTHONDONTWRITEBYTECODE='1')
commands={
'adr-lint':['python3',package+'/scripts/adr_lint.py','docs/adr','--since',base,'--require','0074'],
'adr-lint-prescribed':['python3','/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.37.0/scripts/adr_lint.py','docs/adr','--since',base,'--require','0074'],
'number-guards':['python3',package+'/scripts/number_guards.py','check','--repo',repo,'--workflow-dir',wf,'--task',task,'--base',base,'--head',head],
'design':['python3',package+'/scripts/design_surfaces.py','check',task],
'dispatch-records':['python3',package+'/scripts/dispatch_records.py',task[:-3]],
'comment-ratio':['python3',package+'/scripts/comment_ratio.py',base,head,'--repo',repo,'--workflow-dir',wf],
'doc-impact':['python3',package+'/scripts/doc_impact.py',base,head,'--repo',repo,'--json'],
}
rows=[]
for name,cmd in commands.items():
 p=subprocess.run(cmd,cwd=home/'candidate',env=env,capture_output=True)
 (out/(name+('.json' if name=='doc-impact' else '.log'))).write_bytes(p.stdout+p.stderr)
 rows.append(dict(name=name,command=cmd,exit=p.returncode))
 print(name,p.returncode,flush=True)
(out/'guards.json').write_text(json.dumps(rows,indent=2)+'\n')
