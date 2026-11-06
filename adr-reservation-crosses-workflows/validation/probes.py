import importlib.util
import io
import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

WT = Path('/tmp/adr-reservation-validation-801/candidate')
OUT = Path('/tmp/adr-reservation-validation-801')
script = WT / 'kc-dev-flow-2/scripts/number_guards.py'
spec = importlib.util.spec_from_file_location('guard_tests', script.with_name('test_number_guards.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
source = script.read_text()
fetch = '''["git", "-C", args.repo, "fetch", "--quiet", "origin",
         "+refs/heads/spacedock-state/*:refs/remotes/origin/spacedock-state/*"]'''
own = '''if own_origin and ref == f"origin/{cfg['state_branch']}" and path == own_path:'''
mutants = [
 ('AC1-no-explicit-fetch', fetch, '["git", "--version"]', ['CrossWorkflowTests.test_single_branch_clone_fetches_foreign_holder_at_reserve']),
 ('AC1-no-origin-scan', '"refs/remotes/origin/spacedock-state/").splitlines():', '"refs/remotes/unused/").splitlines():', ['CrossWorkflowTests.test_single_branch_clone_fetches_foreign_holder_at_reserve']),
 ('AC2-no-r8', 'elif number in holders:', 'elif False and number in holders:', ['CrossWorkflowTests.test_merge_ask_refuses_held_number_and_accepts_free_number']),
 ('AC3-flat-only', '[*state.glob("*.md"), *state.glob("*/index.md")]', '[*state.glob("*.md")]', ['CrossWorkflowTests.test_own_folder_holder_counts_at_reserve_and_check']),
 ('AC4-skip-whole-own-branch', own, '''if own_origin and ref == f"origin/{cfg['state_branch']}":''', ['CrossWorkflowTests.test_own_task_pushed_copy_is_excluded_but_sibling_on_own_branch_counts']),
 ('AC4-no-origin-probe', own, '''if ref == f"origin/{cfg['state_branch']}" and path == own_path:''', ['CrossWorkflowTests.test_no_origin_same_basename_and_slug_is_foreign']),
 ('AC4-no-own-path-exclusion', own, 'if False:', ['CrossWorkflowTests.test_own_task_pushed_copy_is_excluded_but_sibling_on_own_branch_counts']),
 ('AC5-double-report', 'elif number in holders:', 'if number in holders:', ['CrossWorkflowTests.test_number_already_on_base_gets_r5_without_r8']),
 ('AC6-no-origin-warning', 'warning: state checkout has no origin; no other workflow sees these reservations;', 'warning: state visibility unknown;', ['CrossWorkflowTests.test_blind_read_warnings_go_to_stderr_and_cached_holders_still_count']),
 ('AC6-no-fetch-warning', 'warning: state fetch failed; reading local origin/spacedock-state/* refs only;', 'warning: cached refs;', ['CrossWorkflowTests.test_blind_read_warnings_go_to_stderr_and_cached_holders_still_count']),
 ('AC8-help-omits-r8', source.split(chr(34) * 3)[1], source.split(chr(34) * 3)[1].replace('R8', 'rule eight'), ['HelpTests.test_help_names_every_rule_from_r1_to_r8_and_holder_sources']),
]
results = []
with (OUT / 'mutations.log').open('w') as log, tempfile.TemporaryDirectory(prefix='adr-mutants-') as tmp:
    cache = Path(tmp) / '__pycache__'
    assert not cache.exists()
    for name, old, new, tests in mutants:
        assert source.count(old) == 1, (name, source.count(old))
        candidate = Path(tmp) / (name + '.py')
        candidate.write_text(source.replace(old, new))
        mod.SCRIPT = str(candidate)
        suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(test, mod) for test in tests)
        output = io.StringIO()
        result = unittest.TextTestRunner(stream=output).run(suite)
        caught = len(result.failures) > 0 and not result.errors
        log.write(name + '\n' + output.getvalue() + '\n')
        log.flush()
        results.append({'name': name, 'status': 'passed' if caught else 'failed', 'message': f'{len(result.failures)} assertion failures, {len(result.errors)} runtime errors; caches absent, python3 -B'})
        print(name, 'caught' if caught else 'NOT CAUGHT', flush=True)
    baseline = Path(tmp) / 'baseline.py'
    baseline.write_text(Path('/tmp/adr-reservation-validation-801/base/kc-dev-flow-2/scripts/number_guards.py').read_text())
    mod.SCRIPT = str(baseline)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(mod.CrossWorkflowTests)
    output = io.StringIO()
    result = unittest.TextTestRunner(stream=output).run(suite)
    log.write('BASELINE\n' + output.getvalue())
    results.append({'name': 'Goal without candidate change', 'status': 'passed' if len(result.failures) >= 6 and not result.errors else 'failed', 'message': f'base: {result.testsRun} tests, {len(result.failures)} assertion failures, {len(result.errors)} runtime errors'})
(OUT / 'mutations.json').write_text(json.dumps(results, indent=2))
assert all(r['status'] == 'passed' for r in results), results

words = lambda t: re.findall(r'[a-z0-9<>/_.\-]+', t.lower().replace('`', ''))
rel = 'kc-dev-flow-2/references/sd/workflow.md'
base = (OUT / 'base' / rel).read_text()
new = (WT / rel).read_text()
expected = base.replace('lists the flags and rules R1 to R6;', 'lists the flags and rules;').replace('(`check` reports R3 or R5 on\n  the later candidate; nothing compares task files)', '(`check` reports R3, R5 or R8 on\n  the later candidate)')
assert new == expected
section = lambda t, title: re.search(r'^## ' + re.escape(title) + r'\n(.*?)(?=^## |\Z)', t, re.M | re.S).group(1)
bullet = lambda t, name: re.search(r'^- \*\*' + name + r'\.\*\*(.*?)(?=^- \*\*|^## |\Z)', t, re.M | re.S).group(0)
counts = [
 {'name': 'FO startup', 'before': len(words(base)), 'after': len(words(new)), 'better': 'lower'},
 {'name': 'Worker Number guards', 'before': len(words(section(base, 'Number guards'))), 'after': len(words(section(new, 'Number guards'))), 'better': 'lower'},
 {'name': 'Reserve bullet', 'before': len(words(bullet(base, 'Reserve'))), 'after': len(words(bullet(new, 'Reserve'))), 'better': 'lower'},
 {'name': 'Check bullet', 'before': len(words(bullet(base, 'Check'))), 'after': len(words(bullet(new, 'Check'))), 'better': 'lower'},
 {'name': 'Collision bullet', 'before': len(words(bullet(base, 'Collision'))), 'after': len(words(bullet(new, 'Collision'))), 'better': 'lower'},
]
assert counts[0]['after'] - counts[0]['before'] == -6
assert all(r['after'] <= r['before'] for r in counts)
(OUT / 'words.json').write_text(json.dumps(counts, indent=2))
print('word recount', counts, flush=True)
