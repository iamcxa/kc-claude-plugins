"""Counterfactual: per home-hit file in a range, does writing ~ (main's rewrite_home) remove every hit? Counts by kind only."""
import collections, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1]); import state_guard as g
root = Path(sys.argv[2]).resolve()
compiled, _ = g.patterns(root); home = [rx for k, rx in compiled if k == 'home'][0]
KINDS = (('captain-steps', r'/captain-steps/'), ('message-record', r'/dispatch/[^/]+-message-\d+\.md$'), ('dispatch-record', r'/dispatch/'),
         ('evidence', r'/evidence/'), ('briefing', r'/review/.*/index\.json$'), ('task-file', r'^(_archive/)?[^/]+\.md$'))
kind = lambda n: next((k for k, rx in KINDS if re.search(rx, n)), 'other')
files, fixed = collections.Counter(), collections.Counter()
for c in subprocess.run(['git', '-C', str(root), 'rev-list', sys.argv[3]], capture_output=True, text=True).stdout.split():
    for name, before, after in g.changes(root, c):
        data = g.added_bytes(root, before, after)
        if not home.search(data): continue
        k = kind(name.decode(errors='replace')); files[k] += 1
        try: text = data.decode('utf-8')
        except UnicodeError: continue
        if not home.search(g.rewrite_home(text).encode()): fixed[k] += 1
for k in sorted(files): print(f'{k}: {files[k]} file changes with home; {fixed[k]} clean after writing ~; residual {files[k]-fixed[k]}')
