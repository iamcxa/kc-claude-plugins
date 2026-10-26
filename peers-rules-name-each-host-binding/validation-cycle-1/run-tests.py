from pathlib import Path
import concurrent.futures,subprocess,json,time
W=Path('/tmp/peers-validation-730-cycle1');E=Path('/tmp/peers-validation-730-cycle1-evidence')
files=sorted(p.relative_to(W).as_posix() for p in (W/'kc-dev-flow-2').rglob('test_*.py'))
assert len(files)==25,files
def run(f):
 cmd=['python3','-B',f]
 if f.endswith('/test_sd_dispatch.py'):cmd+=['--sd-plugin-root','/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3']
 start=time.monotonic()
 p=subprocess.run(cmd,cwd=W,capture_output=True,text=True,timeout=240)
 log=E/(f.replace('/','_')+'.log');log.write_text(p.stdout+p.stderr)
 result=dict(file=f,command=cmd,exit=p.returncode,seconds=round(time.monotonic()-start,2),log=log.name)
 print(f'{f}: exit {p.returncode}',flush=True)
 return result
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(run,files))
(E/'tests.json').write_text(json.dumps(results,indent=2)+'\n')
assert all(x['exit']==0 for x in results)
print('All 25 test files passed.',flush=True)
