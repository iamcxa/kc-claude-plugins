#!/usr/bin/env python3
"""Exercise missing, duplicate and late warnings in isolated candidate copies."""
import argparse
import difflib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--code-root',type=Path,required=True)
p.add_argument('--output-dir',type=Path,required=True)
a=p.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True)
relative=Path('scripts/dispatch_stage.py')
source=(a.code_root/'kc-dev-flow-2'/relative).read_text()
block='    for line in dict.fromkeys(line for check in checks for line in check.stderr.splitlines(keepends=True)):\n        sys.stderr.write(line)\n'
assert source.count(block)==1
method='test_successful_same_symptom_forwards_one_reminder_before_real_build'
mutants=[
 ('drop-forward',source.replace(block,''),method,'successful check reminder was lost or duplicated'),
 ('duplicate-reminders',source.replace(block,'    for check in checks:\n        sys.stderr.write(check.stderr)\n'),method,'successful check reminder was lost or duplicated'),
 ('forward-after-build',source.replace(block,'').replace('    sys.stderr.write(build.stderr)\n',block+'    sys.stderr.write(build.stderr)\n'),method,'reminder was not visible before building'),
 ('deduplicate-whole-stream',source.replace(block,'    for stderr in dict.fromkeys(check.stderr for check in checks):\n        sys.stderr.write(stderr)\n'),'test_successful_checks_keep_distinct_other_stage_warnings','a distinct reminder was lost or shared reminder duplicated'),
]
rows=[]
for name,changed,test,assertion in mutants:
 with tempfile.TemporaryDirectory(prefix='dispatch-warning-mutant-') as tmp:
  root=Path(tmp)/'kc-dev-flow-2'
  shutil.copytree(a.code_root/'kc-dev-flow-2',root,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  (root/relative).write_text(changed)
  (a.output_dir/(name+'.patch')).write_text(''.join(difflib.unified_diff(source.splitlines(True),changed.splitlines(True),fromfile=str(relative),tofile=str(relative))))
  result=subprocess.run([sys.executable,'-B',str(root/'scripts/test_dispatch_stage.py'),'DispatchStageTests.'+test],env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True,timeout=90)
  output=result.stdout+result.stderr
  (a.output_dir/(name+'.log')).write_text(output)
  caught=bool(result.returncode and 'FAIL:' in output and assertion in output)
  rows.append(dict(name=name,status='passed' if caught else 'failed',mutant_exit=result.returncode,test=test,message='Mutant must fail: '+assertion))
  (a.output_dir/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
  print(json.dumps(rows[-1]),flush=True)
sys.exit(any(row['status']!='passed' for row in rows))
