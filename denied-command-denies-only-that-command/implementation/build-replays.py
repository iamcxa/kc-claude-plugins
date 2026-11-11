from pathlib import Path
import subprocess,json
out=Path('/tmp/denied-command-evidence'); m=json.loads((out/'pins.json').read_text())
runs=[('release-sol-1',m['release']),('candidate-sol-1',m['candidate']),('candidate-sol-2',m['candidate']),('release-astra-1',m['release']),('candidate-astra-1',m['candidate']),('candidate-astra-2',m['candidate']),('control-sol-1',m['candidate']),('candidate-claude-1',m['candidate']),('candidate-steer-sol-1',m['candidate'])]
for name,ref in runs:
 run='/tmp/denied-replay-'+name
 argv=['python3','-B','/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1/scripts/replay_dispatch.py','build','--run-dir',run,'--package-repo',m['code_repo'],'--package-ref',ref,'--adopter-readme',str(out/'adopter-readme.md'),'--readme-base-ref',m['release'],'--state-repo',m['state_repo'],'--state-commit',m['state_commit'],'--task',m['task'],'--code-repo',m['code_repo'],'--code-commit',m['base'],'--stage','ideation','--checklist',str(out/'checklist.txt'),'--scope',str(out/'scope.txt'),'--spacedock','/Users/kent/.local/bin/spacedock']
 p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True); (out/('build-'+name+'.log')).write_text(p.stdout); print(name,p.returncode,p.stdout.strip(),flush=True)
 if p.returncode: raise SystemExit(p.returncode)
 if 'claude' in name:
  wf=Path(run)/'wf'; q=subprocess.run(['/Users/kent/.local/bin/spacedock','dispatch','build','--host','claude','--workflow-dir',str(wf),'--entity-path',str(wf/'.spacedock-state'/ (m['task']+'.md')),'--stage','ideation','--checklist-file',run+'/checklist.txt','--scope-notes-file',run+'/scope.txt'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
  (out/('host-'+name+'.json')).write_text(q.stdout)
  if q.returncode: raise SystemExit(q.returncode)
  data=json.loads(q.stdout[q.stdout.index('{'):]); Path(run+'/dispatch.md').write_text(Path(data['dispatch_file_path']).read_text())
