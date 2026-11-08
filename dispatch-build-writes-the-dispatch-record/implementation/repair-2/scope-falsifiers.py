#!/usr/bin/env python3
"""Mutate isolated package copies and require the preservation oracle to fail."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--code-root', type=Path, required=True)
parser.add_argument('--output-dir', type=Path, required=True)
a = parser.parse_args()
a.output_dir.mkdir(parents=True, exist_ok=True)
source = a.code_root / 'kc-dev-flow-2'
original = (source / 'scripts/dispatch_stage.py').read_text()
guard = '        check_task_scope(state, scope)\n'
selected = '[(folder / "dispatch" / f"{args.stage}-1.md").relative_to(state).as_posix()]'
mutants = [
 ('guard-removed', guard, '', None, 'test_retry_preserves_staged_record_with_worktree_at_head'),
 ('index-comparison-omitted', 'if head.get(name) != index.get(name):', 'if False:', 'flat:fresh:report:equal-change', None),
 ('worktree-comparison-omitted', 'if (actual_mode, actual_oid) != (mode, oid):', 'if False:', 'folder:fresh:report:worktree-only', None),
 ('untracked-check-omitted', 'for name in read("ls-files", "--others", "--exclude-standard", "-z", "--", *scope).split(b"\\0"):', 'for name in ():', 'flat:fresh:new-report:untracked', None),
 ('scope-only-selected-record', guard, '        check_task_scope(state, ' + selected + ')\n', 'flat:fresh:task:staged-only', None),
 ('scope-only-dispatch-directory', guard, '        check_task_scope(state, [(folder / "dispatch").relative_to(state).as_posix()])\n', 'folder:fresh:report:partial', None),
 ('guard-after-record-creation', guard + '        path, wrote = select_record(args, folder, dispatched, checklist, notes)\n', '        path, wrote = select_record(args, folder, dispatched, checklist, notes)\n' + guard, 'flat:fresh:report:staged-only', None),
 ('retry-bypasses-guard', guard, '        if not any((folder / "dispatch").glob(f"{args.stage}-*.md")):\n    ' + guard, 'flat:retry:reused:staged-only', None),
 ('advance-bypasses-guard', guard, '        if not args.advance:\n    ' + guard, 'folder:advance:reused:staged-only', None),
]
results = []
for name, old, new, case, method in mutants:
    assert original.count(old) == 1, (name, original.count(old))
    with tempfile.TemporaryDirectory(prefix='dispatch-scope-mutant-') as tmp:
        root = Path(tmp) / 'kc-dev-flow-2'
        shutil.copytree(source, root, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        (root / 'scripts/dispatch_stage.py').write_text(original.replace(old, new))
        log_path = a.output_dir / (name + '.snapshots.jsonl')
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', DISPATCH_SCOPE_LOG=str(log_path))
        env.pop('DISPATCH_SCOPE_CASE', None)
        if case:
            env['DISPATCH_SCOPE_CASE'] = case
        command = [sys.executable, '-B', str(root / 'scripts/test_dispatch_stage.py'),
                   'DispatchStageTests.' + (method or 'test_scope_preservation_matrix')]
        result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=90)
        output = result.stdout + result.stderr
        (a.output_dir / (name + '.log')).write_text(output)
        snapshots = [json.loads(line) for line in log_path.read_text().splitlines()] if log_path.exists() else []
        caught = bool(result.returncode and 'FAIL:' in output and 'refusal changed scoped or outside state' in output
                      and snapshots and any(row['before'] != row['after'] for row in snapshots))
        results.append(dict(name=name, status='passed' if caught else 'failed', mutant_exit=result.returncode,
                            scenario=case or 'reported-retry', oracle='snapshot preservation',
                            message='Mutant must fail its matching preservation assertion'))
        (a.output_dir / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
        print(json.dumps(results[-1]), flush=True)
sys.exit(any(row['status'] != 'passed' for row in results))
