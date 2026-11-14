from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import hashlib,json,os,re,shlex,subprocess,time
S=Path(__file__).parent;WT=Path(os.environ['PRODUCT_WORKTREE'])
env={**os.environ,'TMPDIR':str(S),'PYTHONDONTWRITEBYTECODE':'1','PATH':str(S/'sd-bin')+os.pathsep+os.environ['PATH'],'SPACEDOCK_BIN':os.environ['SPACEDOCK_BIN']}
candidate=subprocess.check_output(['git','-C',str(WT),'rev-parse','HEAD'],text=True).strip()
assert not subprocess.check_output(['git','-C',str(WT),'status','--porcelain'],text=True)
(S/'ci-runner.pid').write_text(str(os.getpid()))
commands=[];rows=[]
for line in (WT/'.github/workflows/kc-dev-flow-2-tests.yml').read_text().splitlines():
 if 'run: ' not in line or 'python3 ' not in line:continue
 cmd=shlex.split(line.split('run: ',1)[1]);cmd=cmd[cmd.index('python3'):];cmd.insert(1,'-B')
 if 'kc-dev-flow-2/scripts/test_sd_dispatch.py' in cmd:cmd=['python3','kc-dev-flow-2/scripts/test_sd_dispatch.py','--sd-plugin-root',str(S/'sd-plugin')]
 commands.append(cmd)
assert len(commands)==29,len(commands)
def run(index,cmd):
 name=Path(next(x for x in cmd if x.endswith('.py'))).stem
 started=time.monotonic();p=subprocess.run(cmd,cwd=WT,env=env,capture_output=True,text=True);out=p.stdout+p.stderr
 (S/(name+'.log')).write_text(out)
 counts=re.findall(r'Ran (\d+) tests? in',out);skips=re.findall(r'skipped=(\d+)',out)
 return dict(index=index,name=name,status='passed' if p.returncode==0 else 'failed',candidate=candidate,command=cmd,exit=p.returncode,output=name+'.log',tests=int(counts[-1]) if counts else None,skipped=int(skips[-1]) if skips else 0,seconds=round(time.monotonic()-started,2))
def retain(row):
 rows.append(row);rows.sort(key=lambda x:x['index']);(S/'ci-tests-final.json').write_text(json.dumps(rows,indent=2)+'\n');print(row['name'],row['exit'],flush=True)
# Independent Python suites use separate temporary fixtures; native transport suites stay ordered.
with ThreadPoolExecutor(max_workers=4) as pool:
 for future in as_completed([pool.submit(run,i,c) for i,c in enumerate(commands[:-3])]):retain(future.result())
for i,cmd in enumerate(commands[-3:],start=26):retain(run(i,cmd))
assert subprocess.check_output(['git','-C',str(WT),'rev-parse','HEAD'],text=True).strip()==candidate
assert not subprocess.check_output(['git','-C',str(WT),'status','--porcelain'],text=True)
assert all(r['exit']==0 for r in rows),[(r['name'],r['exit']) for r in rows if r['exit']]
