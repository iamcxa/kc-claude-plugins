import argparse, json, signal, subprocess, time
from pathlib import Path

R=Path(__file__).resolve().parent
p=argparse.ArgumentParser()
p.add_argument('host',choices=['codex','claude'])
a=p.parse_args()
if a.host=='codex':
    gate=json.loads((R/'runs/codex-base-1-fixed/meta.json').read_text())
    assert gate.get('exit')==0 and gate.get('report_written'), 'D1: first fixed Codex must complete'
    cells=[('base',1,'codex-base-1-repeat'),('candidate',1,'fixed-candidate'),('base',2,'codex-base-2'),('candidate',2,'codex-candidate-2'),('base',3,'codex-base-3'),('candidate',3,'codex-candidate-3')]
else:
    gate=json.loads((R/'batch-codex.json').read_text())
    assert gate['complete'], 'D1: Codex batch must complete before Claude'
    cells=[(arm,n,f'claude-{arm}-{n}') for n in range(1,4) for arm in ['base','candidate']]
active={};finished=[];halt=False
while cells or active:
    while cells and len(active)<5 and not halt:
        arm,n,scratch=cells.pop(0)
        label=f'{a.host}-{arm}-{n}-registered'
        existing=R/'runs'/label/'meta.json'
        if existing.exists():
            done=json.loads(existing.read_text())
            if not done.get('end'):
                active[label]=(None,label,None)
                print('watching '+label,flush=True)
                continue
            assert done.get('exit')==0 and done.get('report_written'), 'existing cell did not complete'
            finished.append({'run':label,'exit':0})
            continue
        assert len(list((R/'runs').glob('*/meta.json')))<16, 'hard stop'
        argv=['python3','-B',str(R/'run.py'),a.host,arm,str(n),'/tmp/validation-review-replay/'+scratch,'--label',label]
        log=(R/f'launch-{label}.log').open('w')
        proc=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        active[proc.pid]=(proc,label,log)
        print('started '+label,flush=True)
        # Wait for durable attempt registration before the next launch.
        while not (R/'runs'/label/'meta.json').exists() and proc.poll() is None:time.sleep(.1)
    for pid,(proc,label,log) in list(active.items()):
        if proc is None:
            observed=json.loads((R/'runs'/label/'meta.json').read_text())
            rc=(0 if observed.get('exit')==0 and observed.get('report_written') else 1) if observed.get('end') else None
        else:rc=proc.poll()
        if rc is None:continue
        if log:log.close()
        finished.append({'run':label,'exit':rc});del active[pid]
        print('finished '+label+' exit='+str(rc),flush=True)
        if rc and a.host=='codex':
            halt=True;cells=[]
            for other,_,_ in active.values():
                if other is not None:other.send_signal(signal.SIGTERM)
    if active:time.sleep(10)
result={'host':a.host,'complete':not halt and len(finished)==6 and all(x['exit']==0 for x in finished),'runs':finished,'D1_halt':halt}
(R/f'batch-{a.host}.json').write_text(json.dumps(result,indent=2)+'\n')
raise SystemExit(0 if result['complete'] else 1)
