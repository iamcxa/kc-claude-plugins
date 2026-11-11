import importlib.util, json, re, subprocess, sys
from pathlib import Path
root=Path(sys.argv[1]); out=Path('/tmp/budget-implementation-2'); scripts=root/'kc-dev-flow-2/scripts';sys.path.insert(0,str(scripts))
import test_role_triggers as fixture
spec=importlib.util.spec_from_file_location('old_role',out/'base_role_triggers.py'); old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
def base(path):return subprocess.check_output(['git','-C',str(root),'show',f'e8664a72b0f904e5dda3c391d52ab3abaca876b4:{path}'],text=True)
def count(text):
    independent=len(re.findall(r'\S+',text)); wc=int(subprocess.check_output(['wc','-w'],input=text,text=True).strip()); assert independent==wc; return independent
f=fixture.BudgetTest('test_uncountable_budget_prints_but_does_not_hold');f.setUp()
try:
    f.seed();f.record('implementation',1); at=fixture.run(f.state,fixture.SLUG)[1]
    f.record('implementation',2); held=fixture.run(f.state,fixture.SLUG)[1]
    f.seed('at most 3 days'); unc=fixture.run(f.state,fixture.SLUG)[1]
    f.seed('ten cycles per stage');f.put(f.body+fixture.validations(fixture.StepBackTest.failed,fixture.StepBackTest.failed))
    old_idle=old.check(f.state,fixture.SLUG,'HEAD')[1];new_idle=fixture.run(f.state,fixture.SLUG)[1]
    data=[dict(name='FO startup/resume workflow',before=count(base('kc-dev-flow-2/references/sd/workflow.md')),after=count((root/'kc-dev-flow-2/references/sd/workflow.md').read_text())),
          dict(name='Countable dispatch budget output',before=0,after=count(at)),dict(name='Uncountable dispatch budget output',before=0,after=count(unc)),
          dict(name='Overrun hold output (failure 2 symptom)',before=0,after=count(held)),dict(name='Idle/merge forwarded reminder, countable task',before=count(old_idle),after=count('\n'.join(l for l in new_idle.splitlines() if l.startswith('next:')))),
          dict(name='Ideation worker principles',before=count(base('kc-dev-flow-2/skills/ideation/principles.md')),after=count((root/'kc-dev-flow-2/skills/ideation/principles.md').read_text()))]
    f.seed('at most 4 dispatches total');total=fixture.run(f.state,fixture.SLUG)[1]
    f.seed('240 累計代理分鐘、最多 4 次派工，含一輪修正');mixed=fixture.run(f.state,fixture.SLUG)[1]
    data += [dict(name='Total dispatch budget output',before=0,after=count(total)),dict(name='Mixed minutes and total budget output',before=0,after=count(mixed))]
    (out/'word-count.json').write_text(json.dumps(dict(measurement='wc -w independently agrees with regex nonspace token count',rows=data,samples=dict(at=at,uncountable=unc,hold=held,old_idle=old_idle,new_idle=new_idle,total=total,mixed=mixed)),indent=2)+'\n')
finally:f.doCleanups()
