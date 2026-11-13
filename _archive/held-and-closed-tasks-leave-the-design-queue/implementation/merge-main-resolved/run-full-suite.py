#!/usr/bin/env python3
"""Run the merged checkout's complete CI command list plus scratch tests."""
import argparse, hashlib, json, os, re, shlex, subprocess, xml.etree.ElementTree as ET
from pathlib import Path
import yaml
p=argparse.ArgumentParser()
for n in ("candidate","scratch","output"):p.add_argument("--"+n,type=Path,required=True)
a=p.parse_args(); ev=a.output; wt=a.candidate
env={**os.environ,"TMPDIR":str(a.scratch/"tmp"),"PYTHONDONTWRITEBYTECODE":"1","SPACEDOCK_BIN":"/Users/kent/.local/bin/spacedock","SD_PLUGIN_ROOT":str(a.scratch/"sd-plugin-root")}
steps=yaml.safe_load((wt/".github/workflows/kc-dev-flow-2-tests.yml").read_text())["jobs"]["unit-tests"]["steps"]
commands=[]
for step in steps:
 cmd=step.get("run","")
 if "python3 " not in cmd:continue
 cmd=cmd.replace('SPACEDOCK_BIN="$HOME/.local/bin/spacedock" ',"").replace('python3 ', 'python3 -B ',1).replace('-B -B','-B')
 cmd=cmd.replace('"$GITHUB_WORKSPACE/.sd-plugin-root"',shlex.quote(str(a.scratch/"sd-plugin-root")))
 commands.append((step["name"],shlex.split(cmd)))
if not any("test_scratch.py" in str(c) for _,c in commands):commands.append(("test_scratch.py (additional)",["python3","-B","kc-dev-flow-2/scripts/test_scratch.py"]))
records=[]
for name,cmd in commands:
 out=subprocess.run(cmd,cwd=wt,env=env,text=True,capture_output=True,timeout=900)
 log=re.sub(r"[^a-zA-Z0-9_.-]","_",name)+".log"; (ev/log).write_text(out.stdout+out.stderr)
 count=re.findall(r"Ran (\d+) tests?",out.stdout+out.stderr)
 records.append(dict(name=name,command=cmd,exit=out.returncode,log=log,unittest_count=sum(map(int,count))))
 (ev/"full-suite.json").write_text(json.dumps(records,indent=2)+"\n")
 print(name,"exit",out.returncode,"unittest count",sum(map(int,count)),flush=True)
suite=ET.Element("testsuite",name="Complete package CI commands plus scratch",tests=str(len(records)),failures=str(sum(r["exit"]!=0 for r in records)),errors="0",skipped="0")
for r in records:
 t=ET.SubElement(suite,"testcase",name=r["name"],classname="package-command")
 if r["exit"]: ET.SubElement(t,"failure",message="exit "+str(r["exit"])).text=(ev/r["log"]).read_text()[-16000:]
ET.ElementTree(suite).write(ev/"full-suite.xml",encoding="unicode")
(ev/"full-suite-summary.json").write_text(json.dumps(dict(commands=len(records),passed=sum(r["exit"]==0 for r in records),failed=sum(r["exit"]!=0 for r in records),unittest_tests=sum(r["unittest_count"] for r in records),native_integration_separate=True,sd_mod_revision="4d158a484ec73e184861067f8ed1e20087fdc26a",sd_mod_sha256=hashlib.sha256((a.scratch/"sd-plugin-root/mods/pr-merge.md").read_bytes()).hexdigest()),indent=2)+"\n")
raise SystemExit(any(r["exit"] for r in records))
