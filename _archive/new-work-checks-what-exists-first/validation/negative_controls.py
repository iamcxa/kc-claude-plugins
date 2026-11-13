"""Independent replay of saved source/evidence falsifiers on archive copies.
Not a behavioral grader. Paths are arguments; private source records are not copied.
"""
import argparse,contextlib,copy,io,json,os,re,runpy,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser()
for n in ("scratch","evidence","implementation","package","task"): p.add_argument("--"+n,type=Path,required=True)
a=p.parse_args(); root=a.scratch/"candidate"; baseline=a.scratch/"base"; results=[]
mod=runpy.run_path(str(a.implementation/"new_work_check.py"))
def source(repo,ref,path):
    return ((baseline if ref=="BASE" else root)/"kc-dev-flow-2"/path).read_text()
def git(repo,*args):
    assert args[0]=="diff",args
    b=baseline/"kc-dev-flow-2"; c=root/"kc-dev-flow-2"
    paths={x.relative_to(b) for x in b.rglob("*") if x.is_file()}|{x.relative_to(c) for x in c.rglob("*") if x.is_file()}
    return "\n".join("kc-dev-flow-2/"+str(x) for x in sorted(paths)
      if not (b/x).is_file() or not (c/x).is_file() or (b/x).read_bytes()!=(c/x).read_bytes())
mod["routing"].__globals__.update(source=source,git=git)
args=argparse.Namespace(repo=root,ref="CANDIDATE",base="BASE")
def probe(mode):
    return lambda: mod[mode](args)
logs=a.evidence/"controls";logs.mkdir(exist_ok=True)
def run(name,fn,want=0):
    stream=io.StringIO()
    with contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):
        try: rc=fn()
        except Exception as exc: print(type(exc).__name__,str(exc));rc=2
    (logs/(name+".log")).write_text(stream.getvalue())
    results.append(dict(name=name,status="passed" if rc==want else "failed",expected_exit=want,actual_exit=rc,output="controls/"+name+".log"))
def command(argv):
    def f():
        r=subprocess.run(argv,cwd=root,capture_output=True,text=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",TMPDIR=str(a.scratch)))
        print(r.stdout+r.stderr,end="");return r.returncode
    return f
def mutate(name,path,fn,check):
    path=root/path; old=path.read_bytes()
    try: path.write_text(fn(old.decode()));run(name,check,1)
    finally:path.write_bytes(old)
ide="kc-dev-flow-2/skills/ideation/principles.md"; imp="kc-dev-flow-2/skills/implementation/principles.md"
run("AC1-original",probe("routing"))
mutate("AC1-unlink-ideation",ide,lambda x:x.replace("#before-new-work","#existing-code-capability-check"),probe("routing"))
mutate("AC1-remove-home",imp,lambda x:x.replace("## Before new work","## Removed home"),probe("routing"))
mutate("AC1-change-retained-audit",imp,lambda x:x.replace("Skip greenfield work","Skip all work"),probe("routing"))
record=json.loads((a.implementation/"replay-result.json").read_text())
guard=a.implementation/"evidence_guard.py"
def record_case(name,obj,want,kind="replay"):
    path=a.scratch/(name+".json");path.write_text(json.dumps(obj))
    argv=["python3","-B",str(guard),kind,str(path)]
    if kind=="counts":argv.append(str(a.implementation/"adopter-counts.json"))
    run(name,command(argv),want)
record_case("AC2-original-record",record,0)
x=copy.deepcopy(record);x["events"].reverse();record_case("AC2-proposal-first",x,1)
x=copy.deepcopy(record);x["events"][0]["primary_tool_contract"]=False;record_case("AC2-sibling-as-contract",x,1)
x=copy.deepcopy(record);x["events"][0]["required_inaccessible"]=["unavailable synthetic source"];record_case("AC2-undisclosed-source",x,1)
counts=json.loads((a.implementation/"adopter-counts.json").read_text())
record_case("AC3-original-counts",counts,0,"counts")
x=copy.deepcopy(counts);x["rows"][0]["private_task_title"]="synthetic sentinel";record_case("AC3-private-field",x,1,"counts")
x=copy.deepcopy(counts);x["rows"][0]["state_read_from_committed_branch"]=0;x["rows"][0]["state_files_read"]=0;record_case("AC3-empty-local-is-not-absence",x,1,"counts")
run("AC4-original-scope",probe("scope"))
extra=root/"kc-dev-flow-2/unapproved-fixture.txt";extra.write_text("synthetic")
try:run("AC4-extra-product-file",probe("scope"),1)
finally:extra.unlink()
run("AC4-original-cost",probe("cost"))
mutate("AC4-new-FO-text","kc-dev-flow-2/references/sd/workflow.md",lambda x:x+"\nNew obligation.\n",probe("cost"))
def disclosed_cost():
    expected=json.loads((a.evidence/"reading-cost.json").read_text())
    good=all(len(source(None,"CANDIDATE","skills/"+x["stage"]+"/principles.md").split())==x["probe_words"] for x in expected["worker_principles"])
    print("matches disclosed worker words:",good);return 0 if good else 1
mutate("AC4-undisclosed-worker-text",imp,lambda x:x+"\nAdditional obligation.\n",disclosed_cost)
lint=command(["python3","-B",str(root/"kc-dev-flow-2/scripts/lint-skills.py")])
run("AC5-original-lint",lint)
mutate("AC5-broken-profile","kc-dev-flow-2/skills/ideation/SKILL.md",lambda x:x.replace("| poc | skip |","| poc | active |"),lint)
mutate("AC5-broken-link",ide,lambda x:x.replace("../implementation/principles.md","../implementation/missing.md"),probe("routing"))
task=a.scratch/"control-task.md";task.write_text(a.task.read_text())
design=command(["python3","-B",str(a.package/"scripts/design_surfaces.py"),"check",str(task)])
run("AC5-original-design",design)
task.write_text(re.sub(r"\*\*AC-(\d+)\*\*",r"AC-\1",task.read_text()))
run("AC5-invalid-AC",design,1)
def poc():
    d=runpy.run_path(str(root/"kc-dev-flow-2/scripts/poc_readme.py"))["derive"]((root/"kc-dev-flow-2/references/sd/workflow.md").read_text())
    good="- name: ideation" not in d and "### `ideation`" not in d
    print("POC omits ideation:",good);return 0 if good else 1
run("AC5-original-POC",poc)
mutate("AC5-added-POC-ideation","kc-dev-flow-2/scripts/poc_readme.py",lambda x:x+"\nderive = lambda text: text\n",poc)
adr=command(["python3","-B",str(a.package/"scripts/adr_lint.py"),str(root/"docs/adr"),"--root",str(root),"--require","0083"])
run("AC5-original-ADR",adr)
mutate("AC5-missing-ADR-field","docs/adr/0083-workers-check-the-existing-chain-before-new-work.md",lambda x:x.replace("**Recommended:**","Recommended:"),adr)
(a.evidence/"controls.json").write_text(json.dumps(results,indent=2)+"\n")
print(json.dumps({"controls":len(results),"failed":sum(x["status"]=="failed" for x in results),"negative":sum(x["expected_exit"]==1 for x in results)}))
sys.exit(any(x["status"]=="failed" for x in results))

