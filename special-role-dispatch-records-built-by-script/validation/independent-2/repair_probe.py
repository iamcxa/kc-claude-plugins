import hashlib, json, os, shutil, subprocess, sys
from pathlib import Path

home = Path(__file__).resolve().parent
out = home / 'evidence'
os.environ.update(SPACEDOCK_BIN='/Users/kent/.local/bin/spacedock',
                  GIT_AUTHOR_DATE='2026-11-10T00:00:00Z',
                  GIT_COMMITTER_DATE='2026-11-10T00:00:00Z')
sys.path.insert(0, str(home / 'candidate/kc-dev-flow-2/scripts'))
from test_dispatch_stage import DispatchStageTests, BINARY

rows, records = [], {}
for revision in ['previous', 'candidate']:
    for role in [True, False]:
        for newline in ['lf', 'crlf']:
            t = DispatchStageTests()
            try:
                t.setUp()
                kind = 'engineering-reviewer' if role else 'ideation'
                ending = b'\r\n' if newline == 'crlf' else b'\n'
                checklist = 'Check raw bytes\n保留內容\n'.encode().replace(b'\n', ending)
                notes = ('Package root: /declared/package\nSend your completion message to `main`.\n保留範圍\n').encode().replace(b'\n', ending)
                t.checklist.write_bytes(checklist)
                t.notes.write_bytes(notes)
                command = [sys.executable, '-B', str(home / revision / 'kc-dev-flow-2/scripts/dispatch_stage.py'),
                           '--workflow-dir', str(t.workflow), '--entity-path', str(t.entity),
                           '--role' if role else '--stage', kind, '--model', 'opus',
                           '--checklist-file', str(t.checklist), '--scope-notes-file', str(t.notes),
                           '--spacedock', BINARY]
                if not role:
                    command += ['--host', 'codex']
                p = subprocess.run(command, cwd=t.base, env=t.env, capture_output=True, timeout=30)
                assert p.returncode == 0, p.stderr
                record = t.record(kind)
                disk = record.read_bytes()
                committed = subprocess.check_output(['git', '-C', str(t.state), 'show', 'HEAD:' + str(record.relative_to(t.state))], env=t.env)
                expected = (f'# {kind}-1\nDispatched: {t.git(t.workflow, "rev-parse", "HEAD")} (workflow checkout)\nModel: opus\n\n## Checklist\n').encode() + checklist + b'\n## Scope notes\n' + notes
                label = f'{revision}-{kind}-{newline}'
                for suffix, data in [('checklist.bin', checklist), ('notes.bin', notes), ('record.bin', disk), ('stdout.bin', p.stdout), ('expected.bin', expected)]:
                    (out / (label + '-' + suffix)).write_bytes(data)
                row = dict(name=label, exit=p.returncode, checklist_preserved=checklist in disk,
                           notes_preserved=notes in disk, record_exact=disk == expected,
                           committed_exact=committed == disk, stdout_exact=p.stdout == disk if role else None,
                           sha256=hashlib.sha256(disk).hexdigest())
                assert row['committed_exact']
                if revision == 'candidate' or newline == 'lf':
                    assert row['record_exact'] and (not role or row['stdout_exact']), row
                else:
                    assert not row['checklist_preserved'] and not row['notes_preserved'], row
                records[(revision, kind, newline)] = disk
                rows.append(row)
            finally:
                t.doCleanups()
for kind in ['engineering-reviewer', 'ideation']:
    assert records[('previous', kind, 'lf')] == records[('candidate', kind, 'lf')], kind
(out / 'repair-bytes.json').write_text(json.dumps(rows, indent=2) + '\n')
print('PASS: previous CRLF failures reproduced; candidate role/stage raw bytes and LF differential pass', flush=True)

mutant = home / 'repair-mutant'
shutil.copytree(home / 'candidate', mutant)
script = mutant / 'kc-dev-flow-2/scripts/dispatch_stage.py'
original = script.read_text()
edits = [('checklist', 'args.checklist_file.read_bytes().decode("utf-8")', 'args.checklist_file.read_text()'),
         ('scope', 'args.scope_notes_file.read_bytes().decode("utf-8")', 'args.scope_notes_file.read_text()'),
         ('stdout', 'sys.stdout.buffer.write(path.read_bytes())', 'sys.stdout.write(path.read_text())')]
controls = []
for name in ['checklist', 'scope', 'stdout', 'all-three']:
    changed = original
    for tag, before, after in edits:
        if name in [tag, 'all-three']:
            assert changed.count(before) == 1
            changed = changed.replace(before, after)
    script.write_text(changed)
    cases = ['DispatchStageTests.test_role_crlf_inputs_keep_raw_bytes']
    if name != 'stdout':
        cases += ['DispatchStageTests.test_stage_crlf_inputs_keep_raw_bytes']
    log = out / ('repair-mutation-' + name + '.log')
    with log.open('w') as stream:
        p = subprocess.run([sys.executable, '-B', 'kc-dev-flow-2/scripts/test_dispatch_stage.py', *cases], cwd=mutant,
                           env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'), stdout=stream, stderr=subprocess.STDOUT)
    text = log.read_text()
    assert p.returncode == 1 and 'AssertionError' in text and 'ERROR:' not in text, text
    controls.append(dict(name=name, exit=p.returncode, caught=True, file=log.name))
    print('Caught byte mutation: ' + name, flush=True)
script.write_text(original)
(out / 'repair-mutations.json').write_text(json.dumps(controls, indent=2) + '\n')
