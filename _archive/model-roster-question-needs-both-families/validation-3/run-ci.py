import json, os, re, shlex, subprocess, time
from pathlib import Path
root=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-model-roster-question-needs-both-families/.context/validation-3/candidate')
evidence=Path('/tmp/roster-validation-3/ci')
plugin=Path('/tmp/roster-repair-ci/spacedock-4d158a484ec73e184861067f8ed1e20087fdc26a')
source=(root/'.github/workflows/kc-dev-flow-2-tests.yml').read_text()
commands=[]
for command in re.findall(r'^\s+run: (.+)$', source, re.M):
 if 'python3 ' not in command: continue
 command=command.replace('"$GITHUB_WORKSPACE/.sd-plugin-root"',str(plugin)).replace('"$HOME/.local/bin/spacedock"','/Users/kent/.local/bin/spacedock')
 args=shlex.split(command);extra={}
 while args and '=' in args[0] and not args[0].startswith('--'):
  key,value=args.pop(0).split('=',1);extra[key]=value
 assert args[0]=='python3',args
 args.insert(1,'-B')
 commands.append((args,extra))
assert len(commands)==26,len(commands)
results=[]
for index,(args,extra) in enumerate(commands,1):
 name=Path(args[2]).stem
 started=time.time()
 with (evidence/(name+'.log')).open('w') as log:
  run=subprocess.run(args,cwd=root,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',TMPDIR='/tmp',**extra),stdout=log,stderr=subprocess.STDOUT,timeout=900)
 record=dict(script=args[2],command=args,env=extra,exit=run.returncode,seconds=round(time.time()-started,2))
 results.append(record)
 print(json.dumps(dict(index=index,total=len(commands),**record)),flush=True)
 (evidence/'results.json').write_text(json.dumps(results,indent=2)+'\n')
print('SUITE EXIT:',int(any(r['exit'] for r in results)),flush=True)
raise SystemExit(int(any(r['exit'] for r in results)))
