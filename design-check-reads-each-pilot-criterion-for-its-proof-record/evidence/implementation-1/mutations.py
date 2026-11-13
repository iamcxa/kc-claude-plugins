import json,os,shutil,subprocess,sys
from pathlib import Path
wt,scratch=map(Path,sys.argv[1:])
source=(wt/"kc-dev-flow-2/scripts/design_surfaces.py").read_text()
mutants=[
("no-exit", '("exit", PROOF_EXIT), ', ""),
("no-command", '("command", PROOF_COMMAND), ', ""),
("no-path", ', ("output path", PROOF_PATH)', ""),
("falsifier-counts", 'claim = FALSIFIER_PART.sub(" ", block)', 'claim = block'),
("bare-id-reason", 'len(words_of(AC_ID.sub("", line))) >= 3', 'True'),
("no-heading-boundary", 'if inside and head and len(head.group(1)) <= level:', 'if False:'),
("inline-unprovable", 'unprovable = unprovable_entries(lines)',
 'unprovable = AC_ID.findall(" ".join(lines)) if any("Not provable now" in line for line in lines) else {}'),
("all-stages", '(profile.group(1), status.group(1)) == ("pilot", "ideation")', 'profile.group(1) == "pilot"'),
("all-profiles", '(profile.group(1), status.group(1)) == ("pilot", "ideation")', 'status.group(1) == "ideation"'),
("no-approval-exemption", 'and not design_approved(text):', ':'),
("no-check-task-call", 'for key, missing in proof_gaps(lines):', 'for key, missing in []:'),
]
results=[]
for name,old,new in mutants:
    assert source.count(old)==1,(name,source.count(old))
    target=scratch/"mutants"/name/"kc-dev-flow-2/scripts"
    shutil.copytree(wt/"kc-dev-flow-2/scripts",target,ignore=shutil.ignore_patterns("__pycache__"),dirs_exist_ok=True)
    (target/"design_surfaces.py").write_text(source.replace(old,new,1))
    cmd=[sys.executable,"-B","-m","unittest","discover","-s",str(target),"-p","test_design_surfaces.py","-k","PilotProofTests"]
    env={**os.environ,"TMPDIR":str(scratch/"tmp"),"PYTHONDONTWRITEBYTECODE":"1"}
    done=subprocess.run(cmd,capture_output=True,text=True,env=env)
    log=scratch/"checks"/("mutant-"+name+".log")
    log.write_text(done.stdout+done.stderr)
    killed=done.returncode==1 and "FAIL:" in done.stderr and "ERROR:" not in done.stderr
    results.append(dict(name=name,exit=done.returncode,killed=killed,output="mutant-"+name+".log"))
    print(name,done.returncode,killed,flush=True)
(scratch/"mutations.json").write_text(json.dumps(results,indent=2))
sys.exit(0 if all(r["killed"] for r in results) else 1)
