import ast, hashlib, json, subprocess
from pathlib import Path

home = Path(__file__).resolve().parent
out = home / 'evidence'
root = home / 'candidate'
repo = '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-special-role-dispatch-records-built-by-script'
base = 'd8dbfcb1051d7c696aca139ed9ade332ee85abaf'
head = '39a76c68836f471fc0c42c18eab12641196860ed'
prior = '8574e879b85197d31239ee2d9a9af0c5d0cb5392'
def git(*args):
    return subprocess.check_output(['git', '-C', repo, *args])

path = 'kc-dev-flow-2/scripts/dispatch_stage.py'
expected = git('show', prior + ':' + path).decode()
for before, after in [('args.checklist_file.read_text()', 'args.checklist_file.read_bytes().decode("utf-8")'),
                      ('args.scope_notes_file.read_text()', 'args.scope_notes_file.read_bytes().decode("utf-8")'),
                      ('sys.stdout.write(path.read_text())', 'sys.stdout.buffer.write(path.read_bytes())')]:
    assert expected.count(before) == 1
    expected = expected.replace(before, after)
assert expected.encode() == (root / path).read_bytes()
repaired = '3567082b0ec1eeb59346b2d82887a07bc5ffc2fb'
changed = git('diff', '--name-only', prior, repaired).decode().splitlines()
assert changed == ['kc-dev-flow-2/scripts/dispatch_stage.py', 'kc-dev-flow-2/scripts/test_dispatch_stage.py']
hashes = {}
for path in git('diff', '--name-only', base, head).decode().splitlines():
    data = (root / path).read_bytes()
    assert data == git('show', head + ':' + path), path
    hashes[path] = hashlib.sha256(data).hexdigest()
(out / 'source-integrity.json').write_text(json.dumps(dict(head=head, base=base, prior=prior, repair_files=changed, exact_three_substitutions=True, sha256=hashes), indent=2) + '\n')

words = out / 'words'
words.mkdir(exist_ok=True)
captures = []
for row in map(json.loads, (out / 'stage-calls.jsonl').read_text().splitlines()):
    if '--role' not in row['argv'] or 'dispatch_stage.py' not in ' '.join(row['argv']):
        continue
    counts = {}
    for stream in ['stdout', 'stderr']:
        path = words / f'role-{len(captures)+1}-{stream}.txt'
        path.write_text(row[stream])
        counts[stream] = int(subprocess.check_output(['wc', '-w', str(path)]).split()[0])
    captures.append(dict(exit=row['exit'], **counts))
files = [out / 'workflow-base.md', root / 'kc-dev-flow-2/references/sd/workflow.md', *sorted(words.glob('*.txt'))]
(out / 'wc-words.log').write_bytes(subprocess.check_output(['wc', '-w', *map(str, files)]))
(out / 'words.json').write_text(json.dumps(dict(startup_base=int(subprocess.check_output(['wc','-w',str(files[0])]).split()[0]), startup_candidate=int(subprocess.check_output(['wc','-w',str(files[1])]).split()[0]), captures=captures), indent=2) + '\n')
print('PASS: exact repair scope, source integrity and captured lifecycle word counts')
