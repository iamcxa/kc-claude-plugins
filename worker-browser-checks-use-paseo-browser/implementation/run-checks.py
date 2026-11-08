import concurrent.futures
import json
from pathlib import Path
import subprocess
import sys
repo, package, workflow, task, base, head, evidence = sys.argv[1:]
out = Path(evidence)
commands = {
    "lint-skills": [sys.executable,"-B",repo+"/kc-dev-flow-2/scripts/lint-skills.py"],
    "adr-lint": [sys.executable,"-B",package+"/scripts/adr_lint.py","docs/adr","--since",base],
    "number-guards": [sys.executable,"-B",package+"/scripts/number_guards.py","check","--workflow-dir",workflow,"--task",task,"--repo",repo,"--base",base,"--head",head],
    "comment-ratio": [sys.executable,"-B",package+"/scripts/comment_ratio.py",base,head,"--workflow-dir",workflow],
    "design-surfaces": [sys.executable,"-B",package+"/scripts/design_surfaces.py","check",task],
    "doc-impact": [sys.executable,"-B",package+"/scripts/doc_impact.py",base,head,"--json"],
}
def run(item):
    name, command = item
    r = subprocess.run(command,cwd=repo,capture_output=True,text=True)
    (out/(name+(".json" if name=="doc-impact" else ".log"))).write_text(r.stdout+r.stderr)
    return {"name":name,"status":"passed" if r.returncode==0 else "failed","exit":r.returncode,"command":command}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    results = list(pool.map(run,commands.items()))
(out/"checks-results.json").write_text(json.dumps(results,indent=2)+"\n")
print(json.dumps(results,indent=2))
sys.exit(1 if any(x["exit"] for x in results) else 0)

