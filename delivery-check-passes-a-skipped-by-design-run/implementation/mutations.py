import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

root, evidence = map(Path, sys.argv[1:3])
source = (root / 'kc-dev-flow-2/scripts/delivery_gate.py').read_text()
mutations = [
    ('AC-1-reject-intended-skip', '("success", "skipped") if settle_skipped', '("success",) if settle_skipped',
     ['RequiredChecksTests.test_a_sole_completed_skipped_run_settles_when_required_names_have_a_pass']),
    ('AC-2-settle-failure', '("success", "skipped") if settle_skipped', '("success", "skipped", "failure") if settle_skipped',
     ['RequiredChecksTests.test_other_workflow_conclusions_hold_even_when_required_checks_pass']),
    ('AC-2-accept-every-bucket', 'if c.get("bucket") == "pass"', 'if True',
     ['RequiredChecksTests.test_each_required_name_needs_a_pass_despite_a_green_rollup']),
    ('AC-3-drop-required-hold', 'if required is not None and (why := required_problem(required)):', 'if False:',
     ['RequiredChecksTests.test_a_required_name_with_only_skipping_entries_holds_a_skipped_run']),
    ('AC-3-count-skipping-as-pass', 'if c.get("bucket") == "pass"', 'if c.get("bucket") in ("pass", "skipping")',
     ['RequiredChecksTests.test_a_required_name_with_only_skipping_entries_holds_a_skipped_run']),
    ('AC-4-settle-unconditionally', 'settle_skipped=bool(required)', 'settle_skipped=True',
     ['SettledChecksTests.test_a_skipped_workflow_run_still_holds_beside_a_green_rollup']),
    ('AC-5-suppress-read-error', 'if "no required checks reported" in done.stderr:', 'if True:',
     ['RequiredChecksTests.test_a_required_read_error_or_unparseable_stdout_holds_without_a_record']),
    ('AC-5-suppress-json-error', 'checks = json.loads(done.stdout)', 'checks = []',
     ['RequiredChecksTests.test_a_required_read_error_or_unparseable_stdout_holds_without_a_record']),
    ('AC-6-remove-call', 'required = required_checks(repo, number)', 'required = []',
     ['SettledChecksTests.test_required_check_read_adds_one_gh_call']),
    ('AC-6-add-call', 'required = required_checks(repo, number)', 'required = required_checks(repo, number)\n        required_checks(repo, number)',
     ['SettledChecksTests.test_required_check_read_adds_one_gh_call']),
]
results = []
for name, old, new, tests in mutations:
    assert source.count(old) == 1, (name, source.count(old))
    with tempfile.TemporaryDirectory(prefix='skipped-run-mutation-') as d:
        package = Path(d, 'kc-dev-flow-2')
        shutil.copytree(root / 'kc-dev-flow-2/scripts', package / 'scripts', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        (package / 'scripts/delivery_gate.py').write_text(source.replace(old, new))
        assert not list(package.rglob('__pycache__'))
        command = [sys.executable, '-B', '-m', 'unittest'] + ['test_delivery_gate.' + t for t in tests]
        done = subprocess.run(command, cwd=package / 'scripts', capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
        output = done.stdout + done.stderr
        (evidence / (name + '.log')).write_text(output)
        failure = re.search(r'FAILED \(failures=\d+\)', output)
        caught = done.returncode == 1 and bool(failure) and 'ERROR:' not in output
        results.append(dict(name=name, status='passed' if caught else 'failed', message='Mutant rejected by assertions; exit ' + str(done.returncode)))
        assert not list(package.rglob('__pycache__'))
        print(name, 'caught' if caught else 'NOT CAUGHT', flush=True)
(evidence / 'mutations.json').write_text(json.dumps(results, indent=2) + '\n')
raise SystemExit(0 if all(r['status'] == 'passed' for r in results) else 1)
