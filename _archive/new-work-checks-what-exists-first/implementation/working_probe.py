import argparse,json,runpy,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('mode');p.add_argument('--repo',type=Path,required=True);p.add_argument('--base',required=True);p.add_argument('--expected',type=Path);a=p.parse_args()
m=runpy.run_path(str(Path(__file__).with_name('new_work_check.py')));g=m['routing'].__globals__;original_git=g['git'];original_source=g['source']
def source(repo,ref,path):
 return (repo/'kc-dev-flow-2'/path).read_text() if ref=='WORKTREE' else original_source(repo,ref,path)
def git(repo,*args):
 return original_git(repo,*[x for x in args if x!='WORKTREE'])
g['source']=source;g['git']=git;a.ref='WORKTREE'
if a.mode=='cost_guard':
 b=json.loads(a.expected.read_text());paths=['references/sd/workflow.md','references/sd/mods/kc-dev-flow-2.md','scripts/pr_watch.py','scripts/delivery_gate.py','scripts/observer_check.py'];good=all(source(a.repo,'WORKTREE',p)==original_source(a.repo,a.base,p) for p in paths)
 for row in b['worker_principles']:
  actual=len(source(a.repo,'WORKTREE','skills/'+row['stage']+'/principles.md').split());good=good and actual==row['probe_words']
 print(json.dumps({'matches_disclosed_instruction_cost':good}));sys.exit(0 if good else 1)
sys.exit(m[a.mode](a))
