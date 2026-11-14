"""Remove each repair in isolated package copies and require its behavioral test to fail."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

code, run = map(Path, sys.argv[1:])
run.mkdir(parents=True,exist_ok=True)
cases=[
 ('remove-no-hunk-fallback', "return b'\\n'.join(added) if in_hunk else data", "return b'\\n'.join(added)",
  'test_state_guard.StateGuardTests.test_no_hunk_changed_text_refuses_commit_and_push'),
 ('remove-path-matching', 'if expression.search(data) or expression.search(name)', 'if expression.search(data)',
  'test_state_guard.StateGuardTests.test_path_identifiers_refuse_new_and_renamed_files'),
 ('drop-same-oid-renames', "if after.strip(b'0') and metadata[1] != b'160000':", "if after.strip(b'0') and before != after and metadata[1] != b'160000':",
  'test_state_guard.StateGuardTests.test_path_identifiers_refuse_new_and_renamed_files'),
 ('rescan-unchanged-content', "    if before == after:\n        return b''\n", '',
  'test_state_guard.StateGuardTests.test_public_archive_renames_preserve_old_text_gzip_and_binary_content')]
results=[]
for name,old,new,test in cases:
    target=run/name
    shutil.copytree(code/'kc-dev-flow-2',target,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    path=target/'scripts/state_guard.py'
    text=path.read_text()
    assert text.count(old)==1,(name,'mutation target not unique')
    path.write_text(text.replace(old,new,1))
    for cache in target.rglob('__pycache__'):
        shutil.rmtree(cache)
    command=[sys.executable,'-B','-m','unittest',test]
    done=subprocess.run(command,cwd=target/'scripts',capture_output=True,text=True,
                        env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},timeout=90)
    output=(done.stdout+done.stderr).replace(str(Path.home()),'~')
    (run/(name+'.log')).write_text(output)
    assert done.returncode==1 and 'FAIL' in output,(name,done.returncode,output[-1500:])
    results.append(dict(name=name,status='passed',test=test,exit=done.returncode,
                        evidence=name+'.log',claim='Removing the named repair makes the real hook-boundary test fail.'))
(run/'results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
