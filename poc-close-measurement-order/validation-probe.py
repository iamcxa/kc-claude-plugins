import hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path
wt, evidence = map(Path, sys.argv[1:3])
sd = Path("/Users/kent/.local/bin/spacedock")
guard = wt / "kc-dev-flow/scripts/poc-close-guard.py"
source = wt / "kc-dev-flow/scripts/poc-close-guard.test.py"
ns = {"__file__": str(source)}
exec(source.read_text().split('with tempfile.TemporaryDirectory(prefix="poc-close-guard-") as temporary:')[0], ns)
root = Path(tempfile.mkdtemp(prefix="poc-independent-recovery-"))
repo = root / "repo"; workflow = repo / "docs/dev"; workflow.mkdir(parents=True)
holder = workflow / ".spacedock-state"; remote = root / "remote.git"
history=[]
env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
def run(*args, input=None, ok=True):
    r=subprocess.run(list(map(str,args)),input=input,text=True,capture_output=True,cwd=repo,env=env)
    history.append({"argv":list(map(str,args)),"rc":r.returncode,"stdout":r.stdout,"stderr":r.stderr})
    if ok: assert r.returncode == 0, history[-1]
    return r
def git(*args, at=repo): return run("git","-C",at,*args)
def native(*args, **kw): return run(sd,*args,"--workflow-dir",workflow,**kw)
def close(phase, target, *args, **kw): return run(sys.executable,guard,"--workflow-dir",workflow,"--work-item",target,"--spacedock-bin",sd,phase,*args,**kw)
def fingerprint(path):
    return {str(p.relative_to(path)):hashlib.sha256(p.read_bytes()).hexdigest() for p in path.rglob("*") if p.is_file()}
def front(path): return path.read_text().split("\n---\n",1)[0]
(workflow/"README.md").write_text("""---
commissioned-by: spacedock@0.27.2
entity-type: task
entity-label: task
entity-label-plural: tasks
id-style: sd-b32
state: .spacedock-state
trunk: main
stages:
  states:
    - name: backlog
      initial: true
      gate: true
    - name: implementation
    - name: validation
      gate: true
      feedback-to: implementation
    - name: done
      terminal: true
---
# Independent recovery fixture
""")
(repo/".gitignore").write_text("docs/dev/.spacedock-state/\n")
git("init","-qb","main");git("config","user.name","Independent synthetic validation");git("config","user.email","validation@example.invalid")
git("add",".gitignore","docs/dev/README.md");git("commit","-qm","synthetic workflow")
run("git","init","--bare",remote);git("remote","add","origin",remote);git("push","-u","origin","main")
git("worktree","add","--detach",holder,"HEAD");git("switch","--orphan","spacedock-state/dev",at=holder)
(holder/".keep").touch();git("add",".keep",at=holder);git("commit","-qm","synthetic state",at=holder);git("push","-u","origin","spacedock-state/dev",at=holder)
body=ns["pending_item_text"]().replace("id: poc123exact\n","")
body += "\n## Stage Report: implementation\n\n- DONE: Local synthetic observation.\n  Recovery probe only, not a real outcome approval.\n"
native("new","probe",input=body)
item=Path(json.loads(native("status","--resolve","probe","--json").stdout)["path"])
native("state","commit","probe")
assert json.loads(close("review",item).stdout)["proof_stage"] == "implementation"
assert "state=open" in close("prepare",item,"--question","Synthetic recovery only?","--artifact",item,"--summary","Independent local fixture").stdout
before=item.read_bytes();assert close("consume",item,ok=False).returncode != 0;assert item.read_bytes()==before
native("gate","record","probe","--decision","approve","--actor","person:captain","--reason","SYNTHETIC TEST ONLY, no Kent approval")
briefing=next(holder.rglob("index.json"));frozen=briefing.read_bytes()
briefing.write_bytes(frozen.replace(b"Synthetic recovery only?",b"Tampered recovery?"))
assert "frozen digest" in close("consume",item,ok=False).stderr
briefing.write_bytes(frozen)
item.write_text(item.read_text().replace("captain_wait_seconds: pending","captain_wait_seconds: 17"));native("state","commit","probe")
assert "route=approved-awaiting-merge" in close("consume",item).stdout
native("merge","guard","probe","--verdict","passed","--json")
archived=next(holder.rglob("probe.md"));assert "_archive" in str(archived)
frozen_after=next(holder.rglob("index.json"));assert frozen_after.read_bytes()==frozen
historical_front=front(archived)
for status in ("pending","failed"):
    b=archived.read_text().replace("cleanup_status: pending",f"cleanup_status: {status}")
    archived.write_text(b)
    before=fingerprint(root);r=close("check-final",archived,ok=False)
    assert r.returncode==2 and f"cleanup_status={status}" in r.stderr
    assert fingerprint(root)==before, "read-only refusal changed fixture bytes"
