from pathlib import Path
import json, os, subprocess
w=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-pilot-ideation-runs-a-probe-before-the-design')
s=Path('/tmp/dev2/kc-claude-plugins-3042bb224e995ded/pilot-ideation-runs-a-probe-before-the-design/implementation-1')
state=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state')
task=state/'pilot-ideation-runs-a-probe-before-the-design'
refs=json.loads((s/'out/refs.json').read_text())
env=dict(os.environ,REPO=str(w),CAND=refs['candidate'],BASE=refs['base'],STATE=str(state),SD='/Users/kent/.local/bin/spacedock',SPACEDOCK_BIN='/Users/kent/.local/bin/spacedock',SDROOT='/Users/kent/.claude/plugins/cache/spacedock/spacedock/0.27.3',INPUTS=str(task/'evidence/ideation-1/inputs'),TMPDIR=str(s/'tmp'),PYTHONDONTWRITEBYTECODE='1')
results=[]
for n in range(1,8):
    ac=f'AC-{n}'
    cmd=['bash',str(task/'evidence/ideation-1/bin/accept.sh'),ac,str(s/'out'/ac)]
    with (s/'out'/f'{ac}.log').open('w') as log:
        r=subprocess.run(cmd,env=env,cwd=w,stdout=log,stderr=subprocess.STDOUT)
    results.append(dict(name=ac,status='passed' if r.returncode==0 else 'failed',exit=r.returncode,command=cmd,output=f'{ac}.log'))
    (s/'out/accept-results.json').write_text(json.dumps(dict(env={k:env[k] for k in ['REPO','CAND','BASE','STATE','SD','SDROOT','INPUTS','TMPDIR','PYTHONDONTWRITEBYTECODE']},results=results),indent=2)+'\n')
    print(ac,r.returncode,flush=True)
