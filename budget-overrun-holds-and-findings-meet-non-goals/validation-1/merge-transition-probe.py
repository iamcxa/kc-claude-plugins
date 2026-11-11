import json, os, subprocess, sys
from pathlib import Path
root=Path(sys.argv[1]);sys.path.insert(0,str(root/'kc-dev-flow-2/scripts'))
import test_delivery_gate as t
text=t.ALIGNED+'\n## Budget\nOne cycle per stage.\n'
rows=[]
for admitted in (False,True):
    records={**t.RECORDS,'implementation-1.md':'Symptom: none\n','implementation-2.md':'Symptom: a different gap\n'}
    if admitted:records={k:'Budget: One cycle per stage.\n'+v for k,v in records.items()}
    def setup(d):
        t.committed(text)(d)
        common=['git','-C',d,'-c','user.name=t','-c','user.email=t@t','-c','core.hooksPath=/dev/null','-c','commit.gpgsign=false']
        subprocess.run([*common,'add','task/dispatch'],check=True)
        subprocess.run([*common,'commit','-qm','records'],check=True)
    result=t.run_check(task=text,records=records,setup=setup,roles=True)
    assert result.code==int(admitted),result.out
    assert (t.gate.ASK in result.out)==(not admitted),result.out
    assert ('budget exceeded' in result.out)==admitted,result.out
    rows.append(dict(first_record_has_header=admitted,exit=result.code,out=result.out,written=result.written))
Path('/tmp/budget-validation-841/evidence/merge-transition-probe.json').write_text(json.dumps(rows,indent=2)+'\n')
print('old first record: merge ask passes; new first record: budget holds merge ask')
