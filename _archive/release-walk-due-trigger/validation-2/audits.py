import fnmatch, importlib.util, json, os, re, subprocess, sys
from pathlib import Path
root=Path(sys.argv[1]);ev=Path(sys.argv[2]);c=root/".validation-2-consumer";package=c/"kc-dev-flow-2"
rules=json.loads(subprocess.check_output(["node","--input-type=module","-e", "import fs from 'node:fs'; import {parse} from 'yaml'; console.log(JSON.stringify(parse(fs.readFileSync('/Users/kent/.claude/kc-plugins-config/sanitize-rules.yaml','utf8'))))"], cwd=root/".validation-2-producer/kc-journey-map",text=True))
files=set()
for pattern in ["reference/*.md","skills/**/*.md","agents/*.md","hooks/**/*.md","docs/*.md","README.md","CLAUDE.md","skill-scenarios/*.yaml"]:files.update(package.glob(pattern))
patterns={"ticket_shape":r"[A-Z]{2,5}-\d{2,6}","pr":r"[a-z][-a-z0-9]+/[a-z][-a-z0-9]+#\d+","sha":r"\x60[0-9a-f]{7,40}\x60","local_path":r"/Users/[^/]+/(Project|Code|Work)/","real_email":r"[A-Za-z0-9._%+-]+@(?!example\.com|test\.com|seed\.[a-z]+)[A-Za-z0-9.-]+\.[A-Za-z]{2,}","branch":r"(feature|fix|chore)/[a-z]{2,5}-\d+"}
reject=list(set(rules.get("reject_patterns",[])+[r"AKIA[0-9A-Z]{16}",r"ghp_[A-Za-z0-9]{36}",r"sk-[A-Za-z0-9]{32,}",r"-----BEGIN [A-Z ]+PRIVATE KEY-----",r"ssh-rsa AAAA[0-9A-Za-z+/=]{100,}"]))
findings=[];scanned=0
for file in sorted(files):
 rel=str(file.relative_to(c))
 if any(fnmatch.fnmatch(rel,x) for x in rules.get("exclude_paths",[])):continue
 if subprocess.run(["git","-C",str(c),"check-ignore","-q",str(file)]).returncode==0:continue
 scanned+=1
 for n,line in enumerate(file.read_text().splitlines(),1):
  for cls,kind,pattern,literal in [("BLOCK","literal",x,True) for x in rules["block_literals"]]+[("REJECT","secret shape",x,False) for x in reject]+[("WARN",k,v,False) for k,v in patterns.items() if k not in rules.get("disable_warn",[])]:
   hits=[pattern] if literal and pattern in line else [] if literal else [x.group(0) for x in re.finditer(pattern,line)]
   for hit in hits:
    if any(x in hit or x in line and hit in x for x in rules.get("allowlist",[])):continue
    findings.append({"severity":"low" if cls=="WARN" else "high","title":cls+" "+kind,"file":rel,"line":n})
(ev/"sanitize-findings.json").write_text(json.dumps(findings,indent=2))
counts={k:sum(f["title"].startswith(k) for f in findings) for k in ["REJECT","BLOCK","WARN"]}
(ev/"sanitize.log").write_text(json.dumps({"files":scanned,**counts,"exit":2 if counts["REJECT"] else 1 if counts["BLOCK"] else 0})+"\n")
assert not counts["REJECT"] and not counts["BLOCK"]
# Reuse the shipped workflow fixture for an actual old/new output comparison.
sys.path.insert(0,str(c/"kc-dev-flow-2/scripts"))
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
test=load("watch_test",c/"kc-dev-flow-2/scripts/test_pr_watch.py")
basefile=root/".validation-2-support/pr_watch_base.py"
basefile.write_bytes(subprocess.check_output(["git","-C",str(c),"show","origin/main:kc-dev-flow-2/scripts/pr_watch.py"]))
base=load("base_watch",basefile);base.SCRIPTS=test.watch.SCRIPTS
case=test.TasksTests();case.setUp()
try:
 case.readme("")
 (case.state/"built.md").write_text("---\ntitle: built\nstatus: done\njourney: demo\njourney-release: r1\n---\n")
 case.git(case.state,"add","built.md");case.git(case.state,"commit","-qm","built")
 mapfile=case.repo/"docs/journey/journey.yaml";mapfile.parent.mkdir(parents=True);mapfile.write_text("journey: demo\n")
 current=case.tasks({});original=test.watch;test.watch=base
 try:previous=case.tasks({})
 finally:test.watch=original
 assert previous==current
 (ev/"unlisted-base-comparison.json").write_text(json.dumps({"base":"e1bee223c47a1cd534a665a47776b683375b34fc","candidate":"a3d9b00211929469c3b8cd8ccf63f95d2e261274","base_result":previous,"candidate_result":current,"equal":True},indent=2))
finally:case.doCleanups()
print("PASS: sanitize has no block/reject; unlisted candidate and origin/main output match.")

