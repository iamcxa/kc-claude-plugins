from pathlib import Path
import json,os,subprocess
s=Path('/tmp/dev2/kc-claude-plugins-3042bb224e995ded/pilot-ideation-runs-a-probe-before-the-design/implementation-1')
w=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-pilot-ideation-runs-a-probe-before-the-design')
state=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state')
task=state/'pilot-ideation-runs-a-probe-before-the-design'
head=subprocess.check_output(['git','-C',str(w),'rev-parse','HEAD'],text=True).strip();base='88f86f2749dadb6f4ef0cf9aa089c1827096865b'
env=dict(os.environ,TMPDIR=str(s/'tmp'),PYTHONDONTWRITEBYTECODE='1')
for source,dest,bare in [(w,s/'code.git',True),(state,s/'state',False)]:
    if dest.exists(): continue
    with (s/'out'/(dest.name+'.clone.log')).open('w') as log:
        subprocess.run(['git','clone','--shared',*(['--bare'] if bare else []),str(source),str(dest)],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
env.update(REPO=str(s/'code.git'),CAND=head,BASE=base,STATE=str(s/'state'),SD='/Users/kent/.local/bin/spacedock',SPACEDOCK_BIN='/Users/kent/.local/bin/spacedock',SDROOT='/Users/kent/.claude/plugins/cache/spacedock/spacedock/0.27.3',INPUTS=str(task/'evidence/ideation-1/inputs'))
results=[]
for n in range(1,8):
    ac=f'AC-{n}'; harness=task/('evidence/implementation-1/bin/accept.sh' if n==3 else 'evidence/ideation-1/bin/accept.sh')
    cmd=['bash',str(harness),ac,str(s/'out'/ac)]
    with (s/'out'/f'{ac}.log').open('w') as log: r=subprocess.run(cmd,env=env,cwd=w,stdout=log,stderr=subprocess.STDOUT)
    results.append(dict(name=ac,exit=r.returncode,status='passed' if r.returncode==0 else 'failed',command=cmd,output=f'{ac}.log'))
    (s/'out/check-results.json').write_text(json.dumps(dict(env={k:env[k] for k in ['REPO','CAND','BASE','STATE','SD','SDROOT','INPUTS','TMPDIR','PYTHONDONTWRITEBYTECODE']},results=results),indent=2)+'\n')
    print(ac,r.returncode,flush=True)
