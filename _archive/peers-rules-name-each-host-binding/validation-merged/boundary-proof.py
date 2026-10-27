from pathlib import Path
import subprocess,importlib.util,tempfile,shutil
W=Path('/tmp/peers-validation-730-merge');E=Path('/tmp/peers-validation-730-merge-evidence');P=W/'kc-dev-flow-2'
spec=importlib.util.spec_from_file_location('lint',P/'scripts/lint-skills.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory() as d:
 root=Path(d);pkg=root/'kc-dev-flow-2';shutil.copytree(P,pkg,ignore=shutil.ignore_patterns('__pycache__'))
 assert m.extension_tier_errors(pkg)==[]
 print('Default package template PASS')
 adopter=root/'docs/dev2/README.md';adopter.parent.mkdir(parents=True)
 for selected in ('learn, peers','learn, peers, paseo','learn, paseo'):
  adopter.write_text('---\nextensions: ['+selected+']\n---\n')
  assert m.extension_tier_errors(pkg)==[]
  print('Adopter ['+selected+']: package result unchanged PASS')
 wf=pkg/m.WORKFLOW;s=wf.read_text()
 wf.write_text(s.replace('extensions: [learn, peers]','extensions: [learn, peers, paseo]'))
 errors=m.extension_tier_errors(pkg);assert any('not `required`' in x for x in errors)
 print('Optional extension in package template REFUSED:',*errors)
 wf.write_text(s)
 readme=pkg/'README.md';oldread=readme.read_text();readme.write_text(oldread.replace('| optional, requires peers |','| required |'))
 assert any('paseo` is required' in x for x in m.extension_tier_errors(pkg))
 print('AC-7 mandatory-Paseo mutant REJECTED')
 readme.write_text(oldread)
 (pkg/'extensions/paseo/EXTENSION.md').unlink()
 assert any('has no EXTENSION.md' in x for x in m.extension_tier_errors(pkg))
 print('Missing extension document REFUSED')
 for selected in ('learn, peers','learn, peers, roborev','learn, peers, paseo'):
  expected='extensions: ['+selected+']\n'
  ours=root/'ours';b=root/'base';theirs=root/'theirs'
  ours.write_text(expected);b.write_text('extensions: [learn, peers]\n');theirs.write_text(b.read_text())
  p=subprocess.run(['git','merge-file','-p',str(ours),str(b),str(theirs)],capture_output=True,text=True)
  assert p.returncode==0 and p.stdout==expected
  print('Three-way merge preserved ['+selected+']')
with tempfile.TemporaryDirectory() as d:
 root=Path(d);pkg=root/'kc-dev-flow-2';shutil.copytree(P,pkg,ignore=shutil.ignore_patterns('__pycache__'));shutil.copytree(W/'scripts',root/'scripts')
 f=pkg/'scripts/lint-skills.py';f.write_text(f.read_text().replace('if not (root / "extensions" / name / "EXTENSION.md").is_file():','if False:',1))
 p=subprocess.run(['python3','-B',str(pkg/'scripts/test_lint_skills.py'),'RouteMutationTests.test_missing_optional_extension_document_is_named'],capture_output=True,text=True)
 (E/'document-mutant.txt').write_text(p.stdout+p.stderr);assert p.returncode==1
 print('Removed-document-guard mutant: named test FAILED as expected (exit 1)')
