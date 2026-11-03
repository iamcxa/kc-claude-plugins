import concurrent.futures,json,os,re,subprocess,sys,time
from pathlib import Path
root=Path(os.environ['CAPTAIN_STEPS_WORKTREE'])
out=Path(__file__).parent/'suite';out.mkdir(exist_ok=True)
modules=sorted((root/'kc-dev-flow-2/scripts').glob('test_*.py'))
def run(path):
    started=time.monotonic()
    command=[sys.executable,'-B','-m','unittest','discover','-s','kc-dev-flow-2/scripts','-p',path.name]
    p=subprocess.run(command,cwd=root,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=os.environ,timeout=900)
    (out/(path.stem+'.log')).write_text(p.stdout)
    total=re.search(r'Ran (\d+) tests?',p.stdout)
    skipped=re.search(r'OK \(skipped=(\d+)\)',p.stdout)
    return {'name':path.stem,'command':command,'status':'passed' if p.returncode==0 else 'failed','exit':p.returncode,'tests':int(total[1]) if total else 0,'skipped':int(skipped[1]) if skipped else 0,'seconds':round(time.monotonic()-started,3),'log':'suite/'+path.stem+'.log'}
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for result in pool.map(run,modules):
        results.append(result)
        (out.parent/'tests.json').write_text(json.dumps(results,indent=2)+'\n')
        print(result['name'],result['exit'],result['tests'],flush=True)
summary={'tests':sum(r['tests'] for r in results),'skipped':sum(r['skipped'] for r in results),'failed_modules':[r['name'] for r in results if r['exit']],'command_count':len(results)}
(out.parent/'suite-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary),flush=True)
sys.exit(bool(summary['failed_modules']))
