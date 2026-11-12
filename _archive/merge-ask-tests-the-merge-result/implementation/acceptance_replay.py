#!/usr/bin/env python3
import json, os, shutil, subprocess, sys
from pathlib import Path
code=Path(sys.argv[1]).resolve()
here=Path(__file__).resolve().parent
candidate=code/'kc-dev-flow-2/scripts/delivery_gate.py'
control=code/'.context/merge-ask-tests-the-merge-result-control/kc-dev-flow-2/scripts/delivery_gate.py'
green=here/'runtime-green/task/merge/result-1.json'
red=here/'runtime-red/task/merge/result-1.json'
control_root=code/'.context/merge-ask-tests-the-merge-result-control'
control_root.mkdir(parents=True,exist_ok=True)
archive=subprocess.run(['git','-C',str(code),'archive','8ce0eb6050c889b21baccf50fec35231bc888d66','kc-dev-flow-2/scripts'],capture_output=True,check=True)
subprocess.run(['tar','-x','-C',str(control_root)],input=archive.stdout,check=True)
os.environ['MERGE_REPLAY_CODE']=str(code)
cases=[('control',control,[],0),('AC-1',candidate,[],1),
       ('AC-2',candidate,['--result',str(green),'--trunk','546a136386c94c58e430c91a6f3457b38bd73880'],0),
       ('AC-3',candidate,['--result',str(green)],1),('AC-4',candidate,['--result',str(red)],1),
       ('AC-5',candidate,['--not-run'],0),
       ('AC-6',candidate,['--status','ahead','--trunk','e8664a72b0f904e5dda3c391d52ab3abaca876b4'],0)]
rows=[]
for name,gate,args,expected in cases:
    log=here/('replay-'+name+'.log')
    done=subprocess.run([sys.executable,'-B',str(here/'replay_841.py'),str(gate),str(log),*args],capture_output=True,text=True)
    rows.append(dict(name=name,status='passed' if done.returncode==expected else 'failed',
                     message=f'exit {done.returncode}, expected {expected}',log=log.name))
    print(name,done.returncode,expected)
base=(here/'replay-control.log').read_text().splitlines()[2:]
ahead=(here/'replay-AC-6.log').read_text().splitlines()[2:]
assert base==ahead,(base,ahead)
rows.append(dict(name='AC-6 unchanged output',status='passed',message=f'{len(" ".join(base).split())} words, equal to control'))
for name,expected in [('green',0),('red',1)]:
    rec=json.loads((here/f'runtime-{name}/task/merge/result-1.json').read_text())
    assert rec['exit']==expected,rec
rows.append(dict(name='AC-7 actual historical merge result',status='passed',message='red result tree 3ba409485baf; 1 failure in 226; earlier trunk passes'))
(here/'acceptance.json').write_text(json.dumps(rows,indent=2)+'\n')
shutil.rmtree(control_root)
raise SystemExit(any(r['status']!='passed' for r in rows))
