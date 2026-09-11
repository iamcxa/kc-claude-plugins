import json, subprocess, tempfile, hashlib, sys
from pathlib import Path
sd=Path(sys.argv[1]); out=Path(sys.argv[2]); root=Path(tempfile.mkdtemp(prefix="knowledge-close-shape-")); results=[]
def run(label,*args,input=None):
 p=subprocess.run(["rtk","proxy",*map(str,args)],cwd=root,text=True,capture_output=True,input=input)
 results.append(dict(label=label,argv=list(map(str,args)),rc=p.returncode,stdout=p.stdout,stderr=p.stderr));return p
(root/"README.md").write_text("""---
commissioned-by: spacedock@0.27.2
entity-type: task
entity-label: task
entity-label-plural: tasks
id-style: sd-b32
trunk: main
stages:
  states:
    - name: validation
      initial: true
      gate: true
    - name: done
      terminal: true
---
# Synthetic knowledge-only closure probe
""")
(root/"_mods").mkdir(); (root/"_mods/pr-merge.md").write_text("---\nname: pr-merge\ndescription: Synthetic merge hook\nversion: 1\n---\n## Hook: merge\nSynthetic only; no remote action.\n")
for a in [("init","-qb","main"),("config","user.name","Synthetic fixture"),("config","user.email","fixture@example.invalid"),("add","README.md","_mods/pr-merge.md"),("commit","-qm","synthetic fixture")]: run("git-setup","git",*a)
def native(label,*a,input=None): return run(label,sd,*a,"--workflow-dir",root,input=input)
body="""---
title: Synthetic accepted knowledge outcome
status: validation
pr: local-merge:accepted-knowledge-no-product-diff
---
# Synthetic evidence
Accepted answer is change, not rejected work. No live approval.
"""
native("new","new","probe",input=body); native("durable","state","commit","probe")
item=root/"probe.md"
native("prepare","gate","prepare","probe","--question","Synthetic approval?","--artifact",item,"--summary","SYNTHETIC ONLY accepted knowledge")
native("approve","gate","record","probe","--decision","approve","--actor","person:captain","--reason","SYNTHETIC ONLY, not Kent approval")
native("consume","gate","consume","probe")
before=item.read_bytes(); native("passed-knowledge","merge","guard","probe","--verdict","passed","--json"); after=item.read_bytes()
results.append(dict(label="readback",unchanged=before==after,active_exists=item.exists(),archive_exists=(root/"_archive/probe.md").exists(),body=after.decode()))
# Syntactic alternative is observed only in this disposable fixture; not a live recommendation.
native("rejected-syntax-only","merge","guard","probe","--verdict","rejected","--json")
native("resolve","status","--resolve","probe","--json")
out.write_text(json.dumps(dict(synthetic_only=True,root=str(root),binary=str(sd),binary_sha256=hashlib.sha256(sd.read_bytes()).hexdigest(),results=results),indent=2))
for r in results: print(r["label"],r.get("rc"),r.get("stdout",""),r.get("stderr",""))
assert any(r["label"]=="passed-knowledge" and '"blocked"' in r["stdout"] for r in results), "expected native refusal not observed"
assert before==after, "blocked guard mutated pending knowledge item"
