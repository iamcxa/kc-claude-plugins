"""Capture a named check's command, exact candidate, time, output and producer exit."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

worktree, output, name, *command = sys.argv[1:]
folder = Path(output)
start = datetime.datetime.now(datetime.timezone.utc).isoformat()
candidate = subprocess.check_output(['git','-C',worktree,'rev-parse','HEAD'],text=True).strip()
with (folder / (name + '.log')).open('w') as log:
    done = subprocess.run(command, cwd=worktree, stdout=log, stderr=subprocess.STDOUT)
result = dict(name=name, command=command, cwd=worktree, start=start,
              end=datetime.datetime.now(datetime.timezone.utc).isoformat(), exit=done.returncode,
              candidate=candidate,
              end_candidate=subprocess.check_output(['git','-C',worktree,'rev-parse','HEAD'],text=True).strip(),
              log=name+'.log', log_sha256=hashlib.sha256((folder/(name+'.log')).read_bytes()).hexdigest())
(folder/(name+'.json')).write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result))
sys.exit(done.returncode)
