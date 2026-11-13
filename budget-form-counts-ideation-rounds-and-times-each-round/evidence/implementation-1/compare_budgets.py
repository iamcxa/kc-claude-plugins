"""compare_budgets.py <base scripts> <candidate scripts> <state>; compare committed tasks."""
from pathlib import Path
import subprocess, sys
base, candidate, state = map(Path, sys.argv[1:])
files = list(state.glob('*.md')) + list(state.glob('*/index.md')) + list((state/'_archive').glob('*.md')) + list((state/'_archive').glob('*/index.md'))
changed, exits, count = [], [], 0
for path in sorted(files):
    text=path.read_text()
    if not text.startswith('---\n') or '\ntitle:' not in text: continue
    slug=path.parent.name if path.name=='index.md' else path.stem
    runs=[subprocess.run([sys.executable,'-B',str(p/'role_triggers.py'),str(state),slug],capture_output=True,text=True) for p in (base,candidate)]
    count+=1
    if runs[0].returncode!=runs[1].returncode: exits.append((slug,runs[0].returncode,runs[1].returncode))
    if runs[0].stdout!=runs[1].stdout: changed.append(slug)
print(f'tasks compared {count}; text changes {len(changed)}; exit changes {len(exits)}')
print('text changed tasks: '+', '.join(changed))
print('exit changes: '+repr(exits))
assert not exits, exits
