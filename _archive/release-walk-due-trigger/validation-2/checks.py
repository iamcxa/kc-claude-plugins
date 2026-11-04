import json,os,subprocess,sys
from pathlib import Path
root=Path(sys.argv[1]); ev=Path(sys.argv[2]); c=root/'.validation-2-consumer';p=root/'.validation-2-producer'
pkg=Path('/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.34.0');wf=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2');state=wf/'.spacedock-state';task=state/'release-walk-due-trigger.md';base='606781cbec3f684af5e7f9a74c90026e49c3e0a1'
checks=[]
def run(name,args,cwd=c):
 r=subprocess.run(list(map(str,args)),cwd=cwd,capture_output=True,text=True)
 (ev/(name+'.log')).write_text(r.stdout+r.stderr)
 checks.append({'name':name,'command':list(map(str,args)),'cwd':str(cwd),'exit':r.returncode,'log':name+'.log'})
 (ev/'checks.json').write_text(json.dumps(checks,indent=2))
 print(name,r.returncode,flush=True)
py=[sys.executable,'-B']
run('lint',py+['kc-dev-flow-2/scripts/lint-skills.py'])
run('adr',py+[pkg/'scripts/adr_lint.py','docs/adr','--since',base,'--require','0056'])
run('adr-literal-main',py+[pkg/'scripts/adr_lint.py','docs/adr','--since','origin/main','--require','0056'])
run('numbers-stacked',py+[pkg/'scripts/number_guards.py','check','--repo',c,'--workflow-dir',wf,'--task',task,'--base',base])
run('numbers-literal-main',py+[pkg/'scripts/number_guards.py','check','--repo',c,'--workflow-dir',wf,'--task',task,'--base','origin/main'])
run('comments',py+[pkg/'scripts/comment_ratio.py',base,'HEAD','--workflow-dir',wf])
run('doc-impact',py+[pkg/'scripts/doc_impact.py',base,'HEAD'])
run('design-surfaces',py+[pkg/'scripts/design_surfaces.py','check',task])
run('dispatch',py+[pkg/'scripts/dispatch_records.py',state/'release-walk-due-trigger'])
run('diff-check',['git','-C',c,'diff','--check',base,'HEAD'])
run('scope-stacked',['git','-C',c,'diff','--name-only',base,'HEAD'])
run('scope-main',['git','-C',c,'diff','--name-only','origin/main...HEAD'])
run('producer-adr',py+[pkg/'scripts/adr_lint.py','docs/adr','--since','origin/main'],p)
run('producer-comments',py+[pkg/'scripts/comment_ratio.py','origin/main','HEAD','--workflow-dir',wf],p)
run('producer-doc-impact',py+[pkg/'scripts/doc_impact.py','origin/main','HEAD'],p)
run('producer-diff-check',['git','-C',p,'diff','--check','origin/main...HEAD'],p)
run('producer-scope',['git','-C',p,'diff','--name-only','origin/main...HEAD'],p)
