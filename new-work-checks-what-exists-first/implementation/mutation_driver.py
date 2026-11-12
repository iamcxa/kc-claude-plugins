"""Round-two disposable source/evidence controls; not a model-behavior grader.
Run with python3 -B, --scratch, --evidence, --task and --loaded-package.
Product bytes are never mutated; --scratch/code-source is an independent clone.
"""
import argparse
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

p = argparse.ArgumentParser()
for arg in ('scratch', 'evidence', 'task', 'loaded-package'):
    p.add_argument('--'+arg, type=Path, required=True)
a = p.parse_args()
r = a.scratch / 'code-source'
e = a.evidence
candidate = json.loads((e/'candidate.json').read_text())['candidate']
base = json.loads((e/'candidate.json').read_text())['base']
assert subprocess.check_output(['git','-C',str(r),'rev-parse','HEAD'],text=True).strip() == candidate
results = []
logs = e/'mutation-output'
logs.mkdir(exist_ok=True)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', TMPDIR=str(a.scratch))

def run(name, args, reject=False):
    for cache in r.rglob('__pycache__'):
        shutil.rmtree(cache)
    done = subprocess.run(args, cwd=r, env=env, capture_output=True, text=True)
    (logs/(name+'.log')).write_text(done.stdout+done.stderr)
    correct = done.returncode == (1 if reject else 0)
    results.append(dict(name=name, status='passed' if correct else 'failed',
                        expected_exit=1 if reject else 0, actual_exit=done.returncode,
                        command=args, output='mutation-output/'+name+'.log'))
    return done

# The frozen trial probe reads a working snapshot for controlled mutations only.
wrapper = a.scratch/'working_probe.py'
wrapper.write_text('''import argparse,json,runpy,subprocess,sys\nfrom pathlib import Path\np=argparse.ArgumentParser();p.add_argument('mode');p.add_argument('--repo',type=Path,required=True);p.add_argument('--base',required=True);p.add_argument('--expected',type=Path);a=p.parse_args()\nm=runpy.run_path(str(Path(__file__).with_name('new_work_check.py')));g=m['routing'].__globals__;original_git=g['git'];original_source=g['source']\ndef source(repo,ref,path):\n return (repo/'kc-dev-flow-2'/path).read_text() if ref=='WORKTREE' else original_source(repo,ref,path)\ndef git(repo,*args):\n return original_git(repo,*[x for x in args if x!='WORKTREE'])\ng['source']=source;g['git']=git;a.ref='WORKTREE'\nif a.mode=='cost_guard':\n b=json.loads(a.expected.read_text());paths=['references/sd/workflow.md','references/sd/mods/kc-dev-flow-2.md','scripts/pr_watch.py','scripts/delivery_gate.py','scripts/observer_check.py'];good=all(source(a.repo,'WORKTREE',p)==original_source(a.repo,a.base,p) for p in paths)\n for row in b['worker_principles']:\n  actual=len(source(a.repo,'WORKTREE','skills/'+row['stage']+'/principles.md').split());good=good and actual==row['probe_words']\n print(json.dumps({'matches_disclosed_instruction_cost':good}));sys.exit(0 if good else 1)\nsys.exit(m[a.mode](a))\n''')

def probe(mode):
    return ['python3','-B',str(wrapper),mode,'--repo',str(r),'--base',base]

def mutate(name, rel, transform, command):
    path=r/rel; old=path.read_bytes()
    try:
        path.write_bytes(transform(old.decode()).encode())
        run(name, command, reject=True)
    finally:
        path.write_bytes(old)

ideation='kc-dev-flow-2/skills/ideation/principles.md'
implementation='kc-dev-flow-2/skills/implementation/principles.md'
run('AC1-positive-routing',probe('routing'))
mutate('AC1-unlinked-ideation',ideation,lambda s:s.replace('#before-new-work','#existing-code-capability-check'),probe('routing'))
mutate('AC1-missing-general-home',implementation,lambda s:s.replace('## Before new work\n','## Removed home\n'),probe('routing'))
mutate('AC1-deeper-audit-altered',implementation,lambda s:s.replace('Skip greenfield work','Skip all work'),probe('routing'))

# Controlled mutations of the actual observation record. These cannot establish
# cold-worker compliance or authenticate a model transcript.
observation=json.loads((e/'replay-result.json').read_text())
checker=a.scratch/'evidence_guard.py'
checker.write_text('''import json,sys\nfrom pathlib import Path\na=json.loads(Path(sys.argv[2]).read_text());kind=sys.argv[1]\nif kind=='replay':\n events=a['events'];found=next((i for i,x in enumerate(events) if x['kind']=='checked_found'),999);proposal=next((i for i,x in enumerate(events) if x['kind']=='proposal'),-1);x=events[found] if found<len(events) else {};ok=found<proposal and x.get('own_repository') and x.get('primary_tool_contract') and x.get('governing_adrs') and set(x.get('required_inaccessible',[]))<=set(x.get('disclosed_inaccessible',[]))\nelif kind=='counts':\n expected=json.loads(Path(sys.argv[3]).read_text());ok=set(a)==set(expected) and a.get('limit')==expected['limit'] and len(a.get('rows',[]))==3\n for x,y in zip(a.get('rows',[]),expected['rows']):\n  ok=ok and set(x)==set(y) and all(type(v)==int and v>=0 for v in x.values()) and x.get('state_read_from_committed_branch')==1 and x.get('state_files_read',0)>0\nelse:raise ValueError(kind)\nprint(json.dumps({'accepted':bool(ok),'limit':'Controlled evidence validation, not model-behavior enforcement.'}));sys.exit(0 if ok else 1)\n''')
def evidence_case(name,kind,obj,reject=False):
    path=a.scratch/(name+'.json');path.write_text(json.dumps(obj))
    args=['python3','-B',str(checker),kind,str(path)]
    if kind=='counts':args.append(str(e/'adopter-counts.json'))
    run(name,args,reject)

