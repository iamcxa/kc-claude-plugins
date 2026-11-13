import os,subprocess,json,sys,shutil
from pathlib import Path
s=Path(__file__).parent
env=dict(os.environ,TMPDIR=str(s/'tmp'),PYTHONDONTWRITEBYTECODE='1')
rows=[]
def run(name,cmd,extra=None):
 with (s/'evidence'/f'{name}.log').open('w') as out:
  p=subprocess.run(cmd,cwd=s/'candidate',env=dict(env,**(extra or {})),stdout=out,stderr=subprocess.STDOUT)
 rows.append(dict(name=name,exit=p.returncode,expected_exit=1,command=cmd,output=f'{name}.log'))
 print(name,p.returncode,flush=True)
cfg=json.loads((s/'evidence/check-results.json').read_text())['env'];cfg['CAND']=cfg['BASE']
run('mutation-AC-1-base-as-candidate',['bash','/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/pilot-ideation-runs-a-probe-before-the-design/evidence/ideation-1/bin/accept.sh','AC-1',str(s/'evidence/mutation-AC-1')],cfg)
# The dispatch suite itself exercises Team-removal and 43 named contract controls; reuse its assert_team at the same candidate.
run('mutation-AC-6-lost-team',['python3','-B','-c',"import sys;sys.path.insert(0,'kc-dev-flow-2/scripts');import test_sd_dispatch as t; text=t.TEMPLATE.read_text();t.assert_team(text.replace(t.TEAM_RULE,'- **Team:** omitted'));print('unexpected accepted')"])
# A real one-dispatch task must not satisfy AC-7's required two-dispatch/timing observation.
run('mutation-AC-7-one-round',['python3','-B','-c',"import sys,json;sys.path.insert(0,'kc-dev-flow-2/scripts');import task_timeline as t;from pathlib import Path;r=t.timeline(Path(sys.argv[1]),'pr-watch-tasks-foreign-worktree');t.show(r);s=r['stages'];print(json.dumps(s));sys.exit(0 if any(x.get('stage')=='ideation' and x.get('dispatches')==2 for x in s) else 1)",str(s/'state.git')])
(s/'evidence/extra-falsifier-results.json').write_text(json.dumps(rows,indent=2))
