import hashlib,json,os,shutil,subprocess
from pathlib import Path
WT=Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-new-work-checks-what-exists-first")
STATE=Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state")
E=Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/new-work-checks-what-exists-first/validation-2")
R=Path("/tmp/validate-new-work-cycle2-20261113-022341")
adopter_root = os.environ["VALIDATION_ADOPTER_ROOT"]
HEAD="1fc2f05f88b18a62d4eda598158ffa385df9fae8"
SEED="353e835dd199fe02e0c1dc174be95cb75da79080"
def run(argv,cwd=WT):
    return subprocess.run(list(map(str,argv)),cwd=cwd,check=True,capture_output=True).stdout
assert run(["git","-C",WT,"rev-parse","HEAD"]).decode().strip()==HEAD
assert not run(["git","-C",WT,"status","--porcelain"]).strip()
assert not R.exists()
R.mkdir(); E.mkdir(exist_ok=True)
C=R/"candidate"; C.mkdir()
run(["tar","-x","-C",C],cwd=WT) if False else None
archive=run(["git","-C",WT,"archive",HEAD])
subprocess.run(["tar","-x","-C",str(C)],input=archive,check=True)
W=R/"wf"; S=W/".spacedock-state"; S.mkdir(parents=True)
(W/"README.md").write_bytes((C/"kc-dev-flow-2/references/sd/workflow.md").read_bytes())
slug="design-surfaces-task-dir-crash"
(S/(slug+".md")).write_bytes(run(["git","-C",STATE,"show",SEED+":"+slug+".md"]))
(S/slug/"dispatch").mkdir(parents=True)
run(["git","init","-b","main",R])
run(["git","init","-b","fixture-state",S])
run(["git","-C",S,"add",slug+".md"])
run(["git","-C",S,"-c","user.name=Validation fixture","-c","user.email=fixture@localhost","commit","-m","Fixture seed"])
O=R/"subject-output"; O.mkdir()
P=C/"kc-dev-flow-2"
scope=f"""Package root: {P}
TEST HARNESS (isolated replay): read {P}/skills/ideation/SKILL.md and follow it, resolving every package path against {P}. The CODE root is {C}, exported from the selected revision and intentionally without Git metadata. The state snapshot is {S}. Work read-only; do not change state, product, private repositories, Git metadata or remotes, and do not start servers, browsers or databases. Save your observations and proposal as separate files in {O} as you work; scratch reproductions may be created only under {O}. The only authorized real adopter root is {adopter_root}, read-only; any persisted evidence from it must contain counts only, no names, titles, rulings or logs. No application unit/integration/e2e run is required for this ideation. Do not spawn agents or contact other sessions. Completion is one final reply to your caller. These harness limits override generated commit/push instructions.
"""
(R/"scope.txt").write_text(scope)
(R/"checklist.txt").write_text("Prepare the smallest ideation proposal for the assigned task Scope. Do not implement, write another task, contact another session or perform external writes.\n")
cmd=["/Users/kent/.local/bin/spacedock","dispatch","build","--workflow-dir",str(W),"--entity-path",str(S/(slug+".md")),"--stage","ideation","--host","codex","--checklist-file",str(R/"checklist.txt"),"--scope-notes-file",str(R/"scope.txt")]
r=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
(E/"cold-dispatch-build.log").write_text(r.stdout+r.stderr)
assert r.returncode==0,(r.returncode,r.stderr)
envelope=json.loads(r.stdout); generated=Path(envelope["dispatch_file_path"])
shutil.copyfile(generated,R/"dispatch.md")
assert f"Package root: {P}\n" in (R/"dispatch.md").read_text()
assert (P/"skills/ideation/SKILL.md").is_file()
manifest={}
for f in sorted(C.rglob("*")):
    if f.is_file() and not f.is_symlink():
        manifest[str(f.relative_to(C))]=hashlib.sha256(f.read_bytes()).hexdigest()
        f.chmod(f.stat().st_mode & ~0o222)
for f in sorted(C.rglob("*"),reverse=True):
    if f.is_dir(): f.chmod(f.stat().st_mode & ~0o222)
C.chmod(C.stat().st_mode & ~0o222)
(E/"archive-before.json").write_text(json.dumps(manifest,indent=2)+"\n")
for name in ["dispatch.md","scope.txt","checklist.txt"]:
    (E/name).write_text((R/name).read_text().replace(adopter_root, "<authorized-adopter-1>"))
(E/"seed-task.md").write_bytes((S/(slug+".md")).read_bytes())
(E/"setup.json").write_text(json.dumps({"head":HEAD,"seed_state_commit":SEED,"command":cmd,"exit":r.returncode,"package_root":str(P),"package_skill_exists":True,"source_files":len(manifest),"candidate_write_bits_removed":True,"generated_dispatch":str(generated),"generated_dispatch_sha256":hashlib.sha256(generated.read_bytes()).hexdigest(),"scratch":str(R),"history":"none","neutral_prompt":"No criterion wording or desired checked/found sequence added to the subject prompt.","mutation_controls":"none on cold export"},indent=2)+"\n")
print(json.dumps({"dispatch":str(R/"dispatch.md"),"package_root_exists":True,"export_files":len(manifest),"generated":str(generated)}))