evidence_case('AC2-positive-observation','replay',observation)
x=copy.deepcopy(observation);x['events'].reverse();evidence_case('AC2-proposal-before-findings','replay',x,True)
x=copy.deepcopy(observation);x['events'][0]['primary_tool_contract']=False;evidence_case('AC2-sibling-as-contract','replay',x,True)
x=copy.deepcopy(observation);x['events'][0]['required_inaccessible']=['synthetic-required-source'];evidence_case('AC2-undisclosed-inaccessible-source','replay',x,True)
counts=json.loads((e/'adopter-counts.json').read_text())
evidence_case('AC3-positive-public-schema','counts',counts)
x=copy.deepcopy(counts);x['rows'][0]['private_task_title']='synthetic private title sentinel';evidence_case('AC3-raw-private-field','counts',x,True)
x=copy.deepcopy(counts);x['rows'][0]['state_read_from_committed_branch']=0;x['rows'][0]['state_files_read']=0;evidence_case('AC3-empty-local-state-as-absence','counts',x,True)
# An input fingerprint control uses a synthetic fixture, never a private source.
fixture=a.scratch/'readonly-source.txt';fixture.write_text('synthetic original source\n')
fp=a.scratch/'input_guard.py';fp.write_text("import hashlib,sys\nfrom pathlib import Path\np=Path(sys.argv[1]);ok=hashlib.sha256(p.read_bytes()).hexdigest()==sys.argv[2];print('input unchanged:',ok);sys.exit(0 if ok else 1)\n")
import hashlib
before=hashlib.sha256(fixture.read_bytes()).hexdigest()
run('AC3-positive-input-fingerprint',['python3','-B',str(fp),str(fixture),before])
fixture.write_text('synthetic changed source\n')
run('AC3-mutated-input',['python3','-B',str(fp),str(fixture),before],True)

run('AC4-positive-product-scope',probe('scope'))
extra=r/'kc-dev-flow-2/disallowed-probe.txt';extra.write_text('disallowed permanent probe\n')
subprocess.run(['git','-C',str(r),'add','-N','--','kc-dev-flow-2/disallowed-probe.txt'],check=True)
try:run('AC4-extra-package-file',probe('scope'),True)
finally:
    subprocess.run(['git','-C',str(r),'reset','--','kc-dev-flow-2/disallowed-probe.txt'],capture_output=True,check=True);extra.unlink()
cost=probe('cost_guard')+['--expected',str(e/'reading-cost.json')]
run('AC4-positive-reading-disclosure',cost)
mutate('AC4-changed-FO-source','kc-dev-flow-2/references/sd/workflow.md',lambda s:s+'\nNew FO obligation.\n',cost)
mutate('AC4-hidden-worker-text',implementation,lambda s:s+'\nAn undisclosed additional worker obligation.\n',cost)

lint=['python3','-B',str(r/'kc-dev-flow-2/scripts/lint-skills.py')]
run('AC5-positive-lint',lint)
mutate('AC5-broken-link',ideation,lambda s:s.replace('../implementation/principles.md','../implementation/not-present.md'),probe('routing'))
mutate('AC5-broken-profile-route','kc-dev-flow-2/skills/ideation/SKILL.md',lambda s:s.replace('| poc | skip |','| poc | active |'),lint)
task=r/'evidence-task.md';task.write_text(a.task.read_text())
design=['python3','-B',str(a.loaded_package/'scripts/design_surfaces.py'),'check',str(task)]
run('AC5-positive-design-copy',design)
old=task.read_text();import re
task.write_text(re.sub(r'\*\*AC-(\d+)\*\*',r'AC-\1',old));run('AC5-unusable-AC-grammar',design,True);task.unlink()
poc=a.scratch/'poc_guard.py';poc.write_text("import sys\nfrom pathlib import Path\nsys.path.insert(0,sys.argv[1]);from poc_readme import derive\ns=derive(Path(sys.argv[2]).read_text());ok='- name: ideation' not in s and '### `ideation`' not in s;print('POC omits ideation:',ok);sys.exit(0 if ok else 1)\n")
poc_cmd=['python3','-B',str(poc),str(r/'kc-dev-flow-2/scripts'),str(r/'kc-dev-flow-2/references/sd/workflow.md')]
run('AC5-positive-POC-graph',poc_cmd)
mutate('AC5-POC-gains-ideation','kc-dev-flow-2/scripts/poc_readme.py',lambda s:s+'\nderive = lambda text: text\n',poc_cmd)
adr='docs/adr/0083-workers-check-the-existing-chain-before-new-work.md'
adr_cmd=['python3','-B',str(a.loaded_package/'scripts/adr_lint.py'),'docs/adr','--since',base,'--require','0083']
run('AC5-positive-required-ADR',adr_cmd)
mutate('AC5-required-check-fails',adr,lambda s:s.replace('**Recommended:**','Recommended:'),adr_cmd)

(e/'mutation-results.json').write_text(json.dumps(results,indent=2)+'\n')
(e/'mutation-tests.json').write_text(json.dumps([{'name':x['name'],'status':x['status'],'message':f"expected exit {x['expected_exit']}; observed {x['actual_exit']}; {x['output']}"} for x in results],indent=2)+'\n')
assert not subprocess.check_output(['git','-C',str(r),'status','--porcelain'],text=True).strip(), 'fixture product bytes not restored'
print(json.dumps({'checks':len(results),'failed':sum(x['status']=='failed' for x in results),'limit':'Source and recorded-evidence mutations, not independent agent behavior.'}))
sys.exit(1 if any(x['status']=='failed' for x in results) else 0)
