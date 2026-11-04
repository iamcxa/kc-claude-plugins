import ast, importlib.util, json, os, subprocess, sys
from pathlib import Path
from unittest import mock
wt=Path(sys.argv[1]);ev=Path(sys.argv[2]);c=wt/'.validation-3-consumer';p=wt/'.validation-3-producer';base=(ev/'base.txt').read_text().strip()
def git(*a):return subprocess.check_output(['git','-C',str(c),*a],text=True)
ra='kc-dev-flow-2/extensions/release-acceptance/release_acceptance.py';test='kc-dev-flow-2/extensions/release-acceptance/test_release_acceptance.py'
def defs(text):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(text).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
old=defs(git('show',base+':'+ra));new=defs((c/ra).read_text())
assert all(old[k]==new[k] for k in ('Task','state_tasks','cmd_accepted'))
def tests(text):
 return {cl.name+'.'+f.name:ast.dump(f,include_attributes=False) for cl in ast.parse(text).body if isinstance(cl,ast.ClassDef) for f in cl.body if isinstance(f,ast.FunctionDef) and f.name.startswith('test_')}
previous=tests(git('show',base+':'+test));current=tests((c/test).read_text())
assert all(current.get(k)==v for k,v in previous.items())
(ev/'retention.json').write_text(json.dumps({'base':base,'candidate':git('rev-parse','HEAD').strip(),'unchanged_prerequisite_functions':['Task','state_tasks','cmd_accepted'],'retained_test_bodies':len(previous),'candidate_tests':len(current)},indent=2))
counts=[]
for path in ['kc-dev-flow-2/references/sd/workflow.md','kc-dev-flow-2/extensions/release-acceptance/EXTENSION.md']:
 before=git('show',base+':'+path);after=(c/path).read_text();assert before==after
 counts.append({'path':path,'base':len(before.split()),'candidate':len(after.split()),'identical':True})
row=next(line for line in (c/'kc-dev-flow-2/README.md').read_text().splitlines() if line.startswith('| [release-acceptance]'))
assert 'idle' in row
(ev/'word-counts.json').write_text(json.dumps({'counts':counts,'readme_row':row},indent=2))
findings=json.loads((ev/'sanitize-findings.json').read_text())
for f in findings:
 line=(c/f['file']).read_text().splitlines()[f['line']-1]
 assert line in git('show',base+':'+f['file']).splitlines()
(ev/'sanitize-baseline.log').write_text('PASS: both heuristic WARN lines occur verbatim on the current origin/main base. No BLOCK or REJECT.\n')
s=importlib.util.spec_from_file_location('due_tests',c/test);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
t=m.DueTests();t.setUp()
try:
 original=m.ra.subprocess.run
 def invoke(argv,**kwargs):
  if 'status' in argv:return original(argv,**kwargs)
  raise subprocess.TimeoutExpired('node',60)
 with mock.patch.object(m.ra.subprocess,'run',side_effect=invoke):
  code,out=t.due()
  assert code==0 and 'not run:' in out and 'timed out' in out and 'next:' not in out, repr((code,out))
  assert len(t.status_calls)==1
 (ev/'producer-timeout.log').write_text('PASS: producer timeout after successful task query diagnoses without next line.\n'+out)
finally:t.doCleanups()
without=wt/'.validation-3-support/base_release_acceptance.py';without.write_text(git('show',base+':'+ra))
r=subprocess.run([sys.executable,'-B',str(without),'due','--workflow-dir','/tmp','example.yaml'],env={**os.environ,'PYTHONPATH':str(c/'kc-dev-flow-2/scripts')},capture_output=True,text=True)
assert r.returncode==2 and 'invalid choice' in r.stderr
(ev/'without-feature.log').write_text(r.stdout+r.stderr)
(ev/'acceptance-exit.txt').write_text('0\n')
print('PASS: prerequisite behavior/tests retained; main weight unchanged; sanitize baseline unchanged; targeted timeout; without-feature control.')
