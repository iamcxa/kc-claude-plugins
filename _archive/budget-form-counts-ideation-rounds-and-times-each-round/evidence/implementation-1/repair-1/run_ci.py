from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess, os, shlex, json, re, threading
wt=Path.cwd(); x=Path(__file__).parent;ev=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/budget-form-counts-ideation-rounds-and-times-each-round/evidence/implementation-1/repair-1')
commands=[]
for line in (wt/'.github/workflows/kc-dev-flow-2-tests.yml').read_text().splitlines():
 match=re.match(r'\s+run: (.+)$',line)
 if not match:continue
 argv=shlex.split(match[1])
 if argv and argv[0].startswith('SPACEDOCK_BIN='):argv=argv[1:]
 if not argv or argv[0]!='python3':continue
 argv=[str(x/'sd-plugin-root') if part=='$GITHUB_WORKSPACE/.sd-plugin-root' else part for part in argv]
 commands.append(argv)
assert len(commands)==29,len(commands)
commands.sort(key=lambda a:0 if a[-1].endswith('test_dispatch_stage.py') else 1 if a[-1].endswith('test_role_triggers.py') else 2)
(ev/'ci-commands.json').write_text(json.dumps(commands,indent=2)+'\n')
env={**os.environ,'TMPDIR':str(x/'tmp'),'PYTHONDONTWRITEBYTECODE':'1','SPACEDOCK_BIN':'/Users/kent/.local/bin/spacedock'}
lock=threading.Lock()
def run(argv):
 script=next(p for p in argv if p.endswith('.py'));name=script.removeprefix('kc-dev-flow-2/').replace('/','__').removesuffix('.py')
 path=ev/('ci-'+name+'.log')
 with path.open('w') as output:
  r=subprocess.run(argv,cwd=wt,env=env,stdout=output,stderr=subprocess.STDOUT)
 text=path.read_text();summary=re.search(r'Ran (\d+) tests in [0-9.]+s',text);skip=re.search(r'OK \(skipped=(\d+)\)',text)
 row={'name':name,'command':shlex.join(argv),'exit':r.returncode,'output':str(path),'tests':int(summary[1]) if summary else None,'skipped':int(skip[1]) if skip else 0}
 with lock:
  with (ev/'ci-results.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
 print(json.dumps(row),flush=True)
 return row
with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(run,commands))
(ev/'ci-results.json').write_text(json.dumps(results,indent=2)+'\n')
(ev/'ci-tests.json').write_text(json.dumps([{'name':r['name'],'status':'passed' if r['exit']==0 else 'failed','message':f"exit {r['exit']}; tests {r['tests']}; skipped {r['skipped']}",'file':r['output']} for r in results],indent=2)+'\n')
print(json.dumps({'entries':len(results),'failed':[r['name'] for r in results if r['exit']],'unittest_tests':sum(r['tests'] or 0 for r in results),'unittest_skipped':sum(r['skipped'] for r in results)}),flush=True)
raise SystemExit(any(r['exit'] for r in results))
