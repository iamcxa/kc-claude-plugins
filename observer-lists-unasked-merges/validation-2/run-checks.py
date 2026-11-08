import json, os, pathlib, re, subprocess, time
ROOT=pathlib.Path('/tmp/observer-validation-a43b537c/candidate')
OUT=ROOT.parent
STATE=pathlib.Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state')
PKG=pathlib.Path('/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0')
WT=pathlib.Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-observer-lists-unasked-merges')
BASE='139feeaee7ce037a0c6535568cd6bd103155cbae'
HEAD='a43b537cd12d69a5ccfde38bf964c6ea35cb0de0'
gitdir=subprocess.check_output(['git','-C',str(WT),'rev-parse','--absolute-git-dir'],text=True).strip()
git_env={**os.environ,'GIT_DIR':gitdir,'GIT_WORK_TREE':str(ROOT),'PYTHONDONTWRITEBYTECODE':'1'}
checks=[
 ('lint',['python3','-B','kc-dev-flow-2/scripts/lint-skills.py']),
 ('adr-lint',['python3','-B',str(PKG/'scripts/adr_lint.py'),'docs/adr','--since',BASE]),
 ('comment-ratio',['python3','-B',str(PKG/'scripts/comment_ratio.py'),BASE,HEAD,'--workflow-dir',str(STATE.parent)]),
 ('number-guards',['python3','-B',str(PKG/'scripts/number_guards.py'),'check','--repo',str(ROOT),'--workflow-dir',str(STATE.parent),'--task',str(STATE/'observer-lists-unasked-merges.md'),'--base',BASE]),
 ('design-check',['python3','-B',str(PKG/'scripts/design_surfaces.py'),'check',str(STATE/'observer-lists-unasked-merges.md')]),
 ('doc-impact',['python3','-B',str(PKG/'scripts/doc_impact.py'),BASE,HEAD,'--json']),
 ('diff-check',['git','-C',str(WT),'diff','--check',BASE,HEAD]),
]
rows=[]
for name,command in checks:
 start=time.monotonic()
 done=subprocess.run(command,cwd=ROOT,env=git_env,capture_output=True,text=True)
 (OUT/(name+('.json' if name=='doc-impact' else '.log'))).write_text(done.stdout+done.stderr)
 rows.append({'name':name,'status':'passed' if done.returncode==0 else 'failed','exit':done.returncode,'command':command,'seconds':time.monotonic()-start})
 print(name,done.returncode,flush=True)
(OUT/'checks.json').write_text(json.dumps(rows,indent=2))
assert all(row['exit']==0 for row in rows)
