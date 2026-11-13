#!/usr/bin/env python3
"""Disposable command-level probe. Arguments: package, fixture-root, evidence-dir, case."""
import hashlib, json, os, shutil, subprocess, sys
from pathlib import Path
package, root, evidence = map(Path, sys.argv[1:4]); case=sys.argv[4]
root.mkdir(parents=True, exist_ok=True); evidence.mkdir(parents=True, exist_ok=True)
workflow=root/'workflow'; workflow.mkdir(exist_ok=True)
state=workflow/'tasks'; state.mkdir(exist_ok=True)
(workflow/'README.md').write_text("""---
entity-type: task
id-style: slug
state: tasks
extensions: []
stages:
  defaults:
    worktree: false
  states:
    - name: implementation
      initial: true
    - name: done
      terminal: true
---
# Disposable probe
""")
body='---\ntitle: Synthetic absent worktree\nstatus: implementation\nvariant: kc-dev-flow-2\nprofile: pilot\n'
if case=='absent': body+='worktree: .worktrees/does-not-exist\n'
(state/'synthetic.md').write_text(body+'---\n\n## Scope\nBounded synthetic read.\n')
bin_dir=root/'bin';bin_dir.mkdir(exist_ok=True)
gh=bin_dir/'gh'; gh.write_text('#!/bin/sh\necho "Unexpected provider call" >&2\nexit 97\n');gh.chmod(0o755)
env=dict(os.environ, PATH=str(bin_dir)+os.pathsep+os.environ['PATH'],SPACEDOCK_BIN='/Users/kent/.local/bin/spacedock',PYTHONDONTWRITEBYTECODE='1')
command=[sys.executable,'-B',str(package/'scripts/pr_watch.py'),'--state',str(root/'watch.json'),'tasks',str(workflow)]
before=(state/'synthetic.md').read_bytes()
r=subprocess.run(command,cwd=root,capture_output=True,text=True,env=env)
(evidence/(case+'.stdout.txt')).write_text(r.stdout)
(evidence/(case+'.stderr.txt')).write_text(r.stderr)
expected='fact: synthetic has no recorded PR; its worktree is not on this machine.\n' if case=='absent' else ''
checks={'exit_zero':r.returncode==0,'exact_output':r.stdout==expected,'no_next':not any(x.startswith('next:') for x in r.stdout.splitlines()),'no_watch_created':not (root/'watch.json').exists(),'task_unchanged':before==(state/'synthetic.md').read_bytes()}
record={'command':command,'cwd':str(root),'exit':r.returncode,'output':str(evidence/(case+'.stdout.txt')),'checks':checks,'package_sha256':hashlib.sha256((package/'scripts/pr_watch.py').read_bytes()).hexdigest()}
(evidence/(case+'.json')).write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
sys.exit(0 if all(checks.values()) else 1)
