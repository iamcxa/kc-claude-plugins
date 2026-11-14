#!/usr/bin/env python3
"""Run public-state acceptance on throwaways; arguments: CODE STATE SPACEDOCK RUN_DIR."""
from collections import Counter
import contextlib
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tarfile
from unittest import mock

code, state, binary, run = map(Path, sys.argv[1:])
os.environ['SPACEDOCK_BIN'] = str(binary)
sys.path.insert(0, str(code / 'kc-dev-flow-2/scripts'))
import scratch
import state_guard
from test_dispatch_stage import DispatchStageTests
from test_state_guard import StateGuardTests

run.mkdir(parents=True, exist_ok=True)
results, commands = [], []
def public(text):
    return text.replace(str(Path.home()), '~')

def record(name, **facts):
    results.append(dict(name=name, status='passed', **facts))

def git(root, *args):
    done = subprocess.run(['git', '-C', str(root), *map(str,args)], capture_output=True, check=True)
    return done.stdout

fixture = DispatchStageTests('test_scratch_in_record_and_real_dispatch_artifact_without_changing_input')
fixture.setUp()
try:
    original = fixture.call
    def observed(args, *a, **kw):
        done = original(args, *a, **kw)
        commands.append(dict(command=public(shlex.join(map(str,args))), exit=done.returncode,
                             stdout=public(done.stdout or ''), stderr=public(done.stderr or '')))
        return done
    fixture.call = observed
    built = fixture.build()
    stamp = fixture.git(fixture.state, 'rev-parse', 'HEAD')
    prompt = Path(json.loads(built.stdout)['dispatch_file_path']).read_bytes()
    assert os.fsencode(code / 'kc-dev-flow-2') in prompt
    assert os.fsencode(Path.home()) in prompt
    saved = fixture.record().read_bytes()
    assert os.fsencode(Path.home()) not in saved
    fixture.call([sys.executable, '-B', code / 'kc-dev-flow-2/scripts/dispatch_records.py', fixture.folder])
    role = fixture.role()
    assert os.fsencode(code/'kc-dev-flow-2') in role.stdout.encode()
    assert os.fsencode(Path.home()) not in fixture.record('engineering-reviewer').read_bytes()
    target = fixture.folder / 'evidence/ideation-1'
    target.mkdir(parents=True)
    text = ('cwd: ' + str(code) + '\n').encode()
    (target / 'cwd.log').write_bytes(text)
    (target / 'large.log').write_bytes(text * (300000 // len(text) + 1))
    (target / 'supplied.gz').write_bytes(gzip.compress(text, mtime=13))
    closed = fixture.call([sys.executable, '-B', code / 'kc-dev-flow-2/scripts/scratch.py',
                           'close', fixture.folder, 'ideation-1'])
    assert not (target / 'large.log').exists()
    assert (target / 'large.log.gz').exists()
    for path in target.iterdir():
        data = path.read_bytes()
        if data.startswith(b'\x1f\x8b'):
            data = gzip.decompress(data)
        assert os.fsencode(Path.home()) not in data
    fixture.git(fixture.state, 'add', '--', fixture.folder.relative_to(fixture.state))
    fixture.git(fixture.state, 'commit', '-m', 'test: sealed public evidence')
    sealed = fixture.git(fixture.state, 'rev-parse', 'HEAD')
    compiled, present = state_guard.patterns(fixture.state)
    assert present
    hits = Counter()
    scanned = 0
    for revision in (stamp, sealed):
        for name in filter(None, git(fixture.state, 'ls-tree', '-r', '-z', '--name-only', revision).split(b'\0')):
            data = git(fixture.state, 'cat-file', 'blob', revision + ':' + os.fsdecode(name))
            if data.startswith(b'\x1f\x8b'):
                data = gzip.decompress(data)
            scanned += 1
            for kind, pattern in compiled:
                hits[kind] += bool(pattern.search(data))
    assert not sum(hits.values()), dict(hits)
    fixture.git(fixture.state, 'push', 'origin', 'spacedock-state/dev2')
    remote = fixture.base / 'dispatch-code.git'
    assert git(remote, 'rev-parse', 'spacedock-state/dev2').decode().strip() == sealed
    for revision in git(remote, 'rev-list', 'spacedock-state/dev2').decode().splitlines():
        for name in filter(None, git(remote, 'ls-tree', '-r', '-z', '--name-only', revision).split(b'\0')):
            data = git(remote, 'cat-file', 'blob', revision + ':' + os.fsdecode(name))
            if data.startswith(b'\x1f\x8b'):
                data = gzip.decompress(data)
            assert not any(pattern.search(data) for _, pattern in compiled)
    record('AC-1 real dispatch and sealed committed bytes', stamp=stamp, sealed=sealed,
           blobs=scanned, hits=dict(hits), prompt_real_paths=True, role_prompt_real_paths=True, large_input_over_256_KiB=True,
           source_unchanged=True, close_exit=closed.returncode)
finally:
    fixture.doCleanups()

for method in ('test_real_commit_refusals_keep_staged_bytes_and_clean_push_passes',
               'test_push_scans_every_commit_even_after_deletion',
               'test_warn_then_refuse_home_and_email_and_do_not_scan_product_worktree'):
    fixture = StateGuardTests(method)
    fixture.setUp()
    original = fixture.run_command
    try:
        def observed(args, *a, **kw):
            done = original(args, *a, **kw)
            words = list(map(str,args))
            if any(word in words for word in ('install', 'check', 'commit', 'push')):
                commands.append(dict(command=public(shlex.join(words)), exit=done.returncode,
                                     stdout=public(done.stdout or ''), stderr=public(done.stderr or '')))
            return done
        fixture.run_command = observed
        getattr(fixture, method)()
        if method == 'test_real_commit_refusals_keep_staged_bytes_and_clean_push_passes':
            with mock.patch.dict(os.environ, fixture.env, clear=True):
                compiled, present = state_guard.patterns(fixture.state)
            assert present
            for revision in git(fixture.remote, 'rev-list', 'spacedock-state/test').decode().splitlines():
                for name in filter(None, git(fixture.remote, 'ls-tree', '-r', '-z', '--name-only', revision).split(b'\0')):
                    data = git(fixture.remote, 'cat-file', 'blob', revision + ':' + os.fsdecode(name))
                    assert not any(pattern.search(data) for _, pattern in compiled)
            fresh = fixture.base / 'fresh-clone'
            fixture.run_command(['git', 'clone', '-q', '--branch', 'spacedock-state/test', fixture.remote, fresh])
            unguarded = fixture.run_command([sys.executable, '-B', state_guard.__file__, 'check', fresh], expected=1)
            assert 'unguarded:' in unguarded.stdout
        record(('AC-5 ' if 'warn_then' in method else 'AC-3 ') + method)
    finally:
        fixture.doCleanups()

base = 'c2f035b6612f5edb42220576b3414e993531ffd6'
baseline = run / 'baseline'
baseline.mkdir(exist_ok=True)
with tarfile.open(fileobj=io.BytesIO(git(code, 'archive', base, 'kc-dev-flow-2'))) as archive:
    archive.extractall(baseline, filter='data')
selected = []
for folder in sorted(state.joinpath('_archive').iterdir()):
    if folder.is_dir() and (folder/'dispatch').is_dir() and list(folder.glob('evidence/*/SHA256SUMS')):
        selected.append(folder)
for folder in sorted(state.iterdir()):
    if folder.is_dir() and (folder/'dispatch').is_dir():
        count = sum(len(p.read_text().splitlines()) for p in folder.glob('evidence/*/SHA256SUMS'))
        if count in (340, 1013):
            selected.append(folder)
assert len(selected) == 7
corpus = []
for index, folder in enumerate(selected, 1):
    statuses = []
    sources = list((folder/'dispatch').glob('*.md')) + list(folder.glob('evidence/*/SHA256SUMS'))
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    for root in (baseline, code):
        command = [sys.executable, '-B', str(root/'kc-dev-flow-2/scripts/dispatch_records.py'), str(folder)]
        done = subprocess.run(command, capture_output=True)
        statuses.append(done.returncode)
    checked = mismatches = 0
    for manifest in sorted(folder.glob('evidence/*/SHA256SUMS')):
        for line in manifest.read_text().splitlines():
            digest, name = line.split('  ', 1)
            path = manifest.parent / name
            data = path.read_bytes() if path.is_file() else gzip.decompress(path.with_name(path.name + '.gz').read_bytes())
            checked += 1
            mismatches += hashlib.sha256(data).hexdigest() != digest
    assert statuses == [0,0]
    assert before == {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    corpus.append(dict(sample=index, record_exit_baseline=statuses[0], record_exit_candidate=statuses[1],
                       digests_checked=checked, preexisting_mismatches=mismatches))
assert sum(row['preexisting_mismatches'] for row in corpus) == 1
record('AC-2 seven historical task folders', samples=corpus,
       limit='One pre-existing digest mismatch remains; six folders have none. No historical bytes were rewritten.')
(run/'acceptance.json').write_text(json.dumps(results, indent=2) + '\n')
(run/'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
print(json.dumps(results, indent=2))
