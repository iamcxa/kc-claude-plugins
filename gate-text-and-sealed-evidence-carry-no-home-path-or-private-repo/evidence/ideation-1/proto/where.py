"""For given commits, print each hit file (class-redacted) and, for markdown, the heading above each hit line. No matched text."""
import re, subprocess, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1]); import state_guard as g
root = Path(sys.argv[2]).resolve(); compiled, _ = g.patterns(root)
for c in sys.argv[3:]:
    for name, before, after in g.changes(root, c):
        data = g.added_bytes(root, before, after)
        ks = sorted({k for k, rx in compiled if rx.search(data) or rx.search(name)})
        if not ks: continue
        heads = set()
        if name.endswith(b'.md'):
            full = g.git(root, 'cat-file', 'blob', after.decode()).decode(errors='replace').splitlines()
            h = '(top)'; added = set(data.decode(errors='replace').splitlines())
            for line in full:
                if line.startswith('#'): h = line[:60]
                if line in added and any(rx.search(line.encode()) for _, rx in compiled):
                    lab = re.match(r'^(\w[\w -]{0,20}):', line); heads.add(h + (' / ' + lab[1] if lab else ''))
        print(c[:9], g.safe_name(name, compiled)[-70:], ks, sorted(heads)[:4])
