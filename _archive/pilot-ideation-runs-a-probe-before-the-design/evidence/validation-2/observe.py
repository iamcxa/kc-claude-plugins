from pathlib import Path
import subprocess,time,json,datetime
s=Path(__file__).parent; f=s/'live/wf/.spacedock-state/pr-watch-tasks-foreign-worktree.md'
for n in range(120):
 refs=subprocess.check_output(['git','-C',str(s/'code.git'),'for-each-ref','--format=%(refname) %(objectname)','refs/heads/poc/pr-watch-tasks-foreign-worktree'],text=True).splitlines()
 row=dict(observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),design_present='\n## Design\n' in f.read_text(),refs=refs)
 newer=[r for r in refs if not r.endswith(('fea415791256e5048bd3df11bb3ffe4490c3d927','88f86f2749dadb6f4ef0cf9aa089c1827096865b'))]
 if newer:
  row['new_probe_refs']=newer
  (s/'evidence/live-midrun-observation.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row),flush=True);break
 if row['design_present']:
  (s/'evidence/live-midrun-observation.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row),flush=True);break
 time.sleep(5)
else:print('Observation timeout; no claim.',flush=True)

