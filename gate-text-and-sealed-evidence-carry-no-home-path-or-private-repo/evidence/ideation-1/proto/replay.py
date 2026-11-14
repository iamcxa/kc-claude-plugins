"""Replay state commits through state_guard's classes; print counts and path kinds only, never matched text.
usage: replay.py GUARD_DIR STATE_CHECKOUT REV_RANGE [--detail]"""
import collections, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import state_guard as g
root = Path(sys.argv[2]).resolve()
commits = subprocess.run(['git', '-C', str(root), 'rev-list', '--reverse', sys.argv[3]], capture_output=True, text=True, check=True).stdout.split()
compiled, present = g.patterns(root)
assert present, 'identifier list absent'
def kind_of(name):
    n = name.decode(errors='replace')
    for label, rx in (('captain-steps', r'/captain-steps/'), ('message-record', r'/dispatch/[^/]+-message-\d+\.md$'),
                      ('dispatch-record', r'/dispatch/'), ('evidence', r'/evidence/'), ('briefing', r'/review/.*/index\.json$'),
                      ('review-other', r'/review/'), ('merge-record', r'/merge/'), ('task-file', r'^(_archive/)?[^/]+\.md$')):
        if re.search(label and rx, n):
            return label
    return 'other'
commit_hits = collections.Counter(); where = collections.Counter(); per = []
for c in commits:
    classes = set(); kinds = collections.defaultdict(set)
    for name, before, after in g.changes(root, c):
        data = g.added_bytes(root, before, after)
        for k, rx in compiled:
            if rx.search(data) or rx.search(name):
                classes.add(k); kinds[k].add(kind_of(name))
    subj = subprocess.run(['git', '-C', str(root), 'log', '-1', '--format=%s', c], capture_output=True, text=True).stdout.strip()
    subj_kind = subj.split(':', 1)[0] if ':' in subj else 'other'
    for k in classes:
        commit_hits[k] += 1
        for w in kinds[k]:
            where[(k, w)] += 1
    per.append((c[:12], subj_kind, {k: sorted(kinds[k]) for k in sorted(classes)}))
print(f'commits: {len(commits)} range {commits[0][:12]}..{commits[-1][:12]}')
for k in g.CLASSES:
    print(f'{k}: {commit_hits[k]} commits; ' + ', '.join(f'{w} {n}' for (kk, w), n in sorted(where.items()) if kk == k))
if '--detail' in sys.argv:
    for c, s, d in per:
        if d: print(c, s, d)
