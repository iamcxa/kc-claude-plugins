import json,os,shutil,subprocess
from pathlib import Path
wt=Path('<home>/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-captain-question-outside-a-gate-is-an-open-record');scratch=Path('/tmp/dev2/kc-claude-plugins-3042bb224e995ded/captain-question-outside-a-gate-is-an-open-record/implementation-1')
folder=scratch/'baseline-scripts';shutil.copytree(wt/'kc-dev-flow-2/scripts',folder,ignore=shutil.ignore_patterns('__pycache__'))
(folder/'task_timeline.py').write_bytes(subprocess.check_output(['git','-C',str(wt),'show','1c3e714ff:kc-dev-flow-2/scripts/task_timeline.py']))
state=scratch/'h3-state';state.mkdir()
(state/'demo/dispatch').mkdir(parents=True)
(state/'demo.md').write_text('---\ntitle: demo\nstatus: ideation\n---\n')
(state/'demo/dispatch/ideation-1.md').write_text('record\n')
source=Path('<home>/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/captain-question-outside-a-gate-is-an-open-record/evidence/ideation-1/h3-fixture-asks.jsonl')
shutil.copyfile(source,state/'demo/asks.jsonl')
subprocess.run(['git','init','-q',str(state)],check=True)
subprocess.run(['git','-C',str(state),'add','--all'],check=True)
subprocess.run(['git','-C',str(state),'-c','user.name=Test','-c','user.email=test@example.invalid','-c','core.hooksPath=/dev/null','commit','-qm','dispatch: demo entering ideation'],check=True,env={**os.environ,'GIT_AUTHOR_DATE':'2026-11-13T07:00:00Z','GIT_COMMITTER_DATE':'2026-11-13T07:00:00Z'})
results=[]
for label,script in [('base',folder/'task_timeline.py'),('candidate',wt/'kc-dev-flow-2/scripts/task_timeline.py')]:
 for json_flag in ([],['--json']):
  cmd=['python3','-B',str(script),str(state),'demo',*json_flag]
  run=subprocess.run(cmd,cwd=wt,capture_output=True,text=True)
  name=f'h3-{label}-'+('json' if json_flag else 'text')+'.log'
  (scratch/name).write_text(run.stdout+run.stderr)
  result=dict(label=label,json=bool(json_flag),exit=run.returncode,command=cmd,log=name)
  if json_flag:result['interruptions']=json.loads(run.stdout)['asks_outside_gate']
  results.append(result)
assert results[0]['exit']==1 and results[1]['interruptions']==4,results
assert results[2]['exit']==0 and results[3]['interruptions']==3,results
(scratch/'h3-results.json').write_text(json.dumps(results,indent=2))
print('Same original h3 fixture: base text exit 1, base JSON count 4; candidate text exit 0, candidate JSON count 3')
