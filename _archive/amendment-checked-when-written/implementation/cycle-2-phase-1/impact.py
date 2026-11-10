import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

from proposal import load_proposal, proposed_source

wt, out, inputs = Path(sys.argv[1]).resolve(), Path(__file__).resolve().parent, Path(sys.argv[2]).resolve()
head = 'd7502656c765e36ce3d24be8602862ccc2551254'
assert subprocess.check_output(['git', '-C', str(wt), 'rev-parse', 'HEAD'], text=True).strip() == head
sys.path.insert(0, str(wt / 'kc-dev-flow-2/scripts'))
import laws_check as lc
import design_surfaces as ds

proposed = load_proposal(wt)
before_source, after_source = proposed_source(wt)
repos = {row['name']: row for row in json.loads(inputs.read_text())}
rows = []
for name, repo in repos.items():
    state = repo['state']
    command = ['git', '-C', state, 'log', '--no-merges', '--format=', '--raw', '--no-abbrev', '--no-renames',
               '-z', repo['before'] + '..' + repo['after'], '--', '*.md']
    records = subprocess.check_output(command).split(b'\0')
    blobs = set()
    index = 0
    while index < len(records):
        meta = records[index].lstrip(b'\n')
        index += 1
        if not meta:
            continue
        assert meta.startswith(b':'), meta
        path = records[index].decode('utf-8')
        index += 1
        if lc.amendment_slug(path) is None:
            continue
        for sha in meta.split()[2:4]:
            if sha != b'0' * 40:
                blobs.add(sha)
    ordered = sorted(blobs)
    stream = subprocess.run(['git', '-C', state, 'cat-file', '--batch'], input=b'\n'.join(ordered) + b'\n',
                            capture_output=True, check=True).stdout
    offset, differences, tildes, unreadable = 0, [], [], []
    for sha in ordered:
        end = stream.index(b'\n', offset)
        fields = stream[offset:end].split()
        assert fields[:2] == [sha, b'blob'], fields
        size = int(fields[2])
        blob = stream[end + 1:end + 1 + size]
        offset = end + size + 2
        try:
            text = blob.decode('utf-8')
        except UnicodeError:
            unreadable.append(sha.decode())
            continue
        lines = text.split('\n')
        if any((m := ds.AMENDMENT_FENCE.match(line)) and m[1][0] == '~' for line in lines):
            tildes.append(sha.decode())
        old, new = ds.move_defects(lines), proposed.move_defects(lines)
        if old != new:
            differences.append({'blob': sha.decode(), 'candidate': old, 'proposal': new})
    assert offset == len(stream)
    row = {**repo, 'candidate': head, 'unique_old_new_task_blobs': len(ordered),
           'tilde_fence_blobs': tildes, 'unreadable_blobs': unreadable,
           'changed_defect_verdicts': differences, 'git_log_argv': command}
    rows.append(row)
    (out / 'corpus-helper-comparison.json').write_text(json.dumps(rows, indent=2) + '\n')
    print(f'{name}: {len(ordered)} task blobs; {len(differences)} changed move-defect results; {len(tildes)} tilde-fenced blobs', flush=True)
assert all(not r['changed_defect_verdicts'] and not r['unreadable_blobs'] for r in rows)

events = []
for name, short in [('dev2', 'a113aa3e9'), ('dev2', '7326e2a11'), ('dev2', 'bf8c73be9'),
                    ('qnow', '3a384063e'), ('qnow', '4ad692922'), ('qnow', '4993b5b60'), ('relay', '06cadae76')]:
    repo = repos[name]
    before, after = lc.commit_of(repo['state'], short + '^'), lc.commit_of(repo['state'], short)
    ctx = lc.Context(repo['state'], before[:12] + '..' + after[:12], lc.walk(repo['state'], before, after), repo['readme'])
    old = lc.judge(ctx, 'L4', lc.LAWS['L4'])
    with patch.object(ds, 'move_defects', proposed.move_defects):
        new = lc.judge(ctx, 'L4', lc.LAWS['L4'])
    assert old == new and old[0] == 1, (name, short, old, new)
    events.append({'repository': name, 'before': before, 'after': after,
                   'candidate_result': old, 'unapplied_proposal_result': new, 'unchanged': True})
(out / 'seven-events.json').write_text(json.dumps(events, indent=2) + '\n')
(out / 'seven-events.log').write_text('\n\n'.join(r['repository'] + '\n' + '\n'.join(r['candidate_result'][1] + r['candidate_result'][2]) for r in events) + '\n')

callers = []
for path in (wt / 'kc-dev-flow-2').rglob('*.py'):
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'move_defects':
            callers.append({'file': str(path.relative_to(wt)), 'line': node.lineno})
assert len(callers) == 2 and all(r['file'] == 'kc-dev-flow-2/scripts/laws_check.py' for r in callers), callers
unchanged = [node.name for node in ast.parse(before_source).body if isinstance(node, ast.FunctionDef) and node.name != 'move_defects']
(out / 'source-boundary.json').write_text(json.dumps({'candidate': head,
    'changed_function_only': 'design_surfaces.move_defects', 'unchanged_functions': unchanged,
    'package_direct_callers': callers, 'shared_unfenced_unchanged': True,
    'shared_unmarked_unchanged': True, 'parse_amendments_unchanged': True,
    'candidate_source_sha256': hashlib.sha256(before_source.encode()).hexdigest(),
    'unapplied_proposal_source_sha256': hashlib.sha256(after_source.encode()).hexdigest(),
    'full_history_CLI_replayed_with_proposal': False}, indent=2) + '\n')
assert subprocess.check_output(['git', '-C', str(wt), 'rev-parse', 'HEAD'], text=True).strip() == head
assert not subprocess.check_output(['git', '-C', str(wt), 'status', '--porcelain'], text=True)
print('Seven first-parent L4 event outputs unchanged; all scanned task-blob defect verdicts unchanged; shared check functions unchanged. This is analysis of an unapplied proposal, not fixed-candidate validation.')
