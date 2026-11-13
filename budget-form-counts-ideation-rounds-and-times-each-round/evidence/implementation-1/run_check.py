import json, os, shlex, subprocess, sys
from pathlib import Path
x=Path(__file__).parent
out=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/budget-form-counts-ideation-rounds-and-times-each-round/evidence/implementation-1')
name=sys.argv[1]; cmd=sys.argv[2:]
env={**os.environ,'TMPDIR':str(x/'tmp'),'PYTHONDONTWRITEBYTECODE':'1','SPACEDOCK_BIN':'/Users/kent/.local/bin/spacedock'}
roots=Path('/tmp/dev2')
before={p.resolve() for p in roots.glob('*/*/*/.owner.json')} if 'dispatch' in name else set()
with (out/(name+'.txt')).open('w') as log:
    run=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT)
after={p.resolve() for p in roots.glob('*/*/*/.owner.json')} if 'dispatch' in name else set()
left=sorted(str(p.parent) for p in after-before if not p.is_relative_to(x.resolve()))
row=dict(name=name,command=shlex.join(cmd),exit=run.returncode,output=str(out/(name+'.txt')),fixture_roots_left=left)
with (out/'commands.jsonl').open('a') as f: f.write(json.dumps(row)+'\n')
print(json.dumps(row))
sys.exit(run.returncode)
