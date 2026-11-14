import argparse
from datetime import datetime
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

CANDIDATE = '02fcf256d8ca2aa4f4d44edd64d7162e3c049b1d'
READING = 'edeaf1fcd589006a8aa623ca380391a4854368cf'
FIRST = 'c4f37b507347bf969cb9b76d7963aee5d4270df7'


def main():
    parser = argparse.ArgumentParser(description='Offline replay of the second reading; no agent or network.')
    parser.add_argument('private_clone', type=Path)
    parser.add_argument('task_file', type=Path)
    parser.add_argument('scratch_root', type=Path)
    args = parser.parse_args()
    repo, task, scratch = (p.resolve() for p in (args.private_clone, args.task_file, args.scratch_root))
    assert task.is_file() and scratch.is_dir()
    assert repo != scratch and repo not in scratch.parents
    assert task.parent != scratch and task.parent not in scratch.parents
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')

    def git(*argv):
        return subprocess.check_output(['git', '-C', str(repo), *argv], env=env)

    assert git('rev-parse', 'HEAD').decode().strip() == CANDIDATE
    assert not git('status', '--porcelain')
    git('merge-base', '--is-ancestor', FIRST, READING)
    git('merge-base', '--is-ancestor', READING, CANDIDATE)
    assert not git('diff', READING, CANDIDATE, '--', 'behaviour/cells')
    before = git('show', READING + ':behaviour/run_cell.py')
    after = git('show', CANDIDATE + ':behaviour/run_cell.py')
    assert before.replace(b'Second reading (reading v2)', b'Second, confirmatory reading (reading v2)') == after
    committed = datetime.fromisoformat(git('show', '-s', '--format=%cI', READING).decode().strip())

    with tempfile.TemporaryDirectory(prefix='acceptance-', dir=scratch) as temporary:
        root = Path(temporary)
        with tarfile.open(fileobj=io.BytesIO(git('archive', CANDIDATE))) as archive:
            archive.extractall(root, filter='data')
        cell, = (root / 'behaviour/cells').glob('*-v2')
        runner = root / 'behaviour/run_cell.py'
        spec = importlib.util.spec_from_file_location('reading_runner', runner)
        reading = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(reading)
        config = reading.load_cell(cell)
        results = root / 'behaviour/results' / cell.name
        runs = reading.run_dirs(results)
        assert len(runs) == len(config['spec']['arms']) * config['spec']['trials']
        for run in runs:
            manifest = reading.load_json(run / 'manifest.json')
            assert manifest['status'] == 'collected' and manifest['stop_reason'] == 'finished'
            assert manifest['reading_commit'] == READING
            assert manifest['contamination_rule'] == 'v2'
            first = min(datetime.fromisoformat(e['timestamp'].replace('Z', '+00:00'))
                        for _, e in reading.events(reading.stream_of(run)) if e.get('timestamp'))
            assert committed < datetime.fromisoformat(manifest['prepared_at']) < first
        print('PASS: frozen rules precede every stored preparation and transcript start')

        def command(*argv, expected=0):
            result = subprocess.run([sys.executable, '-B', str(runner), *map(str, argv)],
                                    cwd=root, env=env, capture_output=True)
            assert result.returncode == expected, 'unexpected exit from ' + str(argv[0])
            return result.stdout

        original = (results / 'table.md').read_bytes()
        assert command('table', cell) == original == (results / 'table.md').read_bytes()
        assert command('scan', cell) == (results / 'scan.out').read_bytes()
        collection = (results / 'collect.out').read_text()
        by_arm = {arm: [] for arm in config['spec']['arms']}
        for run in runs:
            manifest = reading.load_json(run / 'manifest.json')
            grade = reading.grade_run(run, config)
            expected = reading.describe(grade)
            assert command('grade', run).decode().strip() == expected
            assert expected in next(line for line in collection.splitlines() if line.startswith(run.name + ':'))
            scanned = reading.scan_run(run)
            assert not scanned['breaches'] and not scanned['unscanned'] and not scanned['keys']
            by_arm[manifest['arm']].append(dict(grade, contaminated=False, unscanned=False))
        assert reading.final_reading(by_arm, version=2) == ('NO DIFFERENCE',) * 3
        print('PASS: table, collection grades, scan and both decision readings reproduce')

        command('selfcheck', cell)
        assert b'cap reached' in command('prepare', cell, '--dry-run', '--results', cell / 'falsifiers/capped', expected=1)
        assert b'cell halted' in command('prepare', cell, '--dry-run', '--results', cell / 'falsifiers/halted', expected=1)
        print('PASS: existing grading and contamination fixtures; both preparation refusals')

        previous_name, = config['spec']['launch_records_also_in']
        previous_cell = root / 'behaviour/cells' / previous_name
        previous_results = root / 'behaviour/results' / previous_name
        for path in [*(p for p in previous_cell.rglob('*') if p.is_file()),
                     *(p for p in previous_results.rglob('*') if p.is_file() and p.name != 'POST-HOC.md')]:
            rel = path.relative_to(root).as_posix()
            assert path.read_bytes() == git('show', FIRST + ':' + rel)
        previous_table = (previous_results / 'table.md').read_bytes()
        assert command('table', previous_cell) == previous_table
        assert b'first reading: CANNOT DISCRIMINATE (contamination changes the reading)' in previous_table
        assert reading.cell_state(config, results)['records'] <= config['spec']['launch_cap']
        print('PASS: first reading remains byte-identical and combined launch records stay within the cap')

        groups = {'run_ids': set(), 'session_ids': set(), 'case_slug': set(),
                  'private_names': {repo.name, str(repo)}, 'case_content_exact_lines': set()}
        remotes = subprocess.run(['git', '-C', str(repo), 'config', '--get-regexp', r'^remote\..*\.url$'],
                                 env=env, capture_output=True, text=True)
        for line in remotes.stdout.splitlines():
            remote = line.split(None, 1)[1]
            groups['private_names'].add(remote)

        def session_ids(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    if key.lower().replace('_', '') == 'sessionid' and isinstance(child, str) and child:
                        groups['session_ids'].add(child)
                    session_ids(child)
            elif isinstance(value, list):
                for child in value:
                    session_ids(child)

        for source_cell in (cell, previous_cell):
            source_config = reading.load_cell(source_cell)
            groups['case_slug'].add(source_config['spec']['case']['slug'])
            source_results = root / 'behaviour/results' / source_cell.name
            for run in reading.run_dirs(source_results):
                manifest = reading.load_json(run / 'manifest.json')
                groups['run_ids'].add(manifest['run_id'])
                session_ids(manifest)
                for _, event in reading.events(reading.stream_of(run)):
                    session_ids(event)
            for path in [*source_results.glob('*/task-after.md'), *source_cell.glob('falsifiers/**/*.md')]:
                groups['case_content_exact_lines'].update(line for line in path.read_text().splitlines()
                                                         if len(line) > 100 and not line.startswith(('---', '|', '  ', '```')))
        folder = task.with_suffix('')
        lines = [line for path in [task, *(p for p in folder.rglob('*') if p.is_file())]
                 for line in path.read_text(errors='replace').splitlines()]
        counts = {name: sum(any(marker in line for marker in markers) for line in lines)
                  for name, markers in groups.items()}
        print(json.dumps(counts, sort_keys=True))
        assert not any(counts.values()), 'public task marker scan found hits'
        assert not git('status', '--porcelain')
        assert git('rev-parse', 'HEAD').decode().strip() == CANDIDATE
        print('PASS: scoped privacy marker scan; source checkout unchanged')


if __name__ == '__main__':
    main()
