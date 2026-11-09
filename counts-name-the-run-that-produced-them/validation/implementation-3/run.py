"""Capture a check's command, process identity, exact revision, times and producer exit."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

worktree, output, name, *command = sys.argv[1:]
folder = Path(output)
candidate = subprocess.check_output(['git','-C',worktree,'rev-parse','HEAD'],text=True).strip()
start = datetime.datetime.now(datetime.timezone.utc).isoformat()
with (folder/(name+'.log')).open('w') as log:
    child = subprocess.Popen(command,cwd=worktree,stdout=log,stderr=subprocess.STDOUT)
    identity = dict(name=name,pid=child.pid,command=command,cwd=worktree,start=start,candidate=candidate)
    (folder/(name+'-process.json')).write_text(json.dumps(identity,indent=2)+'\n')
    print(json.dumps(dict(name=name,pid=child.pid)),flush=True)
    code = child.wait()
result = dict(**identity,end=datetime.datetime.now(datetime.timezone.utc).isoformat(),exit=code,
              end_candidate=subprocess.check_output(['git','-C',worktree,'rev-parse','HEAD'],text=True).strip(),
              log=name+'.log',log_sha256=hashlib.sha256((folder/(name+'.log')).read_bytes()).hexdigest())
(folder/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(name=name,exit=code,candidate=candidate)),flush=True)
sys.exit(code)
