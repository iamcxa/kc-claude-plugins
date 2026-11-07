import argparse
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument('repo', type=Path)
parser.add_argument('out', type=Path)
args = parser.parse_args()
repo, out = args.repo.resolve(), args.out.resolve()
out.mkdir(parents=True, exist_ok=True)
base = '139feeaee7ce037a0c6535568cd6bd103155cbae'
rows = []

def run(name, command, cwd, expected=0, env=None, contains=None):
    done = subprocess.run(list(map(str, command)), cwd=cwd, env=env, capture_output=True, text=True)
    log = out / (name + '.log')
    log.write_text(done.stdout + done.stderr)
    passed = done.returncode == expected and (contains is None or contains in log.read_text())
    rows.append({'name': name, 'status': 'passed' if passed else 'failed', 'command': list(map(str, command)),
                 'exit': done.returncode, 'expected': expected, 'log': str(log), 'required_text': contains})
    (out / 'proof.json').write_text(json.dumps(rows, indent=2) + '\n')
    print(f'{name}: exit {done.returncode}, expected {expected}, {"PASS" if passed else "FAIL"}', flush=True)
    if not passed:
        raise AssertionError(log.read_text())
    return done

def git(*parts):
    return subprocess.run(['git', '-C', str(repo), *parts], check=True, capture_output=True).stdout

def export(revision, destination):
    with tarfile.open(fileobj=io.BytesIO(git('archive', revision))) as archive:
        archive.extractall(destination, filter='data')

def clear_caches(root):
    for cache in root.rglob('__pycache__'):
        shutil.rmtree(cache)

source_path = Path('kc-adr/scripts/adr_lint.py')
test_path = Path('kc-adr/scripts/test_adr_lint.py')
copy_path = Path('kc-dev-flow-2/scripts/adr_lint.py')
source = (repo / source_path).read_text()
positive = 'ProtectedPathTests.test_asserting_the_recorded_supersession_is_not_a_stale_pointer'
both = 'ProtectedPathTests.test_a_file_pointing_at_a_superseded_adr_fails_naming_file_and_newer_adr'
wrong = 'ProtectedPathTests.test_asserting_a_different_successor_still_fails'
missing = 'ProtectedPathTests.test_the_assertion_does_not_supply_the_successors_own_pointer'
exact = 'and re.search(rf"Superseded by {superseded[number]:04d}(?!\\d)", line)'
assert exact in source
with tempfile.TemporaryDirectory(prefix='adr-pointer-proof-') as temporary:
    scratch = Path(temporary)
    export(base, scratch)
    for path in (source_path, test_path, copy_path, Path('kc-dev-flow-2/scripts/test_sd_dispatch.py')):
        (scratch / path).write_bytes((repo / path).read_bytes())
    run('candidate-25-tests', ['python3', '-B', test_path], scratch)
    mutations = [
        ('base-fails-assertion', git('show', f'{base}:{source_path}').decode(), positive, 'points at ADR 0002, Superseded by 0003'),
        ('removed-exception-fails', source.replace('cited_by(site, skip_assertions=True)', 'cited_by(site)'), positive, 'points at ADR 0002, Superseded by 0003'),
        ('file-wide-successor-fails', source.replace(exact, 'and superseded[number] in map(int, cites.findall(site.read_text(errors="replace")))'), both, 'AssertionError: 0 != 1'),
        ('wrong-successor-fails', source.replace(exact, 'and re.search(r"Superseded by \\d{4}(?!\\d)", line)'), wrong, 'AssertionError: 0 != 1'),
        ('invented-successor-pointer-fails', source.replace('elif int(path.name[:4]) not in cited_by(site):', 'elif int(path.name[:4]) not in (cited_by(site) | {int(n) for n in re.findall(r"Superseded by (\\d{4})", site.read_text(errors="replace"))}):'), missing, 'AssertionError: 0 != 1'),
        ('word-boundary-regression-fails', source.replace('rf"Superseded by', 'rf"\\bSuperseded by'), positive, 'points at ADR 0002, Superseded by 0003'),
    ]
    for name, changed, test, message in mutations:
        assert changed != source
        (scratch / source_path).write_text(changed)
        clear_caches(scratch)
        run(name, ['python3', '-B', test_path, test], scratch, 1, contains=message)
    (scratch / source_path).write_text(source)
    (scratch / copy_path).write_text(source + '\n')
    clear_caches(scratch)
    run('copy-drift-fails', ['bash', 'scripts/kc-adr-copy-sync.sh', 'check'], scratch, 1, contains='differs from kc-adr/scripts/adr_lint.py')
    (scratch / copy_path).write_text(source)
    run('copy-restored-passes', ['bash', 'scripts/kc-adr-copy-sync.sh', 'check'], scratch)

with tempfile.TemporaryDirectory(prefix='adr-pointer-history-') as temporary:
    scratch = Path(temporary)
    export('ae7750375', scratch)
    dispatch = scratch / 'kc-dev-flow-2/scripts/test_sd_dispatch.py'
    old = dispatch.read_text()
    unsplit = old.replace('(ROOT.parent / "docs/adr" / "0047-', '(ROOT.parent / "docs/adr/0047-')
    assert old != unsplit
    dispatch.write_text(unsplit)
    env = {**os.environ, 'GIT_DIR': git('rev-parse', '--absolute-git-dir').decode().strip(), 'GIT_WORK_TREE': str(scratch)}
    command = ['python3', '-B', copy_path, 'docs/adr', '--since', 'ba055b8a7', '--require', '0064']
    clear_caches(scratch)
    run('historical-unsplit-fails', command, scratch, 1, env, 'points at ADR 0047, Superseded by 0050')
    (scratch / copy_path).write_text(source)
    clear_caches(scratch)
    run('historical-candidate-passes', command, scratch, env=env)
print('All candidate and mutation expectations passed.', flush=True)
