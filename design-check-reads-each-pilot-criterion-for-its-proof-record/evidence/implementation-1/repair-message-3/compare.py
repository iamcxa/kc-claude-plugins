import concurrent.futures,contextlib,importlib.util,io,json,sys
from pathlib import Path
MODULES={}
NAMES=("reference","final")
def init(root):
    for name in NAMES:
        path=Path(root)/name/"kc-dev-flow-2/scripts/design_surfaces.py"
        sys.path.insert(0,str(path.parent))
        spec=importlib.util.spec_from_file_location("investigation_"+name.replace("-","_"),path)
        mod=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        MODULES[name]=mod
def run(item):
    label,path,seed=item
    path=Path(path)
    result={}
    for name,mod in MODULES.items():
        output=io.StringIO()
        with contextlib.redirect_stdout(output):
            code=mod.main(["check",*(["--seed"] if seed else []),str(path)])
        result[name]=(code,output.getvalue())
    base=result["reference"]
    body=path.read_text()
    candidate=MODULES["reference"]
    declared=set()
    candidate.check_criteria(path.name,body.splitlines(),[])
    section=candidate.section(body.splitlines(),candidate.AC_HEADING) or []
    declared={found for line in section for found in candidate.AC_DECLARATION.findall(line)}
    covered=set(MODULES["final"].proof_blocks(section))
    return dict(label=label,seed=seed,approved=candidate.design_approved(body),archived="_archive" in path.parts,
      unvisited_by_candidate=len(declared-covered),
      variants={name:dict(changed=result[name]!=base,exit_changed=result[name][0]!=base[0],
         refused_from_pass=base[0]==0 and result[name][0]==1,
         new_proof_lines=len([line for line in result[name][1].splitlines() if "Pilot criterion" in line and line not in base[1].splitlines()]))
         for name in NAMES[1:]},
      private=dict(path=str(path),results=result) if any(result[name]!=base for name in NAMES[1:]) else None)
def main():
    root=Path(__file__).parent
    items=[]
    for folder in sorted((root/"corpora").iterdir()):
        for path in sorted(list(folder.glob("*.md"))+list(folder.glob("_archive/*.md"))):
            items.extend((folder.name,str(path),seed) for seed in (False,True))
    with concurrent.futures.ProcessPoolExecutor(max_workers=4,initializer=init,initargs=(str(root),)) as pool:
        rows=list(pool.map(run,items,chunksize=8))
    summary={}
    for row in rows:
        key=row["label"]+(" check --seed" if row["seed"] else " check")
        counts=summary.setdefault(key,dict(tasks=0,unvisited_by_candidate=0,variants={name:dict(changed=0,exit_changed=0,refused_from_pass=0,new_proof_lines=0,approved_changes=0,archived_changes=0) for name in NAMES[1:]}))
        counts["tasks"]+=1
        counts["unvisited_by_candidate"]+=row["unvisited_by_candidate"]
        for name,values in row["variants"].items():
            for key,value in values.items(): counts["variants"][name][key]+=value
            counts["variants"][name]["approved_changes"]+=values["changed"] and row["approved"]
            counts["variants"][name]["archived_changes"]+=values["changed"] and row["archived"]
    (root/"corpus-comparison.json").write_text(json.dumps(summary,indent=2))
    (root/"private-corpus-diffs.json").write_text(json.dumps([r["private"] for r in rows if r["private"]],indent=2))
    print(json.dumps(summary,indent=2))
if __name__=="__main__": main()
