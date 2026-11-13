from pathlib import Path
import json, os, subprocess
WT=Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-merge-ask-is-produced-from-records")
SCR=Path(__file__).parent
PKG=Path("/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0")
WF=WT.parents[1]/"docs/dev2"
STATE=WF/".spacedock-state"
TASK=STATE/"merge-ask-is-produced-from-records.md"
BASE="bfc53d82510006b52baf41569c1e25176e99d87a"
commands=[
("role-triggers",["python3","-B",str(PKG/"scripts/role_triggers.py"),str(STATE),TASK.stem]),
("lint",["python3","-B","kc-dev-flow-2/scripts/lint-skills.py"]),
("adr-lint",["python3","-B",str(PKG/"scripts/adr_lint.py"),"docs/adr","--since",BASE]),
("number-guards",["python3","-B",str(PKG/"scripts/number_guards.py"),"check","--workflow-dir",str(WF),"--task",str(TASK)]),
("comment-ratio",["python3","-B",str(PKG/"scripts/comment_ratio.py"),BASE,"HEAD","--workflow-dir",str(WF)]),
("design-surfaces",["python3","-B",str(PKG/"scripts/design_surfaces.py"),"check",str(TASK)]),
("doc-impact",["python3","-B",str(PKG/"scripts/doc_impact.py"),BASE,"HEAD"]),
("diff-check",["git","diff","--check",BASE,"HEAD"]),
("dispatch-pins",["python3","-B",str(SCR/"dispatch_pin_check.py")])]
rows=[]
for name,cmd in commands:
 p=subprocess.run(cmd,cwd=WT,capture_output=True,text=True,env={**os.environ,"TMPDIR":str(SCR),"PYTHONDONTWRITEBYTECODE":"1"})
 path=name+"-final.log";(SCR/path).write_text(p.stdout+p.stderr)
 rows.append(dict(name=name,command=cmd,exit=p.returncode,output=path))
(SCR/"final-checks.json").write_text(json.dumps(rows,indent=2)+"\n")
assert all(r["exit"]==(1 if r["name"]=="dispatch-pins" else 0) for r in rows),rows
