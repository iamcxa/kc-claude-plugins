import argparse
import ast
from datetime import datetime
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

HEAD = 'c4f37b507347bf969cb9b76d7963aee5d4270df7'
READING = 'b5489642f9ce99392f43ed52029ffd0d333bd38d'


def main():
    parser = argparse.ArgumentParser(description='Offline checks of the committed first reading; private inputs stay outside state.')
    parser.add_argument('private_clone', type=Path)
    parser.add_argument('task_file', type=Path)
    parser.add_argument('scratch_root', type=Path)
    args = parser.parse_args()
    repo = args.private_clone.resolve()
    task = args.task_file.resolve()
    scratch = args.scratch_root.resolve()
    assert scratch.is_dir() and task.is_file()

    def git(*argv):
        return subprocess.check_output(['git', '-C', str(repo), *argv])

    assert git('rev-parse', 'HEAD').decode().strip() == HEAD
    assert not git('status', '--porcelain')
    git('merge-base', '--is-ancestor', READING, HEAD)
    assert not git('diff', READING, HEAD, '--', 'behaviour/cells')
    old = ast.parse(git('show', READING + ':behaviour/run_cell.py'))
    new = ast.parse(git('show', HEAD + ':behaviour/run_cell.py'))
    functions = ('grade_text', 'grade_run', 'scan_stream', 'scan_run', 'read_one', 'final_reading')
    for name in functions:
        before = next(n for n in old.body if isinstance(n, ast.FunctionDef) and n.name == name)
        after = next(n for n in new.body if isinstance(n, ast.FunctionDef) and n.name == name)
        assert ast.dump(before) == ast.dump(after)
    committed = datetime.fromisoformat(git('show', '-s', '--format=%cI', READING).decode().strip())

    with tempfile.TemporaryDirectory(prefix='acceptance-', dir=scratch) as temporary:
        root = Path(temporary)
        with tarfile.open(fileobj=io.BytesIO(git('archive', HEAD))) as archive:
            archive.extractall(root, filter='data')
        cell, = (root / 'behaviour/cells').iterdir()
        runner = root / 'behaviour/run_cell.py'
        module = importlib.util.spec_from_file_location('reading_runner', runner)
        reading = importlib.util.module_from_spec(module)
        module.loader.exec_module(reading)
        config = reading.load_cell(cell)
        results = root / 'behaviour/results' / cell.name
        runs = reading.run_dirs(results)
        collected = [p for p in runs if reading.load_json(p / 'manifest.json').get('status') == 'collected']
        assert len(collected) == 9 and len(runs) == 10
        for run in collected:
            manifest = reading.load_json(run / 'manifest.json')
            assert manifest['reading_commit'] == READING
            first = min(datetime.fromisoformat(e['timestamp'].replace('Z', '+00:00'))
                        for _, e in reading.events(reading.stream_of(run)) if e.get('timestamp'))
            assert committed < datetime.fromisoformat(manifest['prepared_at']) < first
        print('PASS: frozen reading predates all nine collected runs; historical abort excluded from that claim')

        def command(*argv, expected=0):
            result = subprocess.run([sys.executable, '-B', str(runner), *map(str, argv)], cwd=root, capture_output=True)
            assert result.returncode == expected, 'unexpected exit from ' + str(argv[0])
            return result.stdout

        original = (results / 'table.md').read_bytes()
        assert command('table', cell) == original == (results / 'table.md').read_bytes()
        collection = (results / 'collect.out').read_text()
        for run in collected:
            expected = reading.describe(reading.grade_run(run, config))
            assert command('grade', run).decode().strip() == expected
            assert expected in next(line for line in collection.splitlines() if line.startswith(run.name + ':'))
        print('PASS: table bytes and each collected grade reproduce with the frozen rules')

        command('selfcheck', cell)
        assert b'cap reached' in command('prepare', cell, '--dry-run', '--results', cell / 'falsifiers/capped', expected=1)
        assert b'cell halted' in command('prepare', cell, '--dry-run', '--results', cell / 'falsifiers/halted', expected=1)
        print('PASS: existing grading fixtures and both preparation refusals behave as committed')

        command('scan', cell)
        for run in collected:
            result = reading.scan_run(run)
            assert result['breaches'] and not result['unscanned'] and not result['keys']
        assert 'first reading: CANNOT DISCRIMINATE (contamination changes the reading)' in original.decode()
        print('PASS: contamination is retained and the committed final reading remains indeterminate')

        groups = {'run_ids': set(), 'session_ids': set(), 'case_slug': {config['spec']['case']['slug']},
                  'private_names': {repo.name}, 'case_content_exact_lines': set()}
        for run in runs:
            manifest = reading.load_json(run / 'manifest.json')
            groups['run_ids'].add(manifest['run_id'])
            for key, value in manifest.items():
                if key.lower().replace('_', '') == 'sessionid' and isinstance(value, str):
                    groups['session_ids'].add(value)
            for _, event in reading.events(reading.stream_of(run)):
                for key, value in event.items():
                    if key.lower().replace('_', '') == 'sessionid' and isinstance(value, str):
                        groups['session_ids'].add(value)
        for path in [*results.glob('*/task-after.md'), *cell.glob('falsifiers/*.md')]:
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
        print('PASS: scoped privacy marker scan; source checkout unchanged')


if __name__ == '__main__':
    main()
