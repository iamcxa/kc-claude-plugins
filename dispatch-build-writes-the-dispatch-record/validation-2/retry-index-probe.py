#!/usr/bin/env python3
"""Exercise a staged-only edit to a committed record during an immediate retry."""
import importlib.util
import json
from pathlib import Path
import sys

source = Path(sys.argv[1])
sys.path.insert(0, str(source / 'kc-dev-flow-2/scripts'))
spec = importlib.util.spec_from_file_location('seam', source / 'kc-dev-flow-2/scripts/test_dispatch_stage.py')
seam = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seam)
case = seam.DispatchStageTests('test_identical_retry_reuses_only_at_adding_commit')
case.setUp()
try:
    case.build()
    record = case.record()
    committed = record.read_bytes()
    staged = committed + b'\nPrepared staged-only dispatch annotation.\n'
    record.write_bytes(staged)
    case.git(case.state, 'add', '--', record)
    record.write_bytes(committed)
    before_index = case.git(case.state, 'ls-files', '--stage', '--', record)
    before_status = case.git(case.state, 'status', '--porcelain', '--', record)
    before_head = case.git(case.state, 'rev-parse', 'HEAD')
    result = case.build(expected=None)
    after_index = case.git(case.state, 'ls-files', '--stage', '--', record)
    after_status = case.git(case.state, 'status', '--porcelain', '--', record)
    print(json.dumps(dict(exit=result.returncode, stderr=result.stderr,
                         before_index=before_index, after_index=after_index,
                         before_status=before_status, after_status=after_status,
                         index_preserved=before_index == after_index,
                         worktree_preserved=record.read_bytes() == committed,
                         head_preserved=before_head == case.git(case.state, 'rev-parse', 'HEAD')),
                     indent=2))
finally:
    case.doCleanups()
