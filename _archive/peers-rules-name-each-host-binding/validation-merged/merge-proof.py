from pathlib import Path
import subprocess,tempfile,ast
W=Path('/tmp/peers-validation-730-merge')
def git(*args):return subprocess.check_output(['git','-C',str(W),*args],text=True)
H='f7516476989b59fb45e4e5cb520d41ed9bc563ce'
B='b8ce84e584cf5c5cb482009d9d08d7316ce2a6ac'
O='dc3916fbb4ce9655dc37c5e4185653694e029de4'
A=git('merge-base',B,O).strip()
assert git('show','-s','--format=%P',H).strip()==O+' '+B
prior=set(git('diff','--name-only',A,O).splitlines())
current=set(git('diff','--name-only',B,H).splitlines())
assert prior==current
lint='kc-dev-flow-2/scripts/lint-skills.py'
for f in current-{lint}:assert git('show',H+':'+f)==git('show',O+':'+f),f
for f in set(git('diff','--name-only',O,H).splitlines())-{lint}:assert git('show',H+':'+f)==git('show',B+':'+f),f
with tempfile.TemporaryDirectory() as d:
 paths=[]
 for name,sha in [('ours',O),('ancestor',A),('theirs',B)]:
  p=Path(d)/name;p.write_text(git('show',sha+':'+lint));paths.append(str(p))
 r=subprocess.run(['git','merge-file','-p',*paths],capture_output=True,text=True)
 assert r.returncode==0,r.stderr
 assert r.stdout==git('show',H+':'+lint)
 print('Three-way lint merge reproduced without conflicts; exact candidate bytes match.')
s=git('show',H+':'+lint);main=git('show',B+':'+lint)
presence='    for name in tiers:\n        if not (root / "extensions" / name / "EXTENSION.md").is_file():\n            errors.append(f"README.md: extension `{name}` has no EXTENSION.md")\n'
assert s.replace(presence,'')==main
assert 'extension_dependency_errors' not in s
def budget(t):
 node=next(n for n in ast.parse(t).body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='WORKFLOW_BUDGET_STEPS' for x in n.targets))
 return ast.get_source_segment(t,node)
assert budget(s)==budget(main) and 'delta=144' in budget(s)
print('Main budget list byte-identical; +144 step and extension-document guard retained; removed helper stays absent.')
print('PR-owned files unchanged from prior candidate except merged lint; all other incoming files exactly match main.')
print('Parents:',O,B)
print('Merged base:',B,'; original common ancestor:',A)
