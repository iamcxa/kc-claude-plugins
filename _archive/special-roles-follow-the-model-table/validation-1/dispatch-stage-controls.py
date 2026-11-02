from pathlib import Path
import json,subprocess,sys,shutil,importlib.util
WT=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-special-roles-follow-the-model-table/.validation-562b1a87')
E=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-special-roles-follow-the-model-table/.validation-evidence')
root=Path('/private/tmp/dev-flow-2-sd-wkzd78bn')
records=[]
for row in map(json.loads,(root/'commands.jsonl').read_text().splitlines()):
 args=row['argv']
 if 'dispatch' in args and 'build' in args and '--stamp' in args and 'pilot-' in row['cwd']:
  stage=args[args.index('--stage')+1];host=args[args.index('--host')+1];out=json.loads(row['stdout'])
  expected=None if host=='codex' else 'sonnet' if stage=='implementation' else 'opus'
  assert out['model']==expected,(stage,host,out['model']);records.append(row)
  print('AC8',host,stage,'model='+str(out['model']),row['stderr'].strip())
assert len(records)==6
for row in records:
 args=row['argv']
 if args[args.index('--host')+1]!='claude' or args[args.index('--stage')+1]=='implementation':continue
 readme=Path(row['cwd'])/'README.md';original=readme.read_text(); stage=args[args.index('--stage')+1]
 changed=original.replace('    - name: '+stage+'\n      model: opus\n','    - name: '+stage+'\n',1);assert changed!=original
 try:
  readme.write_text(changed)
  args=[a for a in args if a!='--stamp'];r=subprocess.run(args,text=True,capture_output=True)
  assert r.returncode==0,r.stderr
  assert json.loads(r.stdout)['model']=='sonnet';assert 'from defaults' in r.stderr
  print('AC8 remove',stage,'model: opus =>',r.stderr.strip())
 finally:readme.write_text(original)

(E/'dispatch-stage-records.json').write_text(json.dumps(records,indent=2))
