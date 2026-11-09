import json, os, subprocess, sys, time
from pathlib import Path
root=Path("/tmp/pr818-validation-pP1gbX/candidate")
out=Path("/tmp/pr818-validation-pP1gbX/evidence")
package=Path("/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.36.0")
state=Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state")
task=state/"delivery-gate-ignores-url-paths-and-data-fences"
wt=Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-delivery-gate-ignores-url-paths-and-data-fences")
base="e7c9381f2ae7f11bc715a6f11a3e000b9b807e1e"
head="6f2fe8f33de15cf4e9283bf9dfed185a5691ed57"
gitdir=subprocess.check_output(["git","-C",str(wt),"rev-parse","--absolute-git-dir"],text=True).strip()
env=dict(os.environ,TMPDIR="/tmp",SPACEDOCK_BIN="/Users/kent/.local/bin/spacedock",PYTHONDONTWRITEBYTECODE="1")
commands=[
("fixtures-base",[sys.executable,"-I",str(task/"ideation/fixtures.py"),"/tmp/pr818-validation-pP1gbX/base/kc-dev-flow-2/scripts/delivery_gate.py"],False),
("fixtures-candidate",[sys.executable,"-I",str(task/"ideation/fixtures.py"),str(root/"kc-dev-flow-2/scripts/delivery_gate.py")],False),
("mutations",[sys.executable,"-B",str(task/"implementation-1/run_mutations.py"),str(root),str(out)],False),
("lint-skills",[sys.executable,"-B","kc-dev-flow-2/scripts/lint-skills.py"],False),
("adr-lint",[sys.executable,str(package/"scripts/adr_lint.py"),"docs/adr","--since",base],True),
("number-guards",[sys.executable,str(package/"scripts/number_guards.py"),"check","--repo",str(wt),"--workflow-dir",str(state.parent),"--task",str(task)+".md","--base",base,"--head",head],False),
("comment-ratio",[sys.executable,str(package/"scripts/comment_ratio.py"),base,head,"--repo",str(wt),"--workflow-dir",str(state.parent)],False),
("doc-impact",[sys.executable,str(package/"scripts/doc_impact.py"),base,head,"--repo",str(wt),"--json"],False),
("design-surfaces",[sys.executable,str(package/"scripts/design_surfaces.py"),"check",str(task)+".md"],False),
("dispatch-records",[sys.executable,str(package/"scripts/dispatch_records.py"),str(task)],False),
("diff-check",["git","-C",str(wt),"diff","--check",base,head],False),
]
rows=[]
for name,cmd,metadata in commands:
    with (out/(name+(".json" if name=="doc-impact" else ".log"))).open("w") as stream:
        start=time.time()
        result=subprocess.run(cmd,cwd=root,env=dict(env,GIT_DIR=gitdir,GIT_WORK_TREE=str(root)) if metadata else env,stdout=stream,stderr=subprocess.STDOUT)
    rows.append(dict(name=name,command=cmd,exit=result.returncode,status="passed" if result.returncode==0 else "failed"))
    (out/"checks.json").write_text(json.dumps(rows,indent=2)+"\n")
    print(name+": exit "+str(result.returncode),flush=True)
sys.exit(any(r["exit"] for r in rows))

