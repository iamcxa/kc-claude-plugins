"""Mutate isolated package copies; each selected behavioral check must fail."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

code, root, binary = map(Path, sys.argv[1:])
root.mkdir(parents=True, exist_ok=True)
cases = [
 ('record-home-rewrite', 'dispatch_stage.py',
  'return rewrite_home(text) if public else text',
  'return text',
  'test_dispatch_stage.DispatchStageTests.test_home_record_rewrite_keeps_the_real_path_in_the_worker_prompt'),
 ('role-prompt-redacted', 'dispatch_stage.py',
  "record_text(args, number, dispatched, checklist, notes, public=False).encode('utf-8')",
  'path.read_bytes()',
  'test_dispatch_stage.DispatchStageTests.test_home_role_record_rewrite_keeps_the_real_path_in_the_role_prompt'),
 ('record-root-binding', 'dispatch_records.py',
  'ROOT = re.compile(r"^Package root:[ \\t]*((?:/|~/)\\S+)", re.M)',
  'ROOT = re.compile(r"^Package root:[ \\t]*(/\\S+)", re.M)',
  'test_dispatch_records.ExtensionInstructionTests.test_home_relative_instruction_stays_bound_to_its_root'),
 ('evidence-home-rewrite', 'scratch.py', 'rewrite_home(text).encode(\'utf-8\')', 'text.encode(\'utf-8\')',
  'test_scratch.ScratchTests.test_new_text_rewritten_before_digest_and_gzip_but_old_and_binary_unchanged'),
 ('push-newest-only', 'state_guard.py', "git(root, 'rev-list', '--reverse', *revisions)",
  "git(root, 'rev-list', '--max-count=1', *revisions)",
  'test_state_guard.StateGuardTests.test_push_scans_every_commit_even_after_deletion'),
 ('gzip-uninspected', 'state_guard.py', "if data.startswith(b'\\x1f\\x8b'):\n        try:",
  "if data.startswith(b'\\x1f\\x8b'):\n        return b''\n        try:",
  'test_state_guard.StateGuardTests.test_gzip_and_binary_blobs_refuse_and_file_names_are_safe'),
 ('class-refusal-disabled', 'state_guard.py', 'modes[kind] = mode', "modes[kind] = 'warn'",
  'test_state_guard.StateGuardTests.test_warn_then_refuse_home_and_email_and_do_not_scan_product_worktree'),
 ('legacy-root-rejected', 'dispatch_records.py', '(?:/|~/)\\S', '~/\\S',
  'test_dispatch_stage.DispatchStageTests.test_stamp_commits_complete_record_and_exact_inputs'),
]
results=[]
for name, file, old, new, test in cases:
    candidate = root / name
    shutil.copytree(code/'kc-dev-flow-2', candidate, ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    source = candidate/'scripts'/file
    text=source.read_text()
    assert old in text, (name, 'mutation target absent')
    source.write_text(text.replace(old,new,1))
    for cache in candidate.rglob('__pycache__'):
        shutil.rmtree(cache)
    command=[sys.executable, '-B', '-m', 'unittest', test]
    done=subprocess.run(command, cwd=candidate/'scripts', capture_output=True, text=True,
                        env={**os.environ,'SPACEDOCK_BIN':str(binary),'PYTHONDONTWRITEBYTECODE':'1'},timeout=90)
    output=(done.stdout+done.stderr).replace(str(Path.home()), '~')
    (root/(name+'.log')).write_text(output)
    assert done.returncode==1 and 'FAIL' in output, (name,done.returncode,output[-1200:])
    results.append(dict(name=name,test=test,exit=done.returncode,status='passed',
                        evidence=name+'.log',claim='Mutation causes the behavioral test to fail.'))
(root/'falsifiers.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
