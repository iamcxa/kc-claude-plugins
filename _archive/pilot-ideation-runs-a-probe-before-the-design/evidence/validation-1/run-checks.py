import os, subprocess, json
from pathlib import Path
s=Path(__file__).parent
state=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state')
task=state/'pilot-ideation-runs-a-probe-before-the-design'
env=dict(os.environ,REPO=str(s/'code.git'),CAND='f0e00d30ce00542b2895f13173bd41075cc8bfd4',BASE='88f86f2749dadb6f4ef0cf9aa089c1827096865b',STATE=str(s/'state.git'),SD='/Users/kent/.local/bin/spacedock',SDROOT='/Users/kent/.claude/plugins/cache/spacedock/spacedock/0.27.3',INPUTS=str(task/'evidence/ideation-1/inputs'),TMPDIR=str(s/'tmp'),PYTHONDONTWRITEBYTECODE='1')
results=[]
def run(name,cmd,cwd=s/'candidate'):
 with (s/'evidence'/f'{name}.log').open('w') as log:
  r=subprocess.run(cmd,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT)
 results.append(dict(name=name,command=cmd,exit=r.returncode,output=f'{name}.log'))
 (s/'evidence/check-results.json').write_text(json.dumps(dict(env={k:env[k] for k in ['REPO','CAND','BASE','STATE','SD','SDROOT','INPUTS','TMPDIR']},results=results),indent=2))
 print(name,r.returncode,flush=True)
for n in range(1,8):
 run(f'AC-{n}',['bash',str(task/'evidence/ideation-1/bin/accept.sh'),f'AC-{n}',str(s/'evidence'/f'AC-{n}')])
run('AC-3-corrected',['bash',str(task/'evidence/implementation-1/bin/accept.sh'),'AC-3',str(s/'evidence/AC-3-corrected')])
run('test-lint',['python3','-B','kc-dev-flow-2/scripts/test_lint_skills.py'])
