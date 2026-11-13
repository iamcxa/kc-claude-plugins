import os
from pathlib import Path
import json,os,re,subprocess,shlex,time
S=Path(__file__).parent
WT=Path(os.environ["PRODUCT_WORKTREE"])
env={**os.environ,'TMPDIR':str(S),'PYTHONDONTWRITEBYTECODE':'1','SPACEDOCK_BIN':os.environ["SPACEDOCK_BIN"]}
rows=[]
for line in (WT/'.github/workflows/kc-dev-flow-2-tests.yml').read_text().splitlines():
 if 'run: ' not in line or 'python3 ' not in line:continue
 cmd=shlex.split(line.split('run: ',1)[1]);cmd=cmd[cmd.index('python3'):]
 if 'kc-dev-flow-2/scripts/test_sd_dispatch.py' in cmd:cmd=['python3','kc-dev-flow-2/scripts/test_sd_dispatch.py','--sd-plugin-root',str(S/'sd-plugin')]
 name=Path(next(x for x in cmd if x.endswith('.py'))).stem
 started=time.time();p=subprocess.run(cmd,cwd=WT,env=env,capture_output=True,text=True);out=p.stdout+p.stderr
 (S/(name+'.log')).write_text(out)
 counts=re.search(r'Ran (\d+) tests? in',out);skips=re.search(r'skipped=(\d+)',out)
 rows.append(dict(name=name,status='passed' if p.returncode==0 else 'failed',command=cmd,exit=p.returncode,output=name+'.log',tests=int(counts[1]) if counts else None,skipped=int(skips[1]) if skips else 0,seconds=round(time.time()-started,2)))
 (S/'ci-tests.json').write_text(json.dumps(rows,indent=2)+'\n')
 print(name,p.returncode,flush=True)
assert all(r['exit']==0 for r in rows),[(r['name'],r['exit']) for r in rows if r['exit']]
