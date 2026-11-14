"""Count home hits in scripts (.sh/.py) added in a commit range, and how many would land inside quotes after rewrite_home. Counts only."""
import re, subprocess, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1]); import state_guard as g
root = Path(sys.argv[2]).resolve(); home = str(Path.home())
files = subprocess.run(['git', '-C', str(root), 'log', '--format=', '--name-only', '--diff-filter=A', sys.argv[3]], capture_output=True, text=True).stdout.split()
tot = quoted = scripts = 0
for f in sorted(set(x for x in files if x.endswith(('.sh', '.py')))):
    data = subprocess.run(['git', '-C', str(root), 'show', 'origin/spacedock-state/dev2:' + f], capture_output=True, text=True).stdout
    if home not in data: continue
    scripts += 1
    new = g.rewrite_home(data)
    for m in re.finditer(r'~(?=/|\b)', new):
        line = new[new.rfind('\n', 0, m.start()) + 1: m.start()]
        tot += 1
        if line.count('"') % 2 or line.count("'") % 2 or new[m.start() - 1:m.start()] in '"\'=':
            quoted += 1
print(f'scripts with home: {scripts}; tilde sites after rewrite: {tot}; inside quotes or after =: {quoted}')
