import concurrent.futures, json, os, pathlib, re, subprocess, sys, time
root=pathlib.Path(sys.argv[1]); out=pathlib.Path(sys.argv[2])
files=sorted((root/'kc-dev-flow-2').rglob('test_*.py'))
assert len(files)==25,len(files)
def run(p):
 cmd=[sys.executable,'-B',str(p)]
 if p.name == 'test_sd_dispatch.py':
  cmd+=['--sd-plugin-root','/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3']
 start=time.monotonic()
 result=subprocess.run(cmd,cwd=root,capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},timeout=300)
 log=out/(p.stem+'.log');log.write_text(result.stdout+result.stderr)
 match=re.search(r'Ran (\d+) tests?',result.stderr)
 row={'file':str(p.relative_to(root)),'command':cmd,'exit':result.returncode,'seconds':round(time.monotonic()-start,2),'tests':int(match[1]) if match else None,'log':log.name}
 print(json.dumps(row),flush=True)
 return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: rows=list(pool.map(run,files))
(out/'all-tests.json').write_text(json.dumps(rows,indent=2)+'\n')
print('TOTAL',len(rows),'files',sum(r['tests'] or 0 for r in rows),'unittest cases',flush=True)
assert all(r['exit']==0 for r in rows),rows