archived.write_text(archived.read_text().replace("cleanup_status: failed","cleanup_status: complete").replace("terminal_cleanup_seconds: pending","terminal_cleanup_seconds: 6"))
assert front(archived)==historical_front
assert native("state","commit","probe",ok=False).returncode != 0
# Independent gap: actual publication failure after the final body commit, followed by a fresh process retry.
git("add",archived,at=holder);git("commit","-qm","synthetic final measurements","--",archived,at=holder)
local_head=git("rev-parse","HEAD",at=holder).stdout.strip()
remote_before=run("git","--git-dir",remote,"rev-parse","refs/heads/spacedock-state/dev").stdout.strip()
assert local_head != remote_before
hook=remote/"hooks/pre-receive";hook.write_text("#!/bin/sh\nprintf 'synthetic publication interruption\\n' >&2\nexit 1\n");hook.chmod(0o755)
refused=native("state","commit","probe",ok=False)
assert refused.returncode!=0 and "synthetic publication interruption" in refused.stderr+refused.stdout
assert run("git","--git-dir",remote,"rev-parse","refs/heads/spacedock-state/dev").stdout.strip()==remote_before
assert front(archived)==historical_front and frozen_after.read_bytes()==frozen
hook.unlink()
native("state","commit","probe")
assert run("git","--git-dir",remote,"rev-parse","refs/heads/spacedock-state/dev").stdout.strip()==local_head
before=fingerprint(root);assert json.loads(close("check-final",archived).stdout)["close_complete"];assert fingerprint(root)==before
# A second independent checkout sees final bytes without consuming or recording another approval.
clone=root/"reader";run("git","clone","--branch","spacedock-state/dev",remote,clone)
copy=clone/archived.relative_to(holder);assert copy.read_bytes()==archived.read_bytes()
assert front(copy)==historical_front
before=fingerprint(root);assert json.loads(close("check-final",copy).stdout)["close_complete"];assert fingerprint(root)==before
# Explicit archived path cannot reuse the terminal application; do not rely on an absent active slug.
assert native("gate","consume",archived,ok=False).returncode!=0
for old,new,expected in (("status: done","status: validation","requires work item status done"),("cleanup_status: complete","cleanup_status: failed","cleanup_status=failed"),("captain_wait_seconds: 17","captain_wait_seconds: pending","captain_wait_seconds=pending"),("terminal_cleanup_seconds: 6","terminal_cleanup_seconds: -1","non-negative integer")):
    candidate=root/"adversarial.md";candidate.write_text(copy.read_text().replace(old,new))
    before=fingerprint(root);r=close("check-final",candidate,ok=False)
    assert r.returncode==2 and expected in r.stderr,(old,r.stderr)
    assert fingerprint(root)==before
assert sum(c["argv"][1:3]==["gate","record"] for c in history)==1
assert frozen_after.read_bytes()==frozen and front(archived)==historical_front
result={"result":"PASS","fixture_root":str(root),"synthetic_only":True,"additional_claim":"publication interruption after final-body commit resumes without approval/cloud rerun; complete fixture byte hash unchanged by final checker","approval_records":1,"cloud_runs":0,"frozen_briefing_sha256":hashlib.sha256(frozen).hexdigest(),"archived_frontmatter_sha256":hashlib.sha256(historical_front.encode()).hexdigest(),"published_final_head":local_head,"commands":history}
evidence.write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!="commands"},indent=2))
