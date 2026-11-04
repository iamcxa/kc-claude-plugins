import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

WT = Path(os.environ.get('DIAGNOSIS_CODE_ROOT', '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-diagnosis-rounds-count-toward-step-back')).resolve()
OUT = Path(os.environ.get('DIAGNOSIS_EVIDENCE_DIR', '/tmp/opencode/diagnosis-rounds/message-repair')).resolve()
BASE = '713d4e6ed6381e65fa6d8305e08b282ceb56a8fb'
PKG = WT / 'kc-dev-flow-2'
OLD = WT.parent / '.validation-baseline/kc-dev-flow-2'
ENV = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
       'GIT_CONFIG_SYSTEM': os.devnull, 'GIT_AUTHOR_NAME': 't', 'GIT_AUTHOR_EMAIL': 't@t',
       'GIT_COMMITTER_NAME': 't', 'GIT_COMMITTER_EMAIL': 't@t'}


def run(*args, cwd=WT):
    return subprocess.run(list(map(str, args)), cwd=cwd, capture_output=True, text=True, env=ENV)


def git(where, *args):
    result = run('git', '-C', where, *args)
    assert result.returncode == 0, result.stderr
    return result.stdout


def cli(package, name, *args):
    return run(sys.executable, '-B', package / 'scripts' / name, *args)


def base():
    if not OLD.exists():
        archive = subprocess.run(['git', '-C', str(WT), 'archive', BASE, 'kc-dev-flow-2'], capture_output=True, check=True)
        (WT.parent / '.validation-baseline').mkdir(exist_ok=True)
        with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tar:
            tar.extractall(WT.parent / '.validation-baseline', filter='data')


def load(name):
    sys.path.insert(0, str(PKG / 'scripts'))
    spec = importlib.util.spec_from_file_location(name, PKG / 'scripts' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def replay():
    source = Path(os.environ.get('DIAGNOSIS_QNOW_STATE', '/Users/kent/conductor/repos/qnow-adopt-dev2/docs/dev2/.spacedock-state'))
    revision = git(source, 'rev-parse', '290b47a39').strip()
    prefix = 'schedule-settings-match-design/dispatch/'
    records = {Path(path).name: git(source, 'show', f'{revision}:{path}')
               for path in git(source, 'ls-tree', '-r', '--name-only', revision, '--', prefix).splitlines()}
    hashes = {name: hashlib.sha256(text.encode()).hexdigest() for name, text in records.items()}
    target = OUT / 'replay'
    dispatch = target / 'dispatch'
    dispatch.mkdir(parents=True, exist_ok=True)
    symptom = 'validation-4 F1 phone-width freeze'
    distinct = {22: 'bootstrap shows no day cards', 23: 'focus after Apply', 27: 'mask left after Apply'}
    rows = []
    for k in range(14, 28):
        for path in dispatch.glob('*.md'):
            path.unlink()
        for name, text in records.items():
            if name.startswith('implementation-'):
                n = int(name.split('-')[1].split('.')[0])
                if n > k:
                    continue
                value = symptom if n in list(range(15, 22)) + [24, 25, 26] else distinct.get(n)
                if value:
                    text = f'Symptom: {value}\n' + text
            (dispatch / name).write_text(text)
        candidate = cli(PKG, 'dispatch_records.py', target)
        old = cli(OLD, 'dispatch_records.py', target)
        reminders = [line for line in candidate.stderr.splitlines() if 'step back:' in line]
        assert not any('step back:' in line for line in (old.stdout + old.stderr).splitlines())
        assert candidate.stdout == old.stdout and candidate.returncode == old.returncode
        assert bool(reminders) == (k in list(range(16, 22)) + [24, 25, 26]), (k, candidate.stderr)
        assert not any(label.lower() in line for line in reminders for label in distinct.values())
        rows.append({'k': k, 'candidate_exit': candidate.returncode, 'base_exit': old.returncode,
                     'candidate_stdout': candidate.stdout, 'candidate_stderr': candidate.stderr,
                     'base_stdout': old.stdout, 'base_stderr': old.stderr})
    (OUT / 'replay.json').write_text(json.dumps({'source': str(source), 'revision': revision, 'hashes': hashes, 'runs': rows}, indent=2))
    print('AC-5: first reminder at 16; none through 15 or on distinct symptoms 22, 23, 27; base has none; 14 runs')


def fixture(root, count=0, missing=False):
    root.mkdir(parents=True, exist_ok=True)
    git(root, 'init', '-q', '-b', 'main')
    (root / 'task.md').write_text('---\nprofile: pilot\n---\n## FO alignment\nSurfaces: none\n')
    dispatch = root / 'task/dispatch'
    dispatch.mkdir(parents=True)
    for n in range(1, max(count + 1, 2) + 1):
        symptom = '' if n == 1 or missing else 'Symptom: validation-4 F1 phone-width freeze\n'
        (dispatch / f'implementation-{n}.md').write_text(f'Dispatched: 2026-11-03 {"a" * 40}\nModel: opus\n{symptom}'
                                                      '## Checklist\n- work\n## Scope notes\nPackage root: /pkg\nSend the completion message to `main`.\n')
    git(root, 'add', '-A')
    git(root, 'commit', '-qm', 'fixture')
    return dispatch


def words(package=PKG):
    rows = []
    for label, count, missing, limit in [('clean dispatch', 0, False, 0), ('repeat dispatch', 2, False, 48),
                                          ('missing header', 0, True, 26), ('idle and merge advisory', 2, False, 47),
                                          ('idle and merge owed', 3, False, 74)]:
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp)
            dispatch = fixture(state, count, missing)
            name = 'role_triggers.py' if label.startswith('idle') else 'dispatch_records.py'
            args = [state, 'task'] if name == 'role_triggers.py' else [dispatch.parent]
            before = cli(OLD, name, *args)
            after = cli(package, name, *args)
            assert before.returncode in (0, 1) and after.returncode in (0, 1), (before.stderr, after.stderr)
            old = [line for line in (before.stdout + before.stderr).splitlines() if not line.startswith('role triggers:')]
            new = [line for line in (after.stdout + after.stderr).splitlines() if not line.startswith('role triggers:')]
            added = [line for line in new if line not in old]
            cost = sum(len(line.split()) for line in added)
            assert cost <= limit, (label, cost, limit)
            rows.append({'name': label, 'before': sum(len(line.split()) for line in old),
                         'after': sum(len(line.split()) for line in new), 'added': cost, 'limit': limit,
                         'better': 'lower', 'base_lines': old, 'candidate_lines': new})
    for name in ('references/sd/workflow.md', 'scripts/lint-skills.py'):
        assert (OLD / name).read_bytes() == (package / name).read_bytes()
    rows += [{'name': label, 'before': 0, 'after': 0, 'added': 0, 'limit': 0, 'better': 'lower'}
             for label in ('startup', 'after archive')]
    rows.append({'name': 'workflow template', 'before': len((OLD / 'references/sd/workflow.md').read_text().split()),
                 'after': len((package / 'references/sd/workflow.md').read_text().split()), 'better': 'lower'})
    if package == PKG:
        (OUT / 'words.json').write_text(json.dumps(rows, indent=2))
    print('AC-8: per-moment word limits pass; workflow and budget unchanged')


