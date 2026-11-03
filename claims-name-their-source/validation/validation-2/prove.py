import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import types

WT=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-claims-name-their-source/.context/validation-777-cycle2')
HERE=Path(__file__).resolve().parent
BASE='128fe3e3fed70fa64ded8657f5a1b36933af3ced'
root=WT/'.context/mutation/kc-dev-flow-2'
if root.exists(): shutil.rmtree(root)
shutil.copytree(WT/'kc-dev-flow-2',root,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
support=root.parent/'scripts'
if support.exists(): shutil.rmtree(support)
shutil.copytree(WT/'scripts',support,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
results=[]

def run(name,argv,expected):
    proc=subprocess.run(argv,cwd=root/'scripts',capture_output=True,text=True)
    (HERE/f'{name}.log').write_text(proc.stdout+proc.stderr)
    results.append({'name':name,'exit':proc.returncode,'expected':expected,'matched':proc.returncode==expected})
    assert proc.returncode==expected,(name,proc.stdout,proc.stderr)
    return proc.stdout+proc.stderr

lint=root/'scripts/lint-skills.py'
original=lint.read_text()
start=original.index('    dict(delta=55, why="numbers and factual claims')
stop=original.index('\n]',start)
lint.write_text(original[:start]+original[stop:])
out=run('mutation-budget',[sys.executable,'-B',str(lint),'--root',str(root)],1)
assert 'raise step of 55' in out
lint.write_text(original)

delivery=root/'scripts/delivery_gate.py'
original=delivery.read_text()
delivery.write_text(original.replace('def check(args):\n    emit(CLAIM_SOURCE)\n','def check(args):\n',1))
run('mutation-check',[sys.executable,'-B','-m','unittest','test_delivery_gate.DeliveryGateTests.test_claim_source_reminder_on_pass_hold_and_unreadable_input'],1)
run('mutation-question-control',[sys.executable,'-B','-m','unittest','test_delivery_gate.QuestionTests.test_claim_source_reminder_on_pass_hold_and_unreadable_input'],0)
delivery.write_text(original)

workflow=root/'references/sd/workflow.md'
original=workflow.read_text()
workflow.write_text(original.replace('a claim carries the same source after the sentence that answers him','a claim names the same source after the sentence that answers him'))
out=run('mutation-chat',[sys.executable,'-B',str(lint),'--root',str(root)],1)
assert 'chat-only rule' in out and 'is not in references/sd/workflow.md' in out
workflow.write_text(original)
run('lint-control',[sys.executable,'-B',str(lint),'--root',str(root)],0)
(HERE/'mutation-results.json').write_text(json.dumps(results,indent=2)+'\n')

def old(path):
    return subprocess.check_output(['git','-C',str(WT),'show',f'{BASE}:{path}'],text=True)

wf='kc-dev-flow-2/references/sd/workflow.md'
mod='kc-dev-flow-2/references/sd/mods/kc-dev-flow-2.md'
counts={'command':'python3 -B prove.py; independent str.split() recount, source blobs read by git show',
        'date':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'base':BASE,'workflow':{'base':len(old(wf).split()),'candidate':len((WT/wf).read_text().split())},
        'mod':{'base':len(old(mod).split()),'candidate':len((WT/mod).read_text().split())}}
sys.path.insert(0,str(WT/'kc-dev-flow-2/scripts'))
import test_delivery_gate as fixtures
question=fixtures.QuestionTests().ask('Admit it?')
check=fixtures.run_check()
base_module=types.ModuleType('base_delivery_gate')
base_module.__file__=str(WT/'kc-dev-flow-2/scripts/delivery_gate.py')
exec(compile(old('kc-dev-flow-2/scripts/delivery_gate.py'),base_module.__file__,'exec'),base_module.__dict__)
base_question=fixtures.QuestionTests().ask('Admit it?',module=base_module)
base_check=fixtures.run_variant(base_module)
(HERE/'base-question-output.txt').write_text(base_question[1])
(HERE/'base-check-output.txt').write_text(base_check.out)
(HERE/'question-output.txt').write_text(question[1])
(HERE/'check-output.txt').write_text(check.out)
counts['printed_reminder_words']=len(fixtures.CLAIM_SOURCE.split())
counts['question']={'base_words':len(base_question[1].split()),'candidate_words':len(question[1].split()),'exit':question[0],'base_exit':base_question[0]}
counts['check']={'base_words':len(base_check.out.split()),'candidate_words':len(check.out.split()),'exit':check.code,'base_exit':base_check.code,'ask_last':check.out.splitlines()[-1]==fixtures.gate.ASK}
counts['unchanged_modes']={p:old(p)==(WT/p).read_text() for p in ['kc-dev-flow-2/scripts/pr_watch.py','kc-dev-flow-2/scripts/design_surfaces.py',mod]}
assert counts['workflow']['candidate']-counts['workflow']['base']==55
assert counts['printed_reminder_words']==27
assert all(counts['unchanged_modes'].values())
assert question[0]==0 and check.code==0
(HERE/'word-counts.json').write_text(json.dumps(counts,indent=2)+'\n')
print('budget, check-only emission and chat-phrase mutations caught; independent counts retained')
