from pathlib import Path
import json, os, shutil, subprocess, sys
s=Path(__file__).parent
refs=json.loads((s/'evidence/refs.json').read_text())
w=s/'code.git'
f=s/'mutation-fixture'; f.mkdir()
archive=subprocess.run(['git','-C',str(w),'archive',refs['candidate']],stdout=subprocess.PIPE,check=True).stdout
subprocess.run(['tar','-x','-C',str(f)],input=archive,check=True)
env=dict(os.environ,TMPDIR=str(s/'tmp'),PYTHONDONTWRITEBYTECODE='1')
removed=0
for cache in f.rglob('__pycache__'):
    shutil.rmtree(cache); removed+=1
(s/'evidence/mutation-cache.log').write_text(f'Exported committed candidate; __pycache__ directories removed: {removed}; all Python commands use -B; PYTHONDONTWRITEBYTECODE=1.\n')
results=[]
def run(name,cmd):
    with (s/'evidence'/f'mutation-{name}.log').open('w') as log:
        result=subprocess.run(cmd,cwd=f,env=env,stdout=log,stderr=subprocess.STDOUT)
    results.append(dict(name=name,expected_exit=1,exit=result.returncode,status='passed' if result.returncode==1 else 'failed',command=cmd,output=f'mutation-{name}.log'))
    (s/'evidence/mutation-results.json').write_text(json.dumps(results,indent=2)+'\n')
    print(name,'expected 1, actual',result.returncode,flush=True)
workflow=f/'kc-dev-flow-2/references/sd/workflow.md'
original=workflow.read_text()
base=subprocess.check_output(['git','-C',str(w),'show',refs['base']+':kc-dev-flow-2/references/sd/workflow.md'],text=True)
(f/'base-workflow.md').write_text(base)
# Mutate outside the ideation section, which POC derivation preserves.
workflow.write_text(original.replace('# Dev-flow 2', '# Dev-flow 2 changed',1))
# The workflow's actual title can differ; assert this mutation changes it.
if workflow.read_text()==original:
    workflow.write_text(original+'\nPOC visible mutation.\n')
run('AC-2-outside-ideation',['python3','-B','-c',"from pathlib import Path; import sys; sys.path.insert(0,'kc-dev-flow-2/scripts'); from poc_readme import derive; a=derive(Path('base-workflow.md').read_text()); b=derive(Path('kc-dev-flow-2/references/sd/workflow.md').read_text()); print('poc derived equal' if a==b else 'poc derived DIFFER'); sys.exit(a!=b)"])
workflow.write_text(original)
principles=f/'kc-dev-flow-2/skills/implementation/principles.md'
p=principles.read_text()
principles.write_text(p+'\nIdeation writes no repository file, branch or commit; the design, the criteria and any ADR draft live in the task file.\n')
run('AC-3-duplicate-ban',['python3','-B','kc-dev-flow-2/scripts/lint-skills.py'])
principles.write_text(p)
lint=f/'kc-dev-flow-2/scripts/lint-skills.py'; l=lint.read_text()
start=l.index('    # see docs/adr/0084-')
end=l.index('\n]',start)
lint.write_text(l[:start]+l[end:])
run('AC-4-remove-raise',['python3','-B','kc-dev-flow-2/scripts/lint-skills.py'])
lint.write_text(l)
# Add one word; use the same whitespace counter and +66 threshold as AC-5.
workflow.write_text(original+'\nextra\n')
run('AC-5-word-6100',['python3','-B','-c',"from pathlib import Path; import sys; b=len(Path('base-workflow.md').read_text().split()); c=len(Path('kc-dev-flow-2/references/sd/workflow.md').read_text().split()); print(f'FO startup base {b}, candidate {c}, delta {c-b}; maximum delta 66'); sys.exit(c-b>66)"])
workflow.write_text(original)
if any(r['exit']!=r['expected_exit'] for r in results): sys.exit(1)
