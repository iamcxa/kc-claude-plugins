from pathlib import Path
import os,subprocess,json
out=Path('/tmp/story-release-validation-2')
root=out/'node22-candidate/kc-journey-map'
env={**os.environ,'PATH':str(out/'runtimes/node-v22.13.0-darwin-arm64/bin')+os.pathsep+os.environ['PATH']}
results=[]
for name,command in [('install','npm ci'),('doctor','npm run doctor'),('typecheck','npm run typecheck'),('tests','node --test lib/*.test.mjs'),('smoke','bash scripts/canvas-smoke.sh')]:
    log=out/f'node22-{name}.log'
    with log.open('w') as f:
        try:code=subprocess.run(['bash','--noprofile','--norc','-c',command],cwd=root,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=600).returncode
        except subprocess.TimeoutExpired:code=124
    results.append({'name':name,'command':command,'exit':code,'status':'passed' if code==0 else 'failed','log':log.name,'node':'22.13.0'})
    (out/'node22-matrix.json').write_text(json.dumps(results,indent=2)+'\n')
    print(f'{name}: exit {code}',flush=True)
raise SystemExit(any(x['exit'] for x in results))
