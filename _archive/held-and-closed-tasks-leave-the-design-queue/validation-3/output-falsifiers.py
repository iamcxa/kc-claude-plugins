#!/usr/bin/env python3
"""Exercise fresh-process output and word-bound falsifiers."""
import argparse,json,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser()
for n in ("output","scratch","task"):p.add_argument("--"+n,type=Path,required=True)
a=p.parse_args();ev=a.output;records=[]
def run(name,cmd,want):
 r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True)
 (ev/(name+".log")).write_text(r.stdout+r.stderr)
 records.append(dict(name=name,command=list(map(str,cmd)),exit=r.returncode,expected=want,passed=r.returncode==want))
checker=ev/"check-output.py";ten=a.task/"ideation/held-ten.txt";rows=ev/"held-live.json"
run("AC-3-output",[sys.executable,"-B",checker,"legacy",ev/"legacy-tasks-network.log",ten],0)
bad=a.scratch/"legacy-with-held.txt";bad.write_text((ev/"legacy-tasks-network.log").read_text()+"\n"+ten.read_text().split()[0]+"\n")
run("AC-3-mutated-output",[sys.executable,"-B",checker,"legacy",bad,ten],1)
run("NP-1-current-output",[sys.executable,"-B",checker,"candidate",ev/"candidate-live-network.log",rows],0)
source=(ev/"candidate-live-network.log").read_text();first=json.loads(rows.read_text())["entities"][0]["slug"]
for kind,text in (("missing",source.replace(first,"removed-held-name")),("duplicate",source.replace(first,first+", "+first,1))):
 bad=a.scratch/(kind+"-candidate.txt");bad.write_text(text)
 run("NP-1-"+kind,[sys.executable,"-B",checker,"candidate",bad,rows],1)
measurements=[]
for case in ("one","current","larger"):
 d=json.loads((ev/"words"/(case+".json")).read_text());measurements.append(d)
 checker=a.task/"implementation/amendment-4/check-bound.py";fact=ev/"words"/(case+"-fact.txt")
 run(case+"-word-bound",[sys.executable,"-B",checker,fact,d["held_tasks"]],0)
 bad=a.scratch/(case+"-over-bound.txt");bad.write_text(fact.read_text().strip()+" x"*(d["maximum_words"]+1-d["measured_words"])+"\n")
 run(case+"-over-bound",[sys.executable,"-B",checker,bad,d["held_tasks"]],1)
(ev/"words/measurements.json").write_text(json.dumps(measurements,indent=2)+"\n")
(ev/"output-falsifiers.json").write_text(json.dumps(records,indent=2)+"\n")
print(json.dumps(records,indent=2))
raise SystemExit(not all(r["passed"] for r in records))
