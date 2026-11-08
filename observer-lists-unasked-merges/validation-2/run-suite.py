import concurrent.futures,json,os,pathlib,re,subprocess,time
root=pathlib.Path('/tmp/observer-validation-a43b537c/candidate')
out=root.parent/'suite';out.mkdir(exist_ok=True)
sd='/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3'
names=json.loads(pathlib.Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/observer-lists-unasked-merges/implementation/suite-summary.json').read_text())['results']
def check(row):
 name=row['name']; paths=list((root/'kc-dev-flow-2').rglob(name+'.py'))
 assert len(paths)==1,(name,paths)
 command=['python3','-B',str(paths[0])]
 if name=='test_sd_dispatch':command+=['--sd-plugin-root',sd]
 env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','SPACEDOCK_BIN':'/Users/kent/.local/bin/spacedock'}
 start=time.monotonic();p=subprocess.run(command,cwd=root,env=env,capture_output=True,text=True)
 raw=p.stdout+p.stderr;(out/(name+'.log')).write_text(raw)
 count=re.search(r'Ran (\d+) tests?',raw);skips=re.search(r'OK \(skipped=(\d+)\)',raw)
 return {'name':name,'status':'passed' if p.returncode==0 else 'failed','exit':p.returncode,'tests':int(count[1]) if count else 0,'skipped':int(skips[1]) if skips else 0,'seconds':time.monotonic()-start,'command':command}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(check,names))
summary={'commands':len(rows),'unittest_cases':sum(x['tests'] for x in rows),'skipped':sum(x['skipped'] for x in rows),'results':rows,'limits':'Local CLI 0.27.2 with plugin files 0.27.3; not the pinned hosted installation. CI cost per PR not measured.'}
(root.parent/'suite-summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps({k:v for k,v in summary.items() if k!='results'}));print('failed:',[x['name'] for x in rows if x['exit']])
assert all(x['exit']==0 for x in rows)
