"""Count-only scan and replay of a bounded public state window on a disposable copy."""
import collections
import gzip
import json
import os
from pathlib import Path
import subprocess
import sys

code, live, base, output = map(Path, sys.argv[1:5])
start, end = sys.argv[5:7]
base.mkdir(parents=True)
sys.path.insert(0, str(code / 'kc-dev-flow-2/scripts'))
import state_guard as guard

def run(args, data=None, expected=0):
    p = subprocess.run(list(map(str, args)), input=data, text=True, capture_output=True)
    assert p.returncode == expected, 'replay setup or scan failed'
    return p.stdout

remote, product, state = [base / n for n in ('remote.git', 'product', 'state')]
run(['git', 'clone', '--quiet', '--bare', live, remote])
run(['git', 'clone', '--quiet', '--no-checkout', remote, product])
run(['git', '-C', product, 'worktree', 'add', '-b', 'spacedock-state/replay', state, end])
run([sys.executable, '-B', code / 'kc-dev-flow-2/scripts/state_guard.py', 'install', state,
     '--shared', '--refuse', 'home,private-repo'])
compiled, present = guard.patterns(state)
assert present
raw_only, gz_count, header_count = collections.Counter(), 0, 0
for entry in guard.git(state, 'ls-tree', '-r', '-z', end).split(b'\0'):
    if not entry.endswith(b'.gz'):
        continue
    blob = entry.split(b'\t')[0].split()[2].decode()
    raw = guard.git(state, 'cat-file', 'blob', blob)
    plain = gzip.decompress(raw)
    gz_count += 1
    header_count += bool(raw[3] & 0x18)
    for kind, expression in compiled:
        if expression.search(raw) and not expression.search(plain):
            raw_only[kind] += 1
assert not raw_only
commits = guard.git(state, 'rev-list', '--reverse', start + '..' + end).decode().splitlines()
counts, per_commit = collections.Counter(), []
for commit in commits:
    classes, routes = set(), set()
    for name, before, after in guard.changes(state, commit):
        data = guard.added_bytes(state, before, after)
        for kind, expression in compiled:
            if expression.search(data) or expression.search(name):
                classes.add(kind)
                if kind == 'home':
                    try:
                        clean = guard.rewrite_home(data.decode()).encode()
                    except UnicodeError:
                        routes.add('drop private binary evidence and record reproduction')
                    else:
                        assert not expression.search(clean), 'home hit needs another way forward'
                        routes.add('write home as ~')
                elif kind == 'private-repo':
                    routes.add('drop sealed private evidence or replace a textual name with a placeholder')
    counts.update(classes)
    parent = guard.git(state, 'rev-parse', commit + '^').decode().strip()
    payload = 'refs/heads/spacedock-state/replay ' + commit + ' refs/heads/spacedock-state/replay ' + parent + '\n'
    result = subprocess.run([sys.executable, '-B', str(code / 'kc-dev-flow-2/scripts/state_guard.py'),
                             'scan', str(state), '--event', 'pre-push'], input=payload, text=True, capture_output=True)
    expected = int(bool(classes & {'home', 'private-repo'}))
    assert result.returncode == expected
    per_commit.append(dict(commit=commit, guard_exit=result.returncode, classes=sorted(classes), way_forward=sorted(routes)))
summary = dict(start_exclusive=start, end_inclusive=end, commit_count=len(commits), counts_by_class=dict(counts),
               no_way_forward=0, gzip_blobs=gz_count, named_or_commented_headers=header_count,
               raw_only_class_hits=dict(raw_only), commits=per_commit,
               limit='Only this bounded post-candidate public state window; no future dispatch or live rollout claim.')
(output / 'replay.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
