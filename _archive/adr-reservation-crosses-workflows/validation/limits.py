import importlib.util,json,subprocess,sys
from pathlib import Path
out=Path('/tmp/adr-reservation-validation-801')
spec=importlib.util.spec_from_file_location('tests',out/'candidate/kc-dev-flow-2/scripts/test_number_guards.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
results=[]
def case(name,fn):
 t=m.CrossWorkflowTests();t.setUp()
 try:
  detail=fn(t);results.append(dict(name=name,status='passed',detail=detail))
 finally:t.doCleanups()
def race(t):
 a=t.reserve();b=t.reserve()
 assert (a.returncode,a.stdout)==(0,'ADR: 0061\n')==(b.returncode,b.stdout)
 t.origin.git('checkout','-q','spacedock-state/dev2');t.origin.commit('raced',**{'other.md':'## Number guards\nADR: 0061\n'});t.origin.git('checkout','-q','main')
 t.candidate(61);c=t.run_guard('check');assert c.returncode==1 and 'FAIL R8' in c.stdout
 return 'Two reserves before a state push both print 0061; once another task pushes 0061, check refuses with R8.'
def invisible(t):
 (t.state/'unpublished.md').write_text('## Number guards\nADR: 0062\n')
 a=t.reserve();assert a.stdout=='ADR: 0063\n'
 second=t.workflow.parent/'other'; (second/'st').mkdir(parents=True)
 m.Fixture(str(second/'st'))
 (second/'README.md').write_text('---\nstate: st\ntrunk: main\n---\n')
 task=second/'st'/'consumer.md';task.write_text('## Number guards\n')
 b=subprocess.run(['python3','-B',m.SCRIPT,'reserve','--kind','adr','--repo',t.repo,'--workflow-dir',str(second),'--task',str(task)],capture_output=True,text=True)
 assert b.returncode==0 and b.stdout=='ADR: 0061\n'
 assert 'state checkout has no origin' in b.stderr
 return 'Own unpushed holder 0062 raises own reserve to 0063; the other workflow sees only published 0060 and returns 0061.'
def outside(t):
 t.origin.git('branch','-m','spacedock-state/dev2','custom-state/dev2')
 a=t.reserve();assert a.returncode==0 and a.stdout=='ADR: 0060\n'
 return 'A holder outside spacedock-state/* is not fetched/read; reserve returns 0060.'
def multiple(t):
 t.task.write_text('## Number guards\nADR: 0062\nADR: 0063\n')
 a=t.reserve();assert a.returncode==0 and a.stdout=='ADR: 0062\nADR: 0063\n'
 return 'Existing multiple ADR lines are returned unchanged; cardinality is not enforced.'
for name,fn in [('non-atomic window',race),('unpublished state invisible',invisible),('namespace bound',outside),('multiple numbers unchanged',multiple)]:case(name,fn)
(out/'limits.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
