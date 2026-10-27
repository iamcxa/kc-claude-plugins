from pathlib import Path
import shutil,tempfile,subprocess,json
W=Path('/tmp/peers-validation-730')
E=Path('/tmp/peers-validation-evidence')
cases=[('drop-dependency-check','scripts/lint-skills.py','if dependency not in listed:','if False:','RouteMutationTests.test_peers_alone_and_optional_paseo_selection'),('drop-document-check','scripts/lint-skills.py','if not (root / "extensions" / name / "EXTENSION.md").is_file():','if False:','RouteMutationTests.test_missing_optional_extension_document_is_named')]
results=[]
for name,path,old,new,test in cases:
 with tempfile.TemporaryDirectory() as d:
  root=Path(d);package=root/'kc-dev-flow-2';shutil.copytree(W/'kc-dev-flow-2',package,ignore=shutil.ignore_patterns('__pycache__','*.pyc'));shutil.copytree(W/'scripts',root/'scripts',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  p=package/path;s=p.read_text();assert old in s;p.write_text(s.replace(old,new,1))
  run=subprocess.run(['python3','-B',str(package/'scripts/test_lint_skills.py'),test],capture_output=True,text=True)
  (E/f'mutant-{name}.txt').write_text(run.stdout+run.stderr);assert run.returncode==1
  results.append({'mutant':name,'exit':run.returncode,'test':test})
# Apply the new selection test against pre-change lint and extension data.
with tempfile.TemporaryDirectory() as d:
 root=Path(d);package=root/'kc-dev-flow-2';shutil.copytree(W/'kc-dev-flow-2',package,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for rel in ['scripts/lint-skills.py','extensions/peers/EXTENSION.md']:
  (package/rel).write_bytes(subprocess.check_output(['git','-C',str(W),'show','c70f1b22:kc-dev-flow-2/'+rel]))
 shutil.rmtree(package/'extensions/paseo')
 run=subprocess.run(['python3','-B',str(package/'scripts/test_lint_skills.py'),'RouteMutationTests.test_peers_alone_and_optional_paseo_selection'],capture_output=True,text=True)
 (E/'base-goal-failure.txt').write_text(run.stdout+run.stderr);assert run.returncode==1
 results.append({'base_goal_check':'extension selection contract absent','exit':run.returncode})
(E/'lint-mutations.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results))
