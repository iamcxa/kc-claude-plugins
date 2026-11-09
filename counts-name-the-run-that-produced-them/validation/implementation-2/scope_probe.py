"""Reproduce the out-of-scope POC fixture contract at the base and candidate."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

worktree, output = map(Path, sys.argv[1:])
base = '82c9e67ae892b80647c3f6a8b6929f993e42dbc2'
test = 'test_poc_readme.DeriveTests.test_delivery_recipe_holds_nonzero_and_forwards_checked_summary_in_both_routes'
results=[]
for label in ('base','candidate'):
    with tempfile.TemporaryDirectory(prefix='counts-poc-scope-',dir=worktree/'.context') as temp:
        package=Path(temp)/'kc-dev-flow-2'
        shutil.copytree(worktree/'kc-dev-flow-2',package,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        if label=='base':
            (package/'scripts/delivery_gate.py').write_text(subprocess.check_output(['git','-C',str(worktree),'show',base+':kc-dev-flow-2/scripts/delivery_gate.py'],text=True))
        command=[sys.executable,'-B','-m','unittest',test]
        done=subprocess.run(command,cwd=package/'scripts',capture_output=True,text=True)
        (output/('scope-'+label+'.log')).write_text(done.stdout+done.stderr)
        assert done.returncode == (0 if label=='base' else 1),done.stderr
        results.append(dict(label=label,command=command,exit=done.returncode,log='scope-'+label+'.log'))
print(json.dumps(dict(base=base,candidate=subprocess.check_output(['git','-C',str(worktree),'rev-parse','HEAD'],text=True).strip(),results=results),indent=2))
