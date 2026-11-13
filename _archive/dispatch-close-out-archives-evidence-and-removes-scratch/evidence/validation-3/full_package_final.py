"""Run every Python test command in the candidate's kc-dev-flow-2 CI workflow, at most three at once."""
import concurrent.futures,json,os,pathlib,re,subprocess,sys
repo=pathlib.Path(sys.argv[1]).resolve();root=pathlib.Path(sys.argv[2]).resolve();sd=pathlib.Path(sys.argv[3]).resolve()
out=root/'full-package-final';out.mkdir()
workflow=repo/'.github/workflows/kc-dev-flow-2-tests.yml';source=workflow.read_text()
paths=re.findall(r'run:.*?python3(?: -B)? (kc-dev-flow-2/\S*test_\S*\.py)',source)
assert len(paths)==len(set(paths)) and len(paths)>=28
(out/'test-list.json').write_text(json.dumps({'workflow':str(workflow.relative_to(repo)),'commands':paths,'candidate':subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()},indent=1))
env={**os.environ,'TMPDIR':str(root/'tmp').replace('/private/tmp/','/tmp/',1),'SPACEDOCK_BIN':'/Users/kent/.local/bin/spacedock','SD_PLUGIN_ROOT':str(sd),'PYTHONDONTWRITEBYTECODE':'1'}
def execute(path):
 name=path.replace('/','__')[:-3];args=[sys.executable,'-B',str(root/'full_runner_final.py'),str(out/(name+'.json')),str(repo/path)]
 if path.endswith('/test_sd_dispatch.py'):args += ['--sd-plugin-root',str(sd)]
 with (out/(name+'.log')).open('w') as log:
  done=subprocess.run(args,cwd=repo,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=900)
 row={'name':path,'command':args,'exit':done.returncode,'log':name+'.log','results':name+'.json'}
 print(json.dumps({'completed':path,'exit':done.returncode}),flush=True);return row
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 results=list(pool.map(execute,paths))
(out/'commands.json').write_text(json.dumps(results,indent=1))
rows=[]
for r in results:
 data=json.loads((out/r['results']).read_text())
 if data:rows+=data
 else:rows.append({'name':r['name']+' native integration program','status':'passed' if r['exit']==0 else 'failed'})
(out/'tests.json').write_text(json.dumps(rows,indent=1))
print(json.dumps({'commands':len(results),'passed':sum(r['status']=='passed' for r in rows),'failed':sum(r['status']=='failed' for r in rows),'skipped':sum(r['status']=='skipped' for r in rows)}),flush=True)
sys.exit(any(r['exit'] for r in results))
