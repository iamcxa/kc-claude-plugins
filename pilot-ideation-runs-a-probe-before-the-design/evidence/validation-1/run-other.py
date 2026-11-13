import os, subprocess, json
from pathlib import Path
s=Path(__file__).parent
pkg=Path('/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0/scripts')
state=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state'); task=state/'pilot-ideation-runs-a-probe-before-the-design'
base='88f86f2749dadb6f4ef0cf9aa089c1827096865b'; head='f0e00d30ce00542b2895f13173bd41075cc8bfd4'
env=dict(os.environ,TMPDIR=str(s/'tmp'),PYTHONDONTWRITEBYTECODE='1',GIT_DIR=str(s/'code.git'),GIT_WORK_TREE=str(s/'candidate'))
rows=[]
commands=[
('adr-lint',['python3','-B',str(pkg/'adr_lint.py'),'docs/adr','--since',base,'--require','0084','--root',str(s/'candidate')]),
('number-guards',['python3','-B',str(pkg/'number_guards.py'),'check','--repo',str(s/'candidate'),'--base',base,'--head',head,'--workflow-dir',str(state.parent),'--task',str(task)+'.md']),
('comment-ratio',['python3','-B',str(pkg/'comment_ratio.py'),base,head,'--workflow-dir',str(state.parent)]),
('dispatch-records',['python3','-B',str(pkg/'dispatch_records.py'),str(task)]),
('design-surfaces',['python3','-B',str(pkg/'design_surfaces.py'),'check',str(task)+'.md']),
('doc-impact',['python3','-B',str(pkg/'doc_impact.py'),base,head,'--repo',str(s/'candidate')]),
]
for name,cmd in commands:
 with (s/'evidence'/f'{name}.log').open('w') as out:
  r=subprocess.run(cmd,env=env,cwd=s/'candidate',stdout=out,stderr=subprocess.STDOUT)
 rows.append(dict(name=name,command=cmd,exit=r.returncode,output=f'{name}.log'))
 print(name,r.returncode,flush=True)
(s/'evidence/other-results.json').write_text(json.dumps(rows,indent=2))
