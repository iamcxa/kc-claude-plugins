import ast, hashlib, json, os, subprocess, sys
from pathlib import Path
root=Path("/tmp/validate-pr818-merge-15Eaje/candidate")
out=Path("/tmp/validate-pr818-merge-15Eaje")
wt=Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-delivery-gate-ignores-url-paths-and-data-fences")
package=Path("/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.36.0")
state=Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state")
task=state/"delivery-gate-ignores-url-paths-and-data-fences"
base="8c8313823f353f631e2b7cca4559dd3e643f30a5"
head="b8362fb901cd27bd367be1cd5b826f21fefad70e"
gitdir=subprocess.check_output(["git","-C",str(wt),"rev-parse","--absolute-git-dir"],text=True).strip()
env=dict(os.environ,TMPDIR="/tmp",SPACEDOCK_BIN="/Users/kent/.local/bin/spacedock",PYTHONDONTWRITEBYTECODE="1")
commands=[
("mutations",[sys.executable,"-B",str(out/"run_mutations.py"),str(root),str(out)],False),
("delivery-gate",[sys.executable,"-B","kc-dev-flow-2/scripts/test_delivery_gate.py"],False),
("delivery-record-hold",[sys.executable,"-B","-m","unittest","discover","-s","kc-dev-flow-2/scripts","-p","test_delivery_gate.py","-k","DeliveryCheckBeforeQuestionTests","-v"],False),
("lint-skills",[sys.executable,"-B","kc-dev-flow-2/scripts/lint-skills.py"],False),
("adr-lint",[sys.executable,str(package/"scripts/adr_lint.py"),"docs/adr","--since",base],True),
("adr-lint-required",[sys.executable,str(package/"scripts/adr_lint.py"),"docs/adr","--since",base,"--require","0044","0051","0062","0071"],True),
("number-guards",[sys.executable,str(package/"scripts/number_guards.py"),"check","--repo",str(wt),"--workflow-dir",str(state.parent),"--task",str(task)+".md","--base",base,"--head",head],False),
("comment-ratio",[sys.executable,str(package/"scripts/comment_ratio.py"),base,head,"--repo",str(wt),"--workflow-dir",str(state.parent)],False),
("doc-impact",[sys.executable,str(package/"scripts/doc_impact.py"),base,head,"--repo",str(wt),"--json"],False),
("design-surfaces",[sys.executable,str(package/"scripts/design_surfaces.py"),"check",str(task)+".md"],False),
("dispatch-records",[sys.executable,str(package/"scripts/dispatch_records.py"),str(task)],False),
("diff-check",["git","-C",str(wt),"diff","--check",base,head],False),
]
rows=[]
for name,cmd,metadata in commands:
    path=out/(name+(".json" if name=="doc-impact" else ".log"))
    with path.open("w") as stream:
        result=subprocess.run(cmd,cwd=root,env=dict(env,GIT_DIR=gitdir,GIT_WORK_TREE=str(root)) if metadata else env,stdout=stream,stderr=subprocess.STDOUT)
    rows.append(dict(name=name,command=cmd,exit=result.returncode,status="passed" if result.returncode==0 else "failed",log=str(path)))
    (out/"checks.json").write_text(json.dumps(rows,indent=2)+"\n")
    print(name+": exit "+str(result.returncode),flush=True)
sys.exit(any(r["exit"] for r in rows))

