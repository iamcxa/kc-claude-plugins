import json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
root=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-model-roster-question-needs-both-families/.context/validation-3/candidate')
base=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-model-roster-question-needs-both-families/.context/validation-3/shared-mutations');base.mkdir()
source=(root/'kc-dev-flow-2/scripts/workflow_extensions.py').read_text()
inline='return [unquote(item) for item in re.findall(ITEM, match.group(1))]'
block='extensions.append(unquote(match.group(1)))'
mutations=[('inline-comment-membership',inline,'return re.findall(r"[\\w-]+", value)',1),
 ('quoted-block-item',block,'extensions.append(match.group(1))',0),
 ('block-comment-membership',block,'extensions.append(unquote(match.group(1)) + (raw[match.end(1):] if "#" in raw[match.end(1):] else ""))',0)]
runner=base/'check.py'
runner.write_text("import sys\nfrom pathlib import Path\nsys.path.insert(0,sys.argv[1])\nimport test_sd_dispatch as t\nt.exercise_extension_lists(Path(sys.argv[2]),scripts=Path(sys.argv[3]))\n")
sys.path.insert(0,str(root/'kc-dev-flow-2/scripts'))
from dispatch_records import PASEO_COMPLETION_LINE
from test_sd_dispatch import MAIN_LINE
results=[]
for name,old,new,expected_checker in mutations:
 assert source.count(old)==1,name
 directory=base/name;directory.mkdir()
 pkg=directory/'kc-dev-flow-2'
 shutil.copytree(root/'kc-dev-flow-2',pkg,ignore=shutil.ignore_patterns('__pycache__'))
 (pkg/'scripts/workflow_extensions.py').write_text(source.replace(old,new))
 probe=directory/'probe'
 run=subprocess.run([sys.executable,'-B',str(runner),str(root/'kc-dev-flow-2/scripts'),str(probe),str(pkg/'scripts')],capture_output=True,text=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),timeout=60)
 (directory/'matrix.log').write_text(run.stdout+run.stderr)
 assert run.returncode==1 and 'AssertionError' in run.stderr and 'model_roster.py' in run.stderr,(name,run.stderr)
 repo=probe/'code';record=repo/'task/dispatch/implementation-1.md'
 record.write_text(record.read_text().replace(MAIN_LINE,PASEO_COMPLETION_LINE))
 args=[sys.executable,'-B',str(pkg/'scripts/dispatch_records.py'),'--readme',str(repo/'README.md'),str(repo/'task')]
 checker=subprocess.run(args,capture_output=True,text=True,timeout=30)
 assert checker.returncode != expected_checker and checker.returncode in (0,1),(name,checker.stdout,checker.stderr)
 (directory/'checker.log').write_text(checker.stdout+checker.stderr)
 providers=json.dumps([dict(provider=p,status='available',enabled='Enabled') for p in ('codex','claude')])
 for body in ('extensions: []',''):
  (repo/'README.md').write_text('---\nentity-type: task\n'+body+'\n---\n')
  question=subprocess.run([sys.executable,'-B',str(pkg/'scripts/model_roster.py'),'question','--code-root',str(repo),'--readme',str(repo/'README.md'),'--providers','-'],input=providers,capture_output=True,text=True,timeout=30)
  control=subprocess.run(args,capture_output=True,text=True,timeout=30)
  assert question.returncode==3 and control.returncode==1,(name,body,question.stdout,control.stdout)
 result=dict(mutation=name,matrix_exit=run.returncode,checker_exit=checker.returncode,checker_expected=expected_checker,empty_and_no_key_controls='pass',cache='python3 -B; copied caches excluded')
 results.append(result);print(json.dumps(result),flush=True)
(base/'results.json').write_text(json.dumps(results,indent=2)+'\n')
print('Evidence:',base,flush=True)
