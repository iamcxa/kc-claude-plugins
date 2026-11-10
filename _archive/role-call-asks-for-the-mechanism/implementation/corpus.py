import concurrent.futures, json, pathlib, re, subprocess, sys, tempfile
wt, state, output=map(pathlib.Path,sys.argv[1:4]);rev=sys.argv[4] if len(sys.argv)>4 else subprocess.check_output(['git','-C',str(state),'rev-parse','HEAD'],text=True).strip()
paths=subprocess.check_output(['git','-C',str(state),'ls-tree','-r','--name-only',rev],text=True).splitlines()
tasks=[p for p in paths if re.fullmatch(r'(?:_archive/)?[^/]+(?:/index)?\.md',p) and p not in ('observer.md','README.md')]
with tempfile.TemporaryDirectory(prefix='rcm-corpus-') as tmp:
 base=pathlib.Path(tmp)/'role_triggers.py';base.write_bytes(subprocess.check_output(['git','-C',str(wt),'show','82c9e67ae892b80647c3f6a8b6929f993e42dbc2:kc-dev-flow-2/scripts/role_triggers.py']))
 candidate=wt/'kc-dev-flow-2/scripts/role_triggers.py'
 def compare(path):
  task=pathlib.Path(path);slug=task.parent.name if task.name=='index.md' else task.stem
  where=state/('_archive' if path.startswith('_archive/') else '')
  rows=[]
  for script in (base,candidate):
   r=subprocess.run([sys.executable,'-B',str(script),str(where),slug,'--rev',rev],capture_output=True,text=True)
   rows.append({'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
  a,b=rows
  if a==b: verdict='unchanged'
  elif a['exit']==b['exit']: verdict='intended question/template change'
  elif a['exit']==0 and b['exit']==1 and 'chief-engineer' in b['stdout']: verdict='intended plain decline no longer clears findings'
  else: verdict='unexpected'
  return {'path':path,'verdict':verdict,'base':a,'candidate':b}
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: rows=list(pool.map(compare,tasks))
summary={'state':str(state),'rev':rev,'tasks':len(rows),'counts':{v:sum(x['verdict']==v for x in rows) for v in sorted({x['verdict'] for x in rows})},'rows':rows}
output.write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='rows'}));assert not any(x['verdict']=='unexpected' for x in rows)
