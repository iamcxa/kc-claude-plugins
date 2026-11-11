from pathlib import Path
import subprocess,os,json,time
out=Path('/tmp/story-release-validation-2')
while True:
    try: ready=len(json.loads((out/'dev2-matrix.json').read_text()))==28
    except (ValueError,FileNotFoundError): ready=False
    if ready: break
    time.sleep(5)
print('all workflow commands ended; starting final independent native checks',flush=True)
env={**os.environ,'EVIDENCE_ROOT':str(out),'PRODUCT_WT':str(out/'candidate'),'DEV2_WT':str(out/'candidate'),'PYTHONDONTWRITEBYTECODE':'1'}
rows=[]
for name,cmd,budget in [('progress-final',['python3','-B',str(out/'scripts/replay_progress.py')],400),('falsifiers-final',['python3','-B',str(out/'scripts/replay_falsifiers.py')],180),('acceptance-final',['bash','--noprofile','--norc',str(out/'acceptance.sh')],300)]:
    started=time.monotonic()
    with (out/(name+'.log')).open('w') as f:
        try: code=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=budget).returncode
        except subprocess.TimeoutExpired: code=124;f.write('\nRunner exceeded declared timeout.\n')
    rows.append({'name':name,'command':cmd,'exit':code,'seconds':round(time.monotonic()-started,3),'log':name+'.log'})
    (out/'final-native-results.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(f'{name}: exit {code}',flush=True)
raise SystemExit(any(r['exit'] for r in rows))
