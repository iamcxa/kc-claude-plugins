#!/usr/bin/env python3
"""Independent validator probe: identical configured forms through three real entrances."""
import argparse, importlib.util, json, subprocess, sys
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument("--code",type=Path,required=True)
a=p.parse_args()
scripts=a.code/"kc-dev-flow-2/scripts"
sys.path.insert(0,str(scripts))
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,scripts/file)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m
law=module("law_cases","test_laws_check.py")
watch=module("watch_cases","test_pr_watch.py")
lf=law.Base(); wf=watch.TasksTests()
lf.setUp(); wf.setUp()
rows=[]
try:
    repo,before=lf.violating("independent")
    (repo.path/"_archive").mkdir()
    law.git(repo.path,"mv","t.md","_archive/t.md")
    law.git(repo.path,"commit","-m","archive")
    wf.readme(""); wf.task("example",pr="o/r#7")
    template=(wf.workflow/"README.md").read_text()
    forms=[
        ("absent","",False),
        ("empty-comment","extensions: [] # learn",False),
        ("inline-decoy","extensions: [peers] # learn",False),
        ("block-decoy","extensions: # learn\n  # learn\n\n  - peers # learn",False),
        ("inline-trailing","extensions: [peers, 'learn',] # selected",True),
        ("quoted-block","extensions:\n  - \"learn\" # selected",True),
        ("block-blank-comment","extensions: # choice\n  - peers\n\n  # gap\n  - 'learn' # selected",True),
        ("inline-name-boundary","extensions: [learned, pre-learn, peers] # learn",False),
    ]
    for name,field,enabled in forms:
        lf.learn.write_text("---\nentity-type: task\n"+field+"\n---\n")
        (wf.workflow/"README.md").write_text(template.replace("extensions: []",field))
        oc=subprocess.run([sys.executable,"-B",str(scripts/"observer_check.py"),str(repo.path),"t","--readme",str(lf.learn)],capture_output=True,text=True)
        lc,lo=lf.judge(repo,before)
        wc,wo=wf.tasks({"pr view 7":watch.view("MERGED")})
        observed=[oc.returncode==1 and "kc-dev-flow-2:learn" in oc.stdout,lc==1 and "violation: L1" in lo,wc==0 and any("observer report not committed:" in x for x in wo)]
        passed=oc.returncode==1 and lc==(1 if enabled else 0) and wc==0 and observed==[enabled]*3
        rows.append(dict(case=name,expected=enabled,observer=observed[0],laws=observed[1],watcher=observed[2],exits=[oc.returncode,lc,wc],passed=passed))
finally:
    lf.doCleanups(); wf.doCleanups()
print(json.dumps(dict(cases=rows,passed=sum(r["passed"] for r in rows),total=len(rows)),indent=2))
raise SystemExit(0 if all(r["passed"] for r in rows) else 1)