def laws(package=PKG):
    tests = load('test_laws_check')
    with tempfile.TemporaryDirectory() as tmp:
        repo = tests.Repo(Path(tmp) / 'state')
        before = repo.commit('base', keep='x')
        repo.commit('task', t=tests.task())
        text = tests.record(checklist='- run adr_lint.py')
        repo.commit('repeat and missing', **{'t__dispatch__implementation-1': text,
                    't__dispatch__implementation-2': 'Symptom: freeze\n' + text,
                    't__dispatch__implementation-3': 'Symptom: freeze\n' + text,
                    't__dispatch__implementation-4': text})
        readme = Path(tmp) / 'README.md'
        readme.write_text('---\nentity-type: task\nextensions: []\n---\n')
        after = git(repo.path, 'rev-parse', 'HEAD').strip()
        one = cli(package, 'laws_check.py', repo.path, '--before', before, '--after', after, '--readme', readme)
        for path in (repo.path / 't/dispatch').glob('*.md'):
            path.write_text('\n'.join(line for line in path.read_text().splitlines() if not line.startswith('Symptom:')) + '\n')
        git(repo.path, 'add', '-A')
        git(repo.path, 'commit', '--amend', '--no-edit', '-q')
        two = cli(package, 'laws_check.py', repo.path, '--before', before, '--readme', readme)
        assert one.returncode == two.returncode == 1, (one.stdout, two.stdout)
        assert 'cannot' not in one.stdout.lower(), one.stdout
        assert 'cannot' not in two.stdout.lower(), two.stdout
        def semantic(output):
            import re
            return [re.sub(r'\(line \d+\)', '(line N)', re.sub(r'commit=[0-9a-f]+', 'commit=SHA', line)) for line in output.splitlines()
                    if line.startswith('violation: L2')]
        assert semantic(one.stdout) == semantic(two.stdout), (one.stdout, two.stdout)
        if package == PKG:
            (OUT / 'laws.json').write_text(json.dumps({'with_symptom': {'code': one.returncode, 'out': one.stdout},
                                                       'without_symptom': {'code': two.returncode, 'out': two.stdout}}, indent=2))
    print('AC-6: real L2 verdicts equal with reminders and missing hints; no Cannot')


