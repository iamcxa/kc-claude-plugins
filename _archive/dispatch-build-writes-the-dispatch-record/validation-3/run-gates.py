#!/usr/bin/env python3
import json, os, subprocess
from pathlib import Path
ROOT=Path("/tmp/pr812-validation3.KfmHwh/export")
OUT=Path("/tmp/pr812-validation3.KfmHwh/evidence")
WT="/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-dispatch-build-writes-the-dispatch-record"
PKG="/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0"
TASK="/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/dispatch-build-writes-the-dispatch-record.md"
WF="/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2"
BASE="334d91e3165953b2ca7191e3308d80b6c02c4a99"
HEAD="778367adde2e20e0b3e51966ddba2d9f77f9e614"
env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", GIT_DIR="/Users/kent/Project/kc-claude-workspace/kc-claude-plugins/.git/worktrees/spacedock-ensign-dispatch-build-writes-the-dispatch-record", GIT_WORK_TREE=str(ROOT))
commands=[
 ("candidate-adr",["python3","-B",str(ROOT/"kc-dev-flow-2/scripts/adr_lint.py"),"docs/adr","--since",BASE,"--require","0070"],0),
 ("installed-adr",["python3","-B","/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/adr_lint.py","docs/adr","--since",BASE,"--require","0070"],1),
 ("doc-impact",["python3","-B",PKG+"/scripts/doc_impact.py",BASE,HEAD,"--repo",WT,"--json"],0),
 ("number-guards",["python3","-B",PKG+"/scripts/number_guards.py","check","--repo",WT,"--base",BASE,"--head",HEAD,"--workflow-dir",WF,"--task",TASK],0),
 ("comment-ratio",["python3","-B",PKG+"/scripts/comment_ratio.py",BASE,HEAD,"--repo",WT,"--workflow-dir",WF],0),
 ("design-surfaces",["python3","-B",PKG+"/scripts/design_surfaces.py","check",TASK],0),
 ("dispatch-records",["python3","-B",PKG+"/scripts/dispatch_records.py",TASK[:-3]],0),
 ("diff-check",["git","-C",WT,"diff","--check",BASE,HEAD],0)
]
results=[]
for name,cmd,want in commands:
 result=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True)
 (OUT/(name+".log")).write_text(result.stdout+result.stderr)
 results.append(dict(name=name,status="passed" if result.returncode==want else "failed",exit=result.returncode,expected=want,command=cmd))
(OUT/"gate-results.json").write_text(json.dumps(results,indent=2)+"\n")
print(json.dumps(results,indent=2))

