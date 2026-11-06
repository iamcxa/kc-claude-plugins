from pathlib import Path
import json
import subprocess
import sys
import tempfile

wt = Path('/tmp/merge-guard-validation-b82f20de/export')
source = wt / 'kc-dev-flow-2/scripts/merge_guard.py'
tests = source.with_name('test_merge_guard.py')
text = source.read_text()
previous = subprocess.check_output(['git', '-C', '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-merge-guard-stops-unasked-merges', 'show', 'ebac86a561655d990d2fcd7ff3cd8dbb20e8eb65:kc-dev-flow-2/scripts/merge_guard.py'], text=True)
cases = []

def changed(name, before, after, test, extra=None):
    assert text.count(before) == 1, name
    mutant = text.replace(before, after)
    if extra:
        a, b = extra
        assert a in mutant, name
        mutant = mutant.replace(a, b)
    cases.append((name, mutant, 'MergeGuardTests.test_' + test))

auto_raise = '            raise ValueError("FO never enables auto-merge; a saved head does not authorize a deferred merge")'
for label, test in [('bare-and-equals-auto', 'auto_flag_stops_with_matching_record'),
                    ('wrapped-auto', 'auto_flag_positions_and_wrappers_stop'),
                    ('both-hosts-auto', 'deferred_reason_reaches_both_hosts')]:
    changed(label, auto_raise, '            pass', test)
changed('equals-auto', 'if arg.split("=", 1)[0] == "--auto":', 'if arg == "--auto":',
        'auto_flag_stops_with_matching_record', ('switches = {"--admin",', 'switches = {"--auto", "--admin",'))
changed('rest-async-encoded', '    if re.search(r"(?:^|/)pulls/[^/]+/merge-async(?:/|$)", path):',
        '    if False:', 'rest_async_encoded_endpoint_stops')
for label, test in [('graphql-auto', 'graphql_auto_merge_stops_with_matching_record'),
                    ('graphql-enqueue', 'graphql_enqueue_stops_with_matching_record'),
                    ('graphql-opaque', 'graphql_deferred_opaque_and_encoded_forms_stop')]:
    changed(label, 'path == "graphql" or path.endswith("/graphql")', 'False', test,
            (r'|\bgraphql\b', ''))
changed('unknown-flags', '            raise ValueError("the merge flag cannot be parsed")',
        '            pass', 'unknown_merge_flags_stop')
changed('body-is-not-auto', '    number = head = None',
        '    if "--auto" in args:\n        raise ValueError("mutant broad auto scan")\n    number = head = None',
        'synchronous_flags_and_cancelling_auto_still_pass')
changed('no-live-query', '        pr, head = target',
        '        subprocess.run(["gh", "pr", "view"], check=True)\n        pr, head = target',
        'carried_merge_has_no_live_gh_lookup')
for test in ('auto_flag_stops_with_matching_record', 'auto_flag_positions_and_wrappers_stop',
             'rest_async_encoded_endpoint_stops', 'unknown_merge_flags_stop',
             'synchronous_flags_and_cancelling_auto_still_pass', 'deferred_reason_reaches_both_hosts'):
    cases.append(('previous-' + test, previous, 'MergeGuardTests.test_' + test))

out = Path('/tmp/merge-guard-validation-b82f20de/evidence/merge-guard-deferred-mutants')
out.mkdir(exist_ok=True)
results = []
for name, mutant, test in cases:
    with tempfile.TemporaryDirectory(prefix='merge-deferred-mutant-') as folder:
        root = Path(folder)
        (root / 'merge_guard.py').write_text(mutant)
        (root / 'test_merge_guard.py').write_text(tests.read_text())
        result = subprocess.run([sys.executable, '-B', str(root / 'test_merge_guard.py'), test], capture_output=True, text=True)
        (out / (name + '.log')).write_text(result.stdout + result.stderr)
        rejected = result.returncode != 0 and 'FAIL:' in result.stderr and 'ERROR:' not in result.stderr
        results.append({'name': name, 'status': 'passed' if rejected else 'failed', 'message': test + ' rejects mutant by assertion' if rejected else 'mutant survived or errored'})
Path('/tmp/merge-guard-validation-b82f20de/evidence/merge-guard-deferred-mutations.json').write_text(json.dumps(results, indent=2) + '\n')
print(len(results), 'falsifiers; rejected', sum(row['status'] == 'passed' for row in results))
assert all(row['status'] == 'passed' for row in results), results
