import json, os, sys
from pathlib import Path
os.environ['SPACEDOCK_BIN'] = '/Users/kent/.local/bin/spacedock'
os.environ['DISPATCH_STAGE_LOG'] = '/tmp/pr827-validation/evidence/probe-calls.jsonl'
sys.path.insert(0, '/tmp/pr827-validation/candidate/kc-dev-flow-2/scripts')
from test_dispatch_stage import DispatchStageTests

out = Path('/tmp/pr827-validation/evidence')
rows = []
def probe(name, body):
    t = DispatchStageTests()
    try:
        t.setUp()
        data = body(t)
        rows.append(dict(name=name, **data))
    finally:
        t.doCleanups()
    (out / 'probes.json').write_text(json.dumps(rows, indent=2) + '\n')
    print(json.dumps(rows[-1]), flush=True)

def crlf(t):
    t.checklist.write_bytes(b'Inspect the dispatch seam\r\nKeep these supplied line endings\r\n')
    t.notes.write_bytes(t.notes.read_bytes().replace(b'\n', b'\r\n'))
    result = t.role()
    record = t.record('engineering-reviewer').read_bytes()
    for name, data in [('crlf-checklist.txt', t.checklist.read_bytes()), ('crlf-notes.txt', t.notes.read_bytes()), ('crlf-record.md', record)]:
        (out / name).write_bytes(data)
    return dict(exit=result.returncode, checklist_bytes_preserved=t.checklist.read_bytes() in record, notes_bytes_preserved=t.notes.read_bytes() in record, stdout_matches_record=result.stdout.encode() == record, input_crlf=t.checklist.read_bytes().count(b'\r\n'), record_crlf=record.count(b'\r\n'))

def each_missing(t):
    notes = t.notes.read_text()
    results = []
    for label, bad in [('package', '\n'.join(notes.splitlines()[1:]) + '\n'), ('completion', '\n'.join(x for x in notes.splitlines() if 'completion' not in x) + '\n')]:
        t.notes.write_text(bad)
        p = t.role(expected=1)
        assert not p.stdout and not t.record('engineering-reviewer').exists()
        results.append(dict(missing=label, exit=p.returncode, stderr=p.stderr))
    return dict(results=results)

def folder_layout(t):
    t.folder.mkdir()
    old = t.entity
    t.entity = t.folder / 'index.md'
    old.rename(t.entity)
    t.git(t.state, 'add', '--', old.name, t.slug)
    t.git(t.state, 'commit', '-m', 'test: folder layout')
    p = t.role()
    t.assert_committed(t.record('engineering-reviewer'), f'state: update {t.slug}')
    return dict(exit=p.returncode, committed=True)

def unknown(t):
    p = t.role(extra=('--model', 'unknown-family'), expected=1)
    assert not p.stdout and not t.record('engineering-reviewer').exists()
    return dict(exit=p.returncode, stderr=p.stderr)

probe('CRLF supplied inputs', crlf)
probe('Missing fields independently', each_missing)
probe('Folder task layout', folder_layout)
probe('Unknown model limit', unknown)
