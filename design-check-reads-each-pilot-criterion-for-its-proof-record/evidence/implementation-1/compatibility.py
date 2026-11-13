import concurrent.futures,json,os,re,subprocess,sys
from pathlib import Path
wt,scratch=map(Path,sys.argv[1:])
base=scratch/"base/kc-dev-flow-2/scripts/design_surfaces.py"
candidate=wt/"kc-dev-flow-2/scripts/design_surfaces.py"
env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1","TMPDIR":str(scratch/"tmp")}
def compare(item):
    label,path,seed=item
    commands=[]
    for checker in (base,candidate):
        done=subprocess.run([sys.executable,"-B",str(checker),"check",*(["--seed"] if seed else []),str(path)],
                            capture_output=True,text=True,env=env)
        commands.append((done.returncode,done.stdout,done.stderr))
    old,new=commands
    added=[line for line in new[1].splitlines() if line not in old[1].splitlines() and "design surfaces presentable" not in line]
    removed=[line for line in old[1].splitlines() if line not in new[1].splitlines() and "design surfaces presentable" not in line]
    proof=[line for line in new[1].splitlines() if "Pilot criterion" in line]
    text=path.read_text()
    approved=bool(re.search(r"stage: ideation\n(?:(?:[ \t]+.*|)\n)*?[ \t]+decision: approve",text))
    archived="_archive" in path.parts
    expected=not added or all("Pilot criterion" in line for line in added)
    expected=expected and not removed and not (seed and proof) and not ((approved or archived) and proof)
    return dict(label=label,seed=seed,changed=old!=new,exit_changed=old[0]!=new[0],added_proof=bool(proof),
                approved=approved,archived=archived,expected=expected,
                private=dict(path=str(path),base=old,candidate=new) if not expected else None)
items=[]
for root in sorted((scratch/"corpora").iterdir()):
    for path in sorted(list(root.glob("*.md"))+list(root.glob("_archive/*.md"))):
        items.extend((root.name,path,seed) for seed in (False,True))
summary={}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    results=list(pool.map(compare,items))
for result in results:
    key=result["label"]+(" check --seed" if result["seed"] else " check")
    counts=summary.setdefault(key,dict(tasks=0,changed=0,exit_changed=0,proof_refusals=0,approved=0,archived=0,unexpected=0))
    for field,value in dict(tasks=1,changed=result["changed"],exit_changed=result["exit_changed"],
                            proof_refusals=result["added_proof"],approved=result["approved"],
                            archived=result["archived"],unexpected=not result["expected"]).items():
        counts[field]+=value
(scratch/"compatibility.json").write_text(json.dumps(summary,indent=2))
(scratch/"private-compatibility-unexpected.json").write_text(json.dumps([r for r in results if not r["expected"]],indent=2))
print(json.dumps(summary,indent=2))
sys.exit(0 if all(result["expected"] for result in results) else 1)
