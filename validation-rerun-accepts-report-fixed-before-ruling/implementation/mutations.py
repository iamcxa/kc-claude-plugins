import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

source = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
original = (source / 'kc-dev-flow-2/scripts/dispatch_records.py').read_text()
env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
mutations = [
    ('AC-1-any-rewrite', [('        if len(reports) > ordinal:\n',
                           '        if len(reports) > ordinal:\n            if reports[ordinal] != selected[-1]:\n                raise RulingHistoryError("rewritten-report")\n')],
     ['test_correction_before_later_ruling_clears']),
    ('AC-2-identities', [('        if settled_ids - known:', '        if False:'),
                         ('            if identities - known or ancestor(settled[0], commit):',
                          '            if ancestor(settled[0], commit):')],
     ['test_rewrite_after_native_ruling_or_nonclearing_gate_is_refused']),
    ('AC-2-same-commit', [('        if settled_ids - known:', '        if False:')],
     ['test_correction_committed_beside_amendment_is_refused']),
    ('AC-3-verdict-list', [('        if any(re.findall(r"\\b(PASSED|REJECTED)\\b", report) != words for _, report, _ in versions):',
                           '        if False:')],
     ['test_pre_ruling_verdict_flip_added_word_or_reordering_is_refused']),
    ('AC-3-unreadable', [('        if not words:', '        if False:')],
     ['test_rewritten_report_without_verdict_word_is_refused']),
    ('AC-4-final-clock', [('        report_commit = settled[0]', '        report_commit = origins[0]')],
     ['test_corrected_report_without_ruling_names_final_text_commit']),
    ('AC-4-old-text-return', [('            if identities - known or ancestor(settled[0], commit):',
                              '            if identities - known:')],
     ['test_old_text_returning_after_final_text_cannot_reset_clock']),
    ('AC-5-recovery', [('hold dispatch and bring it to the Captain', 'hold dispatch and report the missing history to FO')],
     ['test_rewrite_after_native_ruling_or_nonclearing_gate_is_refused',
      'test_pre_ruling_verdict_flip_added_word_or_reordering_is_refused',
      'test_rewritten_report_without_verdict_word_is_refused']),
]
results = []
for name, replacements, tests in mutations:
    root = out / 'mutants' / name
    shutil.copytree(source / 'kc-dev-flow-2', root / 'kc-dev-flow-2',
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    code = original
    for old, new in replacements:
        assert code.count(old) == 1, (name, old, code.count(old))
        code = code.replace(old, new)
    script = root / 'kc-dev-flow-2/scripts/dispatch_records.py'
    script.write_text(code)
    command = [sys.executable, '-B', str(script.with_name('test_dispatch_records.py')),
               *['LiveValidationRulingTests.' + name for name in tests]]
    done = subprocess.run(command, capture_output=True, text=True, env=env, cwd=source)
    (out / (name + '.log')).write_text(done.stdout + done.stderr)
    killed = done.returncode == 1 and 'FAIL:' in done.stderr and 'ERROR:' not in done.stderr
    results.append({'name': name, 'status': 'passed' if killed else 'failed',
                    'message': f'mutant test exit={done.returncode}; assertion failure required',
                    'command': command})
    print(name, 'killed' if killed else 'SURVIVED/ERROR', flush=True)
(out / 'mutations.json').write_text(json.dumps(results, indent=2) + '\n')
assert all(r['status'] == 'passed' for r in results), results
