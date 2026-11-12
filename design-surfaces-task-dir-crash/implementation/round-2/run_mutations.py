#!/usr/bin/env python3
"""Mutate only the owned checker, exercise each named falsifier, then restore bytes."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--temp', type=Path, required=True)
    parser.add_argument('--base', required=True)
    parser.add_argument('--adopter-state', type=Path, action='append', required=True)
    args = parser.parse_args()
    args.temp.mkdir(exist_ok=False)
    target = args.source / 'kc-dev-flow-2/scripts/design_surfaces.py'
    original = target.read_bytes()
    text = original.decode()
    fallback = '    if not path.is_file() and path.name and (path.is_dir() or not path.suffix):\n        path = path.parent / (path.name + ".md")\n'
    guard = '    if not path.is_file():\n        parser.error(f"task file not found: {path}; pass a task file or its suffixless name")\n'
    ac1 = ['TaskArgumentTests.test_same_named_directory_checks_the_sibling_task_in_both_modes',
           'TaskArgumentTests.test_resolving_a_name_preserves_a_failing_verdict']
    ac2 = ['TaskArgumentTests.test_suffixless_name_without_a_directory_checks_the_task',
           'TaskArgumentTests.test_an_existing_file_wins_over_a_sibling_md_file']
    cases = [
        ('ac-1-no-fallback', fallback, '', ac1),
        ('ac-1-replace-dotted-suffix', 'path = path.parent / (path.name + ".md")', 'path = path.with_suffix(".md")', ac1),
        ('ac-1-force-success', 'return 1 if errors else 0', 'return 0', ac1),
        ('ac-2-require-directory', '(path.is_dir() or not path.suffix)', 'path.is_dir()', ac2),
        ('ac-2-override-exact-file', 'if not path.is_file() and path.name and (path.is_dir() or not path.suffix):', 'if path.name and (path.is_dir() or not path.suffix):', ac2),
        ('ac-3-no-usage-guard', guard, '', ['TaskArgumentTests.test_unresolved_names_and_directories_are_usage_errors']),
        ('ac-3-encoding-as-usage', '    notes = []\n    errors = check_task',
         '    try:\n        path.read_text()\n    except UnicodeError as exc:\n        parser.error(str(exc))\n    notes = []\n    errors = check_task',
         ['SeedBoundsTests.test_unreadable_seed_is_a_diagnostic_and_nonzero_without_traceback']),
        ('ac-4-no-fallback', fallback + guard, '', None),
        ('ac-4-change-valid-file-rule', 'def check_task(path, seed=False, notes=None):\n    errors = []',
         'def check_task(path, seed=False, notes=None):\n    errors = [f"{path.name}: mutation rejects all tasks"]', None),
    ]
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'TMPDIR': str(args.temp)}
    results = []
    try:
        for name, old, new, tests in cases:
            assert text.count(old) == 1, name + ': mutation target must be unique'
            mutant = text.replace(old, new, 1)
            ast.parse(mutant)
            caches = list((target.parent / '__pycache__').glob('design_surfaces.*.pyc'))
            for cache in caches:
                cache.unlink()
            target.write_text(mutant)
            output = args.output / name
            output.mkdir()
            if tests is not None:
                argv = [sys.executable, '-B', 'kc-dev-flow-2/scripts/test_design_surfaces.py', *tests]
            else:
                probe = args.output.parents[1] / 'evidence/run_probe.py'
                argv = [sys.executable, '-B', str(probe), '--source', str(args.source),
                        '--base', args.base, '--scratch', str(args.temp / name), '--output', str(output)]
                for root in args.adopter_state:
                    argv.extend(['--adopter-state', str(root)])
            log = output / 'run.txt'
            with log.open('w') as stream:
                done = subprocess.run(argv, cwd=args.source, env=env, stdout=stream,
                                      stderr=subprocess.STDOUT, timeout=180)
            target.write_bytes(original)
            if tests is not None:
                detected = done.returncode == 1 and 'FAILED (' in log.read_text()
            else:
                summary = json.loads((output / 'probe-summary.json').read_text())
                detected = done.returncode == 1 and summary['adopter_unavailable'] == 0 and (
                    summary['adopter_alias_matches'] < summary['adopter_mode_checks'] if name.endswith('no-fallback')
                    else summary['adopter_explicit_unchanged'] < summary['adopter_mode_checks'])
            safe_argv = [next((f'$ADOPTER_STATE_{i}' for i, root in enumerate(args.adopter_state, 1)
                               if value == str(root)), value) for value in argv]
            item = {'name': name, 'status': 'passed' if detected else 'failed',
                    'meaning': 'falsifier detected' if detected else 'falsifier not established',
                    'command': safe_argv, 'exit': done.returncode, 'syntax_valid': True,
                    'source_restored': target.read_bytes() == original,
                    'cleared_checker_cache_files': len(caches), 'output': str(log.relative_to(args.output))}
            results.append(item)
            print(json.dumps(item), flush=True)
            (args.output / 'mutation-results.json').write_text(json.dumps(results, indent=2) + '\n')
    finally:
        target.write_bytes(original)
    assert target.read_bytes() == original
    summary = {'mutants': len(results), 'detected': sum(x['status'] == 'passed' for x in results),
               'restored_sha256': hashlib.sha256(original).hexdigest(),
               'python_bytecode': '-B plus PYTHONDONTWRITEBYTECODE=1; checker pyc cleared before each mutation'}
    (args.output / 'mutation-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary), flush=True)
    return 0 if summary['mutants'] == 9 and summary['detected'] == 9 else 1


if __name__ == '__main__':
    sys.exit(main())
