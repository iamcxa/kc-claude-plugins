from pathlib import Path
import os,subprocess,json,shutil,sys,time
v=Path(__file__).parent;s=Path('/tmp/validate-853-20261112-1752');repo=Path('/tmp/validate-853-20261112-1752/objects.git')
gate=s/'candidate/kc-dev-flow-2/scripts/delivery_gate.py'
env=dict(os.environ,TMPDIR=str(s/'tmp'),MERGE_REPLAY_CODE=str(repo),PYTHONDONTWRITEBYTECODE='1')
head='6da9a765ee04e1e2c7836517ba01f75b0ea91d73';red='eeee002303aca7c14237258253cd9318a5b3248c';green='546a136386c94c58e430c91a6f3457b38bd73880'
rows=[]
def run(name,args,expected):
 start=time.monotonic()
 with (v/(name+'.log')).open('w') as f:r=subprocess.run([str(x) for x in args],env=env,stdout=f,stderr=subprocess.STDOUT)
 rows.append(dict(name=name,status='passed' if r.returncode==expected else 'failed',exit=r.returncode,expected=expected,seconds=time.monotonic()-start))
 print(name,r.returncode,'expected',expected,flush=True)
 assert r.returncode==expected,(name,r.returncode)
 return r
for name,trunk,expected in [('red',red,1),('green',green,0)]:
 wf=s/('runtime-'+name);wf.mkdir(exist_ok=True);(wf/'task.md').write_text('# Historical runtime\n');(wf/'README.md').write_text('---\ntrunk: main\nmerge-test: python3 -B kc-dev-flow-2/scripts/test_design_surfaces.py\n---\n')
 run('runtime-'+name,['python3','-B',gate,'merge-run',wf/'task.md','--pr','iamcxa/kc-claude-plugins#841','--head',head,'--trunk',trunk,'--workflow-dir',wf,'--repo-dir',repo,'--','python3','-B','kc-dev-flow-2/scripts/test_design_surfaces.py'],expected)
 for f in (wf/'task/merge').iterdir():shutil.copy(f,v/(name+'-'+f.name))
merged=subprocess.check_output(['git','-C',str(repo),'merge-tree','--write-tree',red,head],text=True).strip()
landed=subprocess.check_output(['git','-C',str(repo),'rev-parse','571a7bd8a24ce08fac149fbcc91c4561610834c7^{tree}'],text=True).strip()
assert merged==landed
(v/'tree-equality.log').write_text('merge-tree='+merged+'\nlanded-tree='+landed+'\n')
head_dir=s/'historical-head';head_dir.mkdir()
a=subprocess.Popen(['git','-C',str(repo),'archive',head],stdout=subprocess.PIPE);t=subprocess.run(['tar','-x','-C',str(head_dir)],stdin=a.stdout);a.stdout.close();assert a.wait()==t.returncode==0
run('head-only',['python3','-B',head_dir/'kc-dev-flow-2/scripts/test_design_surfaces.py'],0)
replay=v/'replay_841.py';base=s/'base/kc-dev-flow-2/scripts/delivery_gate.py'
for name,g,args,expected in [('control',base,[],0),('AC-1',gate,[],1),('AC-2',gate,['--result',v/'green-result-1.json','--trunk',green],0),('AC-3',gate,['--result',v/'green-result-1.json'],1),('AC-4',gate,['--result',v/'red-result-1.json'],1),('AC-5',gate,['--not-run'],0),('AC-6',gate,['--status','ahead','--trunk','e8664a72b0f904e5dda3c391d52ab3abaca876b4'],0)]:
 run('invoke-'+name,['python3','-B',replay,g,v/('replay-'+name+'.log'),*args],expected)
r=json.loads((v/'green-result-1.json').read_text());r['exit']=1;(v/'green-exit-mutated.json').write_text(json.dumps(r)+'\n')
run('AC-2-falsifier',['python3','-B',replay,gate,v/'AC-2-falsifier-output.log','--result',v/'green-exit-mutated.json','--trunk',green],1)
(v/'runtime-tests.json').write_text(json.dumps(rows,indent=2)+'\n')
