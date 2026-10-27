from pathlib import Path
import ast,subprocess,importlib.util,tempfile,shutil
W=Path('/tmp/peers-validation-730-cycle1');E=Path('/tmp/peers-validation-730-cycle1-evidence');P=W/'kc-dev-flow-2'
def git(*args):return subprocess.check_output(['git','-C',str(W),*args],text=True)
base='c70f1b22cb1e4a66fd15c617647c778d54c59ec9';old='bff1d8147b626ae91c6ca431f7dde459a63f254d'
text=(P/'scripts/lint-skills.py').read_text()
assert 'extension_dependency_errors' not in text
tests=(P/'scripts/test_lint_skills.py').read_text()
assert 'test_peers_alone_and_optional_paseo_selection' not in tests
assert 'test_paseo_without_peers_is_refused_in_the_workflow' not in tests
def func(s):
 node=next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef) and n.name=='extension_tier_errors')
 return ast.get_source_segment(s,node)
presence='    for name in tiers:\n        if not (root / "extensions" / name / "EXTENSION.md").is_file():\n            errors.append(f"README.md: extension `{name}` has no EXTENSION.md")\n'
assert presence in text
assert func(text).replace(presence,'')==func(git('show',base+':kc-dev-flow-2/scripts/lint-skills.py'))
assert set(git('diff','--name-only',old,'HEAD').splitlines())=={'kc-dev-flow-2/scripts/lint-skills.py','kc-dev-flow-2/scripts/test_lint_skills.py'}
for row in git('diff','--numstat',old,'HEAD').splitlines():assert row.split()[0]=='0'
assert sum(int(r.split()[1]) for r in git('diff','--numstat',old,'HEAD').splitlines())==23
print('Repair identity PASS: helper/call/two tests removed; 23 deletions in two scripts; every other path unchanged.')
print('Tier-check bytes match base exactly; presence-check addition retained.')
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
