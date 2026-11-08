import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

wt = Path(sys.argv[1])
evidence = Path(__file__).parent
scripts = wt / 'kc-dev-flow-2/scripts'
source = (scripts / 'design_surfaces.py').read_text()
guard = '    elif foreign:\n        return "not run", f"backlog briefing binds {bound.group(2)}, not this task file"\n'
foreign = '    foreign = unarchived(bound.group(2)) != unarchived(task_path(task))\n'
cases = [
    ('removed guard', source.replace(guard, ''), 'test_a_foreign_binding_without_scope_is_not_run_before_and_after_a_scope_edit'),
    ('unconditional guard', source.replace('    elif foreign:', '    elif True:'), 'test_a_scope_line_added_after_the_backlog_gate_holds_with_a_line_addressed_to_fo'),
    ('folder path guessed from parent', source.replace('return git_out(task, "rev-parse", "--show-prefix").stdout.decode().rstrip("\\n") + task.name', 'return task.parent.name + ".md"'), 'test_a_folder_task_bound_to_itself_is_checked_even_when_untracked_or_archived'),
    ('guard only when Scope missing', source.replace('    elif foreign:', '    elif foreign and not scope_lines(baseline):'), 'test_a_foreign_binding_with_its_own_scope_is_not_run'),
    ('guard before amendment lookup', source.replace(foreign, foreign + '    if foreign:\n        return "not run", "foreign binding before amendment"\n'), 'test_a_dated_amendment_supplies_the_baseline_despite_a_foreign_binding'),
]
rows = []
for name, mutant, method in cases:
    assert mutant != source, name
    with tempfile.TemporaryDirectory(prefix='scope-mutation-', dir=evidence) as folder:
        target = Path(folder) / 'scripts'
        shutil.copytree(scripts, target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        (target / 'design_surfaces.py').write_text(mutant)
        assert not list(target.rglob('__pycache__'))
        done = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'test_design_surfaces.ScopeCheckTests.' + method], cwd=target, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}, capture_output=True, text=True)
        (evidence / ('mutation-' + name.replace(' ', '-') + '.log')).write_text(done.stdout + done.stderr)
        assert done.returncode == 1 and 'FAIL:' in done.stderr and 'ERROR:' not in done.stderr, (name, done.stdout, done.stderr)
        rows.append({'name': name, 'status': 'passed', 'message': 'Mutant failed the named behavior assertion: ' + method})
allowed = ['kc-dev-flow-2/scripts/design_surfaces.py', 'kc-dev-flow-2/scripts/test_design_surfaces.py']
changed = subprocess.check_output(['git', '-C', json.loads((evidence / 'metadata.json').read_text())['wt'], 'diff', '--name-only', '139feeaee7ce037a0c6535568cd6bd103155cbae', '2760f259379e9c3bb43bab9efa56d90c5b657ab1'], text=True).splitlines()
assert sorted(changed) == allowed, changed
assert sorted(changed + ['kc-dev-flow-2/scripts/unapproved.py']) != allowed
rows.append({'name': 'AC-5 file-boundary falsifier', 'status': 'passed', 'message': 'Adding an unapproved path fails the exact two-file boundary.'})
(evidence / 'mutations.json').write_text(json.dumps(rows, indent=2) + '\n')
print(f'{len(rows)} falsifiers caught')
