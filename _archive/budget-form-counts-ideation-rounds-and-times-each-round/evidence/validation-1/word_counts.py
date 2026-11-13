from pathlib import Path
import subprocess, re, json, sys
wt=Path.cwd(); x=Path(sys.argv[1]); state=x/'state'
def count(text): return len(re.findall(r'[a-z0-9<>/_.\-]+',text.lower().replace('`','')))
def output(cmd): return subprocess.check_output(list(map(str,cmd)),text=True)
base=(x/'base/kc-dev-flow-2/references/sd/workflow.md').read_text()
candidate=(wt/'kc-dev-flow-2/references/sd/workflow.md').read_text()
rows=[]
def add(name,before,after):rows.append(dict(moment=name,base=count(before),candidate=count(after),delta=count(after)-count(before)))
rows.append(dict(moment='Workflow lint budget (whitespace words)',base=len(base.split()),candidate=len(candidate.split()),delta=len(candidate.split())-len(base.split())))
add('Startup and resume (normalized words)',base,candidate)
def ideation(text): return text.split('### `ideation`',1)[1].split('### `implementation`',1)[0]
add('Design stage definition, normalized words',ideation(base),ideation(candidate))

for slug,label in [('merge-ask-holds-missing-clauses','Timeline on demand, three-design-round task'),('kc-decision-log-cli','Timeline on demand, thirteen-round task')]:
    texts=[output(['python3','-B',p/'task_timeline.py',state,slug]) for p in (x/'base/kc-dev-flow-2/scripts',wt/'kc-dev-flow-2/scripts')]
    add(label,*texts)
slug='budget-form-counts-ideation-rounds-and-times-each-round'
texts=[output(['python3','-B',p/'role_triggers.py',state,slug]) for p in (x/'base/kc-dev-flow-2/scripts',wt/'kc-dev-flow-2/scripts')]
add('Pilot implementation/check budget line',*texts)
texts=[output(['python3','-B',p/'role_triggers.py',state,slug,'--budget-only']) if i else '' for i,p in enumerate((x/'base/kc-dev-flow-2/scripts',wt/'kc-dev-flow-2/scripts'))]
add('Pilot design dispatch budget line',*texts)
print(json.dumps(rows,indent=2))
