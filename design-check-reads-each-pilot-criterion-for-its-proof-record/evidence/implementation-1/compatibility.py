"""Compare both design-check modes at frozen revisions via their main(argv) entrypoints."""
import concurrent.futures,contextlib,importlib.util,io,json,os,sys
from pathlib import Path
BASE=CANDIDATE=None
def initialize(base,candidate):
    global BASE,CANDIDATE
    def load(name,path):
        sys.path.insert(0,str(Path(path).parent))
        spec=importlib.util.spec_from_file_location(name,path)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    BASE=load("base_design_surfaces",base)
    CANDIDATE=load("candidate_design_surfaces",candidate)
def compare(item):
    label,path,seed=item
    path=Path(path)
    rows=[]
    for module in (BASE,CANDIDATE):
        out=io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                code=module.main(["check",*(["--seed"] if seed else []),str(path)])
            rows.append((code,out.getvalue()))
        except Exception as exc:
            rows.append((2,type(exc).__name__+": "+str(exc)))
    old,new=rows
    proof=[line for line in new[1].splitlines() if "Pilot criterion" in line]
    added=[line for line in new[1].splitlines() if line not in old[1].splitlines()]
    if old[0]==0 and new[0]==1:
        expected=bool(proof) and all("Pilot criterion" in line or line.startswith("scope check not run:") for line in added)
    elif old[0]==new[0]:
        expected=all("Pilot criterion" in line for line in added)
    else:
        expected=False
    approved=CANDIDATE.design_approved(path.read_text())
    archived="_archive" in path.parts
    expected=expected and not (seed and proof) and not ((approved or archived) and proof)
    return dict(label=label,seed=seed,changed=old!=new,exit_changed=old[0]!=new[0],proof=bool(proof),
                approved=approved,archived=archived,expected=expected,
                private=dict(path=str(path),base=old,candidate=new) if not expected else None)
def main():
    wt,scratch=map(Path,sys.argv[1:])
    items=[]
    for root in sorted((scratch/"corpora").iterdir()):
        for path in sorted(list(root.glob("*.md"))+list(root.glob("_archive/*.md"))):
            items.extend((root.name,str(path),seed) for seed in (False,True))
    summary={}
    with concurrent.futures.ProcessPoolExecutor(max_workers=4,initializer=initialize,
        initargs=(str(scratch/"base/kc-dev-flow-2/scripts/design_surfaces.py"),
                  str(scratch/"final/kc-dev-flow-2/scripts/design_surfaces.py"))) as pool:
        results=[]
        for count,row in enumerate(pool.map(compare,items,chunksize=8),1):
            results.append(row)
            if count%100==0: print("Compared modes:",count,"/",len(items),flush=True)
    for result in results:
        key=result["label"]+(" check --seed" if result["seed"] else " check")
        counts=summary.setdefault(key,dict(tasks=0,changed=0,exit_changed=0,proof_refusals=0,approved=0,archived=0,unexpected=0))
        for field,value in dict(tasks=1,changed=result["changed"],exit_changed=result["exit_changed"],
             proof_refusals=result["proof"],approved=result["approved"],archived=result["archived"],
             unexpected=not result["expected"]).items(): counts[field]+=value
    (scratch/"compatibility.json").write_text(json.dumps(summary,indent=2))
    (scratch/"private-compatibility-unexpected.json").write_text(json.dumps([r for r in results if not r["expected"]],indent=2))
    print(json.dumps(summary,indent=2))
    return 0 if all(row["expected"] for row in results) else 1
if __name__=="__main__": sys.exit(main())
