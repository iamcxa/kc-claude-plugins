from pathlib import Path
import subprocess, tarfile, io, json, re
out = Path('/tmp/budget-validation-841/evidence')
pins = {'dev2': ('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state', 'e5efef4e'), 'qnow': ('/Users/kent/conductor/repos/qnow-adopt-dev2/docs/dev2/.spacedock-state', 'd80c162d0c525e4b3400861fdd30e6fc5b3d040d'), 'relay': ('/Users/kent/conductor/workspaces/subspace-relay/beirut-dev2/docs/dev2/.spacedock-state', '13ef35675e1a1150fe480e71a0e747a7b37cfa87'), 'web': ('/Users/kent/conductor/workspaces/subspace-web/dev2-fo/docs/dev2/.spacedock-state', 'faf28a257b22f92b4036cff8518a80ff10cd0fd2')}
for name, (repo, sha) in list(pins.items()):
    full = subprocess.check_output(['git', '-C', repo, 'rev-parse', sha + '^{commit}'], text=True).strip()
    pins[name] = [repo, full]
    dest = out / 'corpus-md' / name
    dest.mkdir(parents=True, exist_ok=True)
    listing = subprocess.check_output(['git', '-C', repo, 'ls-tree', '-r', '--name-only', full], text=True).splitlines()
    paths = [p for p in listing if re.fullmatch(r'(?:_archive/)?(?:[^/]+\.md|[^/]+/index\.md|[^/]+/dispatch/[^/]+\.md)', p)]
    data = subprocess.check_output(['git', '--literal-pathspecs', '-C', repo, 'archive', full, '--', *paths])
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        for item in archive:
            if item.isfile() and item.name in paths:
                target = dest / item.name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.extractfile(item).read())
    print(name, full, len(paths), flush=True)
(out / 'pins.json').write_text(json.dumps(pins, indent=2) + '\n')
wt = '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-budget-overrun-holds-and-findings-meet-non-goals'
base = subprocess.check_output(['git', '-C', wt, 'show', 'e8664a72b0f904e5dda3c391d52ab3abaca876b4:kc-dev-flow-2/scripts/role_triggers.py'], text=True)
(out / 'base_role_triggers.py').write_text(base)
