import argparse, importlib.util, json, re, shutil, subprocess, sys, tarfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('candidate',type=Path);p.add_argument('relay_state',type=Path);p.add_argument('own_state',type=Path);p.add_argument('out',type=Path);p.add_argument('--relay-readme',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
def git(root,*args):return subprocess.check_output(['git','-C',str(root),*args])
def snapshot(root,name):
 sha=git(root,'rev-parse','HEAD').decode().strip();dest=a.out/name;dest.mkdir(exist_ok=True)
 archive=a.out/(name+'.tar');archive.write_bytes(git(root,'archive',sha))
 with tarfile.open(archive) as t:t.extractall(dest,filter='data')
 return sha,dest
base=a.out/'base';base.mkdir(exist_ok=True)
archive=a.out/'base.tar';archive.write_bytes(git(a.candidate,'archive','6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1','kc-dev-flow-2/scripts'))
with tarfile.open(archive) as t:t.extractall(base,filter='data')
scripts=a.candidate/'kc-dev-flow-2/scripts';sys.path.insert(0,str(scripts))
import decision_ledger as dl
result={}
for label,root in [('relay',a.relay_state),('own',a.own_state)]:
 sha,dest=snapshot(root,label)
 tasks=['theme-switch-keeps-draft','room-result-skips-legacy-retraction','signed-in-job-split','pair-pages-favicon']
 rows=dl.ledger(dest)
 rows=[r for r in rows if r['kind']=='resolution' and r['by']=='person:captain' and (r['task'] in tasks if label=='relay' else (r.get('at') or '')[:10]>='2026-11-06')]
 compared=[{'task':r['task'],'attempt':r['attempt'],'at':r['at'],'quoted':dl.quotes_bound_question(r),'question':r['question'],'reason':r['reason']} for r in rows]
 result[label]={'sha':sha,'total':len(rows),'refused':sum(not r['quoted'] for r in compared),'rows':compared}
 if label=='relay':
  assert (len(rows),result[label]['refused'])==(12,11),result[label]
  task=dest/'_archive/theme-switch-keeps-draft.md';report=dest/'_archive/theme-switch-keeps-draft/design/validation-1.yaml'
  task.write_text(re.sub(r'^status: done$', 'status: validation', task.read_text(), flags=re.M))
  t=report.read_text();pictures=re.search(r'^  # (design/built/.*)$',t,re.M)[1].split(', ');assert len(pictures)==14
  report.write_text(re.sub(r'^  preview:.*$', '  preview:\n'+''.join('    - '+v+'\n' for v in pictures).rstrip(),t,flags=re.M))
  result['screen']={}
  result['coverage']={}
  for version,code in [('base',base),('candidate',a.candidate)]:
   cmds={'screen':['design_surfaces.py','check',str(task)],'coverage':['dispatch_records.py','--coverage',str(task.with_suffix('')),'--stage','validation','--readme',str(a.relay_readme)]}
   for kind,cmd in cmds.items():
    run=subprocess.run([sys.executable,'-B',str(code/'kc-dev-flow-2/scripts'/cmd[0]),*cmd[1:]],capture_output=True,text=True)
    (a.out/f'{kind}-{version}.log').write_text(run.stdout+run.stderr)
    result[kind][version]={'exit':run.returncode,'preview_lines':len(re.findall(r'^preview: ',run.stdout,re.M)),'stdout':run.stdout,'stderr':run.stderr}
  assert result['screen']['candidate']['preview_lines']==14,result['screen']
  assert 'built screen review not run' not in result['screen']['candidate']['stdout'],result['screen']
  assert 'built screen review not run' in result['screen']['base']['stdout'],result['screen']
  assert result['coverage']['candidate']['exit']==0 and result['coverage']['base']['exit']==2,result['coverage']
(a.out/'replay.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:{n:v for n,v in d.items() if n not in ('rows','stdout','stderr')} for k,d in result.items()},ensure_ascii=False,indent=2))
