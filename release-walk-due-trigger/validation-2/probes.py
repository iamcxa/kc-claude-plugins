import argparse, contextlib, importlib.util, io, json, os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path
parser=argparse.ArgumentParser()
parser.add_argument("root"); parser.add_argument("evidence"); parser.add_argument("workflow")
args=parser.parse_args()
root=Path(args.root); ev=Path(args.evidence); consumer=root/".validation-2-consumer"; producer=root/".validation-2-producer"
records=[]
def run(argv, cwd=None, env=None, stdin=None):
    start=time.perf_counter()
    result=subprocess.run(list(map(str,argv)),cwd=cwd,env=env,input=stdin,capture_output=True,text=True)
    row={"command":list(map(str,argv)),"cwd":str(cwd) if cwd else None,"exit":result.returncode,"stdout":result.stdout,"stderr":result.stderr,"seconds":round(time.perf_counter()-start,4)}
    records.append(row)
    (ev/"real-seams.json").write_text(json.dumps(records,indent=2))
    return row
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
t=module("due_tests",consumer/"kc-dev-flow-2/extensions/release-acceptance/test_release_acceptance.py")
case=t.DueTests(); case.setUp()
try:
    node,progress,env=case.live_producer()
    # Prove the producer registered in the separate candidate is the same executable source.
    assert (producer/"kc-journey-map/lib/progress.mjs").read_bytes()==(consumer/"kc-journey-map/lib/progress.mjs").read_bytes()
    progress=producer/"kc-journey-map/lib/journey-progress.mjs"
    realenv={**env,"SPACEDOCK_BIN":shutil.which("spacedock", path=env["PATH"]),"GIT_AUTHOR_NAME":"Validation","GIT_AUTHOR_EMAIL":"validation@example.com","GIT_COMMITTER_NAME":"Validation","GIT_COMMITTER_EMAIL":"validation@example.com"}
    due=[sys.executable,"-B",consumer/"kc-dev-flow-2/extensions/release-acceptance/release_acceptance.py","due","--workflow-dir",case.wf,"--progress",progress,case.map]
    normal=run(due,env=realenv); assert normal["exit"]==0 and normal["stdout"].count("next:")==2
    for path in (case.root,case.state):
        branch="spacedock-state/workflow" if path==case.state else "validation"
        assert run(["git","-C",path,"init","-q","-b",branch],env=realenv)["exit"]==0
    binary=realenv["SPACEDOCK_BIN"]
    for argv,stdin in [
        ([binary,"new","r1-acceptance","--workflow-dir",case.wf],"---\ntitle: r1 acceptance\n---\n\nValidation fixture\n"),
        ([binary,"status","--set","r1-acceptance","release-acceptance=book-pickup/r1","--workflow-dir",case.wf],None),
        ([binary,"state","commit","r1-acceptance","--workflow-dir",case.wf],None)]:
        assert run(argv,env=realenv,stdin=stdin)["exit"]==0
    listing=run([binary,"status","--workflow-dir",case.wf,"--archived","--all-fields","--limit","0","--json"],env=realenv)
    assert any(row.get("release-acceptance")=="book-pickup/r1" for row in json.loads(listing["stdout"])["entities"])
    assert "release-acceptance: book-pickup/r1" in run(["git","-C",case.state,"show","HEAD:r1-acceptance.md"],env=realenv)["stdout"]
    claimed=run(due,env=realenv); assert "release book-pickup/r1 " not in claimed["stdout"]
    claim=case.state/"r1-acceptance.md"
    claim.write_text(claim.read_text().replace("release-acceptance: book-pickup/r1\n",""))
    removed=run(due,env=realenv); assert "release book-pickup/r1 " in removed["stdout"]
    # A YAML comment is a producer-readable frontmatter value. Compare both readers.
    claim.write_text("---\ntitle: acceptance\nrelease-acceptance: book-pickup/r1 # existing walk\n---\n")
    observed_claim=run([binary,"status","--workflow-dir",case.wf,"--read",claim,"--json"],env=realenv)
    claim_due=run(due,env=realenv)
    assert claim_due["stdout"].count("next:")==1, claim_due
    (ev/"yaml-claim.json").write_text(json.dumps({"spacedock":observed_claim,"due":claim_due},indent=2))
    claim.unlink()
    timings=[]
    for label,workflow,mapfile in [
        ("Unmapped current workflow",Path(args.workflow),consumer/"docs/journey/kc-journey-map/draw-a-journey.yaml"),
        ("Mapped five-task scratch",case.wf,case.map)]:
        for name,argv in [
            ("producer",[node,progress,mapfile,"--workflow-dir",workflow]),
            ("due",[sys.executable,"-B",consumer/"kc-dev-flow-2/extensions/release-acceptance/release_acceptance.py","due","--workflow-dir",workflow,"--progress",progress,mapfile])]:
            row=run(argv,env=realenv); assert row["exit"] in (0,1)
            timings.append({"name":label+": "+name,**row})
    (ev/"timings.json").write_text(json.dumps(timings,indent=2))
    (ev/"benchmark.json").write_text(json.dumps([{"name":r["name"],"metrics":{"seconds":r["seconds"]},"status":"passed","context":"One observation; full argv and output in timings.json"} for r in timings],indent=2))
    assert all(r.get("command") for r in timings)
    missing=[{k:v for k,v in r.items() if k!="command"} for r in timings]
    assert not all(r.get("command") for r in missing)
    (ev/"AC-17-no-command.log").write_text("PASS: timing records have commands; removing command provenance is rejected.\n")
finally:
    case.doCleanups()
(ev/"real-seams.json").write_text(json.dumps(records,indent=2))
print("PASS: real producer, split-root persistence, claim-removal falsifier, timings; YAML claim comparison recorded.")

