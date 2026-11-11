from pathlib import Path
import subprocess, shlex, os, re, json, sys, time
root=Path('/tmp/story-release-validation-2/candidate')
out=root.parent
commands=[m[1] for line in (root/'.github/workflows/kc-dev-flow-2-tests.yml').read_text().splitlines() if (m:=re.match(r'\s+run: (.*python3 kc-dev-flow-2/.*)',line))]
assert len(commands)==28
results=[]
for n,cmd in enumerate(commands,1):
    argv=shlex.split(cmd); env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','GITHUB_WORKSPACE':str(root)}
    if argv[0].startswith('SPACEDOCK_BIN='):
        env['SPACEDOCK_BIN']='/Users/kent/.local/bin/spacedock'; argv=argv[1:]
    argv=[a.replace('$GITHUB_WORKSPACE',str(root)) for a in argv]
    log=out/f'matrix-{n:02d}-{Path(argv[1]).stem}.log'
    with log.open('w') as f:
        try: code=subprocess.run(argv,cwd=root,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=900).returncode
        except subprocess.TimeoutExpired: code=124
    results.append({'name':Path(argv[1]).name,'command':cmd,'argv':argv,'exit':code,'status':'passed' if code==0 else 'failed','log':log.name})
    (out/'dev2-matrix.json').write_text(json.dumps(results,indent=2)+'\n')
    print(f'{n}/28 {Path(argv[1]).name}: exit {code}',flush=True)
sys.exit(any(r['exit']!=0 for r in results))
