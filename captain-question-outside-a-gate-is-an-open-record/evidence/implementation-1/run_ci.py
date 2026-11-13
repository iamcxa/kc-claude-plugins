import json,os,re,subprocess,time
from pathlib import Path
wt=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-captain-question-outside-a-gate-is-an-open-record')
scratch=Path('/tmp/dev2/kc-claude-plugins-3042bb224e995ded/captain-question-outside-a-gate-is-an-open-record/implementation-1')
env={**os.environ,'TMPDIR':str(scratch/'tmp'),'SPACEDOCK_BIN':'/Users/kent/.local/bin/spacedock'}
commands=[]
for line in (wt/'.github/workflows/kc-dev-flow-2-tests.yml').read_text().splitlines():
    m=re.search(r'run: (.*python3 .*)',line)
    if not m: continue
    command=m[1]
    command=re.sub(r'^SPACEDOCK_BIN="[^"]+" ', '',command)
    command=command.replace('"$GITHUB_WORKSPACE/.sd-plugin-root"','/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.28.0')
    commands.append(command)
results=[]
for i,command in enumerate(commands,1):
    name=command.split()[2] if command.split()[1]=='-B' else command.split()[1]
    log=scratch/('ci-'+Path(name).stem+'-'+str(i)+'.log')
    start=time.monotonic()
    with log.open('w') as out:
        result=subprocess.run(command,shell=True,cwd=wt,env=env,stdout=out,stderr=subprocess.STDOUT)
    results.append(dict(name=name,status='passed' if result.returncode==0 else 'failed',exit=result.returncode,command=command,log=log.name,seconds=round(time.monotonic()-start,2)))
    (scratch/'ci-results.json').write_text(json.dumps(results,indent=2))
    print(f'{i}/{len(commands)} {name}: exit {result.returncode}',flush=True)
raise SystemExit(any(r['exit'] for r in results))
