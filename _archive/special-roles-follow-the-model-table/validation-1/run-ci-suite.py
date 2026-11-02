from pathlib import Path
import os,re,subprocess,sys,json,time
WT=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-special-roles-follow-the-model-table/.validation-562b1a87')
E=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-special-roles-follow-the-model-table/.validation-evidence');plugin=Path('/tmp/special-roles-ci-repair/spacedock')
assert subprocess.check_output(['git','-C',str(plugin),'rev-parse','HEAD'],text=True).strip()=='4d158a484ec73e184861067f8ed1e20087fdc26a'
workflow=WT/'.github/workflows/kc-dev-flow-2-tests.yml'
scripts=re.findall(r'^\s*run: (?:[^\n]*? )?python3 (kc-dev-flow-2/\S+)',workflow.read_text(),re.M)
assert scripts and len(scripts)==len(set(scripts))
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','SPACEDOCK_BIN':'/Users/kent/.local/bin/spacedock'}
results=[];started=time.monotonic()
for i,script in enumerate(scripts,1):
 cmd=[sys.executable,'-B',script]
 if script.endswith('/test_sd_dispatch.py'):cmd+=['--sd-plugin-root',str(plugin),'--keep']
 r=subprocess.run(cmd,cwd=WT,env=env,text=True,capture_output=True)
 log=E/(Path(script).stem+'.log');log.write_text(r.stdout+r.stderr)
 counts=re.findall(r'Ran (\d+) tests? in',r.stdout+r.stderr)
 row={'script':script,'command':cmd,'exit':r.returncode,'unittest_count':int(counts[-1]) if counts else None,'log':str(log)}
 results.append(row);(E/'suite-results.json').write_text(json.dumps(results,indent=2))
 print(f'{i}/{len(scripts)} exit={r.returncode} tests={row["unittest_count"]} {script}',flush=True)
 if r.returncode:print((r.stdout+r.stderr)[-3000:],flush=True)
print('TOTAL',len(results),'commands;',sum(row['unittest_count'] or 0 for row in results),'unit tests;',sum(row['exit']!=0 for row in results),'failed commands;',round(time.monotonic()-started,2),'seconds',flush=True)
raise SystemExit(any(row['exit'] for row in results))
