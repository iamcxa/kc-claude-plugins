import io,json,re,subprocess,sys,tarfile,tempfile
from pathlib import Path
root=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-model-roster-question-needs-both-families/.context/validation-3/candidate')
state=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state')
base=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-model-roster-question-needs-both-families/.context/validation-3/corpus');base.mkdir()
main=subprocess.check_output(['git','-C',str(root),'rev-parse','origin/main'],text=True).strip()
state_head=subprocess.check_output(['git','-C',str(state),'rev-parse','HEAD'],text=True).strip()
for name,repo,rev,paths in [('main',root,main,['kc-dev-flow-2']),('state',state,state_head,['*.md'])]:
 raw=subprocess.check_output(['git','-C',str(repo),'archive',rev,'--',*paths])
 dest=base/name;dest.mkdir()
 with tarfile.open(fileobj=io.BytesIO(raw)) as archive: archive.extractall(dest,filter='data')
readme=base/'README.md';readme.write_bytes((state.parent/'README.md').read_bytes())
rows=[];changes=[]
for task in sorted((base/'state').rglob('*.md')):
 text=task.read_text()
 if not text.startswith('---\n') or not re.search(r'^status:',text,re.M) or not re.search(r'^title:',text,re.M): continue
 outputs=[]
 for script in (base/'main/kc-dev-flow-2/scripts/dispatch_records.py',root/'kc-dev-flow-2/scripts/dispatch_records.py'):
  done=subprocess.run([sys.executable,'-B',str(script),'--readme',str(readme),str(task)],capture_output=True,text=True,timeout=30)
  outputs.append(dict(exit=done.returncode,stdout=done.stdout,stderr=done.stderr))
 row=dict(task=str(task.relative_to(base/'state')),main=outputs[0],candidate=outputs[1])
 rows.append(row)
 if outputs[0]!=outputs[1]:changes.append(row)
(base/'results.json').write_text(json.dumps(dict(main=main,state=state_head,mode='folder (the changed mode)',tasks=len(rows),changes=changes,rows=rows),indent=2)+'\n')
print(json.dumps(dict(main=main,state=state_head,tasks=len(rows),changed_verdicts=len(changes),evidence=str(base)),indent=2),flush=True)
assert not changes,changes
