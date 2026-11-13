import json,subprocess,sys,shutil
from pathlib import Path
root=Path(__file__).parent
base=Path("/tmp/dev2")
before={p.resolve() for p in base.iterdir()}
results=[]
for suite in ("dispatch-stage","sd-dispatch"):
    code=subprocess.call(["python3","-B",str(root/"run_checks.py"),suite])
    created=sorted(p for p in base.iterdir() if p.resolve() not in before and p.name.startswith("dispatch-code-"))
    rows=[]
    for path in created:
        files=[p for p in path.rglob("*") if p.is_file()]
        owners=[json.loads(p.read_text()) for p in files if p.name==".owner.json"]
        expected="Package root: "+'<worktree>'+"/kc-dev-flow-2"
        note=any(expected in p.read_text(errors="replace") for p in files if p.suffix in (".txt",".md"))
        own=bool(owners) and all(x.get("task","").startswith("dispatch-fixture-") for x in owners) and note
        rows.append(dict(root=path.name,files=len(files),ownership_verified=own,removed=False))
        if own:
            shutil.rmtree(path)
            rows[-1]["removed"]=True
    remain=[p.name for p in base.iterdir() if p.resolve() not in before and p.name.startswith("dispatch-code-")]
    results.append(dict(suite=suite,exit=code,left_after_suite=len(created),roots=rows,remaining=remain))
    (root/"synthetic-cleanup.json").write_text(json.dumps(results,indent=2))
    print(suite,"exit",code,"left",len(created),"removed",sum(x["removed"] for x in rows),"remaining",len(remain),flush=True)
    if code or remain: sys.exit(1)