def mutations():
    changes = [
        ('AC-1 first record counted for every symptom', 'role_triggers.py',
         'return {key: [(order[0], date) for order, date in sorted(rounds)] for key, rounds in groups.items()}',
         'return {key: [(1, None)] + [(order[0], date) for order, date in sorted(rounds)] for key, rounds in groups.items()}',
         'test_dispatch_records.SymptomDispatchTests.test_second_symptom_prints_questions_only_on_stderr_without_changing_verdict'),
        ('AC-1 reminders moved to stdout', 'dispatch_records.py', 'file=sys.stderr)', 'file=sys.stdout)',
         'test_dispatch_records.SymptomDispatchTests.test_second_symptom_prints_questions_only_on_stderr_without_changing_verdict'),
        ('AC-2 stage removed from grouping', 'role_triggers.py',
         'groups.setdefault((record[1], symptom), [])', 'groups.setdefault(("implementation", symptom), [])',
         'test_role_triggers.SymptomRoundsTest.test_groups_normalize_but_keep_stages_and_symptoms_separate'),
        ('AC-3 first record requires header', 'dispatch_records.py',
         'if int(record[2]) >= 2 and not symptom:', 'if int(record[2]) >= 1 and not symptom:',
         'test_dispatch_records.SymptomDispatchTests.test_missing_line_hints_but_only_strict_holds_and_first_and_none_pass'),
        ('AC-3 folder mode holds missing header', 'dispatch_records.py',
         'check_symptoms([path for _, path in newest.values()])',
         'symptom_status = check_symptoms([path for _, path in newest.values()])\n    if symptom_status:\n        return 1',
         'test_dispatch_records.SymptomDispatchTests.test_missing_line_hints_but_only_strict_holds_and_first_and_none_pass'),
        ('AC-4 dispatches read from disk', 'role_triggers.py', 'def read_records(state, slug, rev):',
         'def read_records(state, slug, rev):\n    return [(p.name, p.read_text()) for p in (Path(state) / slug / "dispatch").glob("*.md")]',
         'test_role_triggers.SymptomRoundsTest.test_second_advises_third_owes_and_only_committed_records_count'),
        ('AC-4 date test removed', 'role_triggers.py',
         'any(made >= group[2][1] for made in dated) if group[2][1] else calls or waivers', 'calls or waivers',
         'test_role_triggers.SymptomRoundsTest.test_date_model_and_waiver_clear_the_third_record_once'),
        ('AC-6 stderr output moved to stdout', 'dispatch_records.py', 'file=sys.stderr)', 'file=sys.stdout)', 'laws'),
        ('AC-7 advisory next prefix removed', 'role_triggers.py',
         "f'next: {slug} has 2 {stage} dispatches", "f'{slug} has 2 {stage} dispatches",
         'test_pr_watch.TasksTests.test_committed_second_symptom_round_is_forwarded_at_idle'),
        ('AC-8 word budget exceeded', 'role_triggers.py',
         'what breaks if this criterion or process is deleted?', 'extra extra extra what breaks if this criterion or process is deleted?', 'words'),
    ]
    results = []
    for index, (label, file, old, new, test) in enumerate(changes):
        target = WT.parent / '.validation-mutants' / str(index) / 'kc-dev-flow-2'
        shutil.copytree(PKG, target, ignore=shutil.ignore_patterns('__pycache__'), dirs_exist_ok=True)
        path = target / 'scripts' / file
        text = path.read_text()
        assert old in text, (label, old)
        path.write_text(text.replace(old, new))
        for cache in target.rglob('__pycache__'):
            shutil.rmtree(cache)
        if test in ('laws', 'words'):
            log = io.StringIO()
            with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
                try:
                    globals()[test](target)
                    code = 0
                except AssertionError as error:
                    print(error)
                    code = 1
            output = log.getvalue()
        else:
            done = run(sys.executable, '-B', '-m', 'unittest', test, cwd=target / 'scripts')
            code, output = done.returncode, done.stdout + done.stderr
            assert 'FAILED (failures=' in output, (label, code, output)
        (OUT / f'mutation-{index}.log').write_text(output)
        assert code != 0, f'mutant survived: {label}'
        results.append({'name': label, 'status': 'passed', 'message': f'mutant rejected, exit {code}; mutation-{index}.log'})
        print(f'killed {label}', flush=True)
    results.append({'name': 'AC-5 base has no symptom reminder', 'status': 'passed', 'message': '14 base replay runs print no step-back line; replay.json'})
    (OUT / 'mutations.json').write_text(json.dumps(results, indent=2))


if __name__ == '__main__':
    base()
    globals()[sys.argv[1]]()
