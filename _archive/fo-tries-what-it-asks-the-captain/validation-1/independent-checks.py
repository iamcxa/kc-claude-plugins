import ast, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path
root=Path(os.environ['CAPTAIN_STEPS_WORKTREE'])
out=Path(__file__).parent
base=subprocess.check_output(['git','-C',str(root),'rev-parse','origin/main'],text=True).strip()
def blob(path):
    return subprocess.check_output(['git','-C',str(root),'show',base+':'+path],text=True)
def count(text):
    return len(re.findall(r'\S+',text))
def function(text,name):
    node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name==name)
    return ast.dump(node,include_attributes=False)
workflow='kc-dev-flow-2/references/sd/workflow.md'
old=blob(workflow);new=(root/workflow).read_text()
def passage(text):
    return 'Before the gate, FO runs'+text.split('Before the gate, FO runs',1)[1].split('Before recommending delivery',1)[0]
mod='kc-dev-flow-2/references/sd/mods/kc-dev-flow-2.md'
assert blob(mod)==(root/mod).read_text()
mod_words=count(blob(mod))
section='## Captain steps'+new.split('## Captain steps',1)[1].split('\n## ',1)[0]
rows=[
 {'name':'Workflow','before':count(old),'after':count(new)},
 {'name':'Startup including mod','before':count(old)+mod_words,'after':count(new)+mod_words},
 {'name':'Validation passage','before':count(passage(old)),'after':count(passage(new))},
 {'name':'Captain steps section including heading','before':0,'after':count(section)},
 {'name':'Steps success output','before':0,'after':count('captain steps complete: 3 steps, 1 left to him')}
]
assert [(r['before'],r['after']) for r in rows]==[(5781,5836),(5829,5884),(64,33),(0,86),(0,9)],rows
path='kc-dev-flow-2/scripts/pr_watch.py'
assert blob(path)==(root/path).read_text()
gate='kc-dev-flow-2/scripts/delivery_gate.py'
for name in ('check','write_record'):
    assert function(blob(gate),name)==function((root/gate).read_text(),name)
def ask(text):
    return next(ast.literal_eval(n.value) for n in ast.parse(text).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ASK' for t in n.targets))
assert ask(blob(gate))==ask((root/gate).read_text())
results={'base':base,'mod_words':mod_words,'moments':rows,'unchanged':['idle open PR','idle merged PR','archive','merge ask'],'basis':'pr_watch and mod bytes, check/write_record AST and ASK literal unchanged','pass_line_correction':'9 words; design table says 8, implementation explicitly reports correction'}
(out/'independent-word-counts.json').write_text(json.dumps(results,indent=2)+'\n')
with tempfile.TemporaryDirectory() as tmp:
    pkg=Path(tmp)/'kc-dev-flow-2'
    shutil.copytree(root/'kc-dev-flow-2',pkg,ignore=shutil.ignore_patterns('__pycache__'))
    test=pkg/'scripts/test_delivery_gate.py'
    source=test.read_text();assert source.count('text + captain_record(entry)')==1
    test.write_text(source.replace('text + captain_record(entry)','text'))
    done=subprocess.run([sys.executable,'-B','-m','unittest','test_delivery_gate.QuestionTests.test_both_wordings_in_use_and_a_question_that_names_no_merge_pass'],cwd=pkg/'scripts',text=True,capture_output=True)
    (out/'ac8-falsifier.log').write_text(done.stdout+done.stderr)
    assert done.returncode==1 and 'FAIL:' in done.stderr,(done.returncode,done.stderr)
    (out/'ac8-falsifier.json').write_text(json.dumps({'mutation':'Remove Captain record from legacy question fixture','exit':done.returncode,'expected':'test assertion fails on new intentional hold'},indent=2)+'\n')
print('Independent recount agrees: +55 startup words; idle/archive/merge unchanged. AC-8 missing-record falsifier fails as expected.')
