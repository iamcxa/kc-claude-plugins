import importlib.util, json, os, subprocess, sys
from pathlib import Path
root=Path(sys.argv[1]);ev=Path(sys.argv[2]);c=root/".validation-775"
spec=importlib.util.spec_from_file_location("due_tests",c/"kc-dev-flow-2/extensions/release-acceptance/test_release_acceptance.py");m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
t=m.DueTests();t.setUp()
try:
 node,progress,env=t.live_producer()
 commands=[
  [node,str(progress),str(t.map),"--workflow-dir",str(t.wf)],
  [sys.executable,"-B",str(c/"kc-dev-flow-2/extensions/release-acceptance/release_acceptance.py"),"due","--workflow-dir",str(t.wf),"--progress",str(progress),str(t.map)]]
 for p in t.state.glob("*.md"):p.write_text(p.read_text().replace("status: done\n","status: done # completed\n"))
 results=[]
 for argv in commands:
  r=subprocess.run(argv,env=env,capture_output=True,text=True);results.append({"command":argv,"exit":r.returncode,"stdout":r.stdout,"stderr":r.stderr})
 document=json.loads(results[0]["stdout"]);assert document["diagnostic"] is None
 assert sum(row["acceptance"]=="pending delivery acceptance" for row in document["releases"])==2
 assert results[1]["exit"]==0 and results[1]["stdout"]==""
 (ev/"yaml-status.json").write_text(json.dumps(results,indent=2))
 print("REPRODUCED: real producer reports 2 pending releases; due emits no reminder for status: done # completed")
finally:t.doCleanups()

