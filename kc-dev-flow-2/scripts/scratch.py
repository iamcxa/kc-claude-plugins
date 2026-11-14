#!/usr/bin/env python3
"""Close a dispatch: retain cited evidence, then remove its derived scratch root."""

import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys

from state_guard import rewrite_home

BASE = Path('/tmp').resolve() / 'dev2'
RECORD = re.compile(r'[a-z][a-z0-9_-]*-[1-9][0-9]*(?:-message-[1-9][0-9]*)?')


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], capture_output=True,
                          text=True, check=True).stdout.strip()


def identity(repo, state):
    url = git(repo, 'remote', 'get-url', 'origin').rstrip('/')
    name = re.split(r'[/\\:]', url)[-1].removesuffix('.git')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', name):
        raise ValueError('origin has no usable repository name')
    common = Path(git(repo, 'rev-parse', '--git-common-dir'))
    common = (common if common.is_absolute() else Path(repo) / common).resolve()
    digest = hashlib.sha256(json.dumps([url, str(common), str(state.resolve())]).encode()).hexdigest()
    return name, digest


def repository(repo, state):
    name, digest = identity(repo, state)
    return name + '-' + digest[:16]


def state_of(folder):
    return folder.parent.parent if folder.parent.name == '_archive' else folder.parent


def dispatch_name(record):
    if not RECORD.fullmatch(record):
        raise ValueError('invalid dispatch record name')
    return re.sub(r'-message-[1-9][0-9]*$', '', record)


def root_for(repo, folder, record):
    folder = Path(folder)
    slug = folder.name
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', slug):
        raise ValueError('invalid task folder name')
    return BASE / repository(repo, state_of(folder)) / slug / dispatch_name(record)


def owner_for(repo, folder, record):
    return dict(repository=identity(repo, state_of(folder))[1], task=folder.name, record=dispatch_name(record))


def check_owner(root, owner):
    marker = root / '.owner.json'
    safe_path(root)
    safe_path(marker)
    if not root.is_dir() or not marker.is_file() or json.loads(marker.read_text()) != owner:
        raise ValueError(f'scratch ownership missing or differs: {root}')


def claim_root(repo, folder, record):
    root = root_for(repo, folder, record)
    safe_path(root)
    owner = owner_for(repo, folder, record)
    try:
        root.mkdir(parents=True)
    except FileExistsError:
        check_owner(root, owner)
    else:
        with (root / '.owner.json').open('x') as output:
            json.dump(owner, output, sort_keys=True)
    return root


def safe_path(path):
    if any(p.is_symlink() for p in (path, *path.parents)) or path.resolve() != path:
        raise ValueError(f'symlinked or non-derived path: {path}')


def notes_for(repo, folder, record, notes, package):
    root = root_for(repo, folder, record)
    safe_path(root)
    if root.exists():
        check_owner(root, owner_for(repo, folder, record))
    for raw in re.findall(r'(?<![\w/])/(?:private/)?tmp/[^\s`\'"<>()\[\]{};,]+', notes):
        path = Path(os.path.abspath(raw.rstrip('.')))
        if str(path).startswith('/tmp/'):
            path = Path('/tmp').resolve() / path.relative_to('/tmp')
        if not path.is_relative_to(root):
            raise ValueError(f'scope notes name a /tmp path outside {root}: {raw}')
    command = shlex.join(['python3', str(package / 'scripts/scratch.py'), 'close', str(folder), record])
    # see docs/adr/0079-dispatch-close-out-retains-public-evidence-and-removes-scratch.md
    return (notes + '\nScratch: ' + str(root).replace(str(BASE.parent), '/tmp', 1) + '\n'
            "Put files and checkouts outside the task worktree or state checkout under that folder. "
            f"Copy cited evidence into evidence/{record}/ in the task folder. "
            "Never archive private repository evidence, secrets or personal data; instead write "
            "`Not archived (private): <what>; reproduce: <command>`. "
            f"Before reporting, run `{command}` and paste its output.\n")


def evidence(folder, record):
    # see docs/adr/0079-dispatch-close-out-retains-public-evidence-and-removes-scratch.md
    target = folder / 'evidence' / record
    safe_path(target)
    paths = sorted(p for p in target.rglob('*') if p.name != 'SHA256SUMS') if target.exists() else []
    for path in paths:
        safe_path(path)
        if not path.is_file() and not path.is_dir():
            raise ValueError(f'unsupported evidence type: {path}')
    manifest = target / 'SHA256SUMS'
    safe_path(manifest)
    previous = dict(line.split('  ', 1)[::-1] for line in manifest.read_text().splitlines()) if manifest.exists() else {}
    sums, compress, rewrites = [], [], {}
    for path in (p for p in paths if p.is_file()):
        name = path.relative_to(target).as_posix()
        compressed = name.endswith('.gz') and name[:-3] in previous and not path.with_suffix('').exists()
        data = gzip.decompress(path.read_bytes()) if compressed else path.read_bytes()
        original = name[:-3] if compressed else name
        digest = hashlib.sha256(data).hexdigest()
        if compressed and digest != previous[original]:
            raise ValueError(f'evidence digest differs: {path}')
        # see docs/adr/0087-public-state-writes-and-an-opt-in-git-guard.md
        if not compressed and digest != previous.get(original):
            packed = data.startswith(b'\x1f\x8b')
            content = gzip.decompress(data) if packed else data
            try:
                text = content.decode('utf-8') if b'\0' not in content else None
            except UnicodeError:
                text = None
            if text is not None and (rewritten := rewrite_home(text).encode('utf-8')) != content:
                data = gzip.compress(rewritten, mtime=0) if packed else rewritten
                rewrites[path] = data
                digest = hashlib.sha256(data).hexdigest()
        sums.append(f'{digest}  {original}\n')
        if not compressed and len(data) > 256 * 1024:
            destination = path.with_name(path.name + '.gz')
            if destination.exists():
                raise ValueError(f'evidence compression would overwrite {destination}')
            compress.append(path)
    target.mkdir(parents=True, exist_ok=True)
    for path, data in rewrites.items():
        path.write_bytes(data)
    manifest.write_text(''.join(sums))
    for path in compress:
        destination = path.with_name(path.name + '.gz')
        with destination.open('xb') as output:
            output.write(gzip.compress(path.read_bytes(), mtime=0))
        path.unlink()
    size = sum(p.stat().st_size for p in target.rglob('*') if p.is_file())
    if size > 1024 * 1024:
        raise ValueError('evidence exceeds 1 MiB after compression; trim or record a reproduce command')
    return f'Evidence: evidence/{record}/ ({len(sums)} files, {size / 1024:.1f} KiB)'


def close(folder, record):
    folder = Path(os.path.abspath(folder))
    safe_path(folder)
    name = dispatch_name(record)
    source = folder / 'dispatch' / (record + '.md')
    safe_path(source)
    if not source.is_file():
        raise ValueError(f'dispatch record missing: {source}')
    root = root_for(folder, folder, name)
    safe_path(root)
    if root.exists():
        check_owner(root, owner_for(folder, folder, name))
    stated = re.findall(r'^Scratch: (.+)$', source.read_text(), re.M)
    if stated and (len(stated) != 1 or Path(stated[0]).resolve() != root):
        raise ValueError('record scratch root differs from the derived path')
    log = folder / 'scratch-removed.txt'
    safe_path(log)
    if log.exists() and not log.is_file():
        raise ValueError(f'unsupported removal log: {log}')
    retained = evidence(folder, name)
    if not root.exists():
        print(f'Scratch removed: {root} (absent)\n{retained}')
        return
    size = sum(p.lstat().st_size for p in root.rglob('*') if not p.is_symlink() and p.is_file())
    removed = []
    listing = subprocess.run(['git', '-C', str(folder), 'worktree', 'list', '--porcelain', '-z'],
                             capture_output=True, text=True, check=True).stdout
    worktrees = [Path(s[9:]) for s in listing.split('\0') if s.startswith('worktree ')]
    for path in sorted(worktrees, key=lambda p: len(p.parts), reverse=True):
        if path.is_relative_to(root):
            safe_path(path)
            changed = git(path, 'ls-files', '-z', '--modified', '--deleted', '--others', '--exclude-standard')
            staged = git(path, 'diff', '--cached', '--name-only', '-z')
            count = len(set(filter(None, (changed + '\0' + staged).split('\0'))))
            # see docs/adr/0079-dispatch-close-out-retains-public-evidence-and-removes-scratch.md
            git(folder, 'worktree', 'remove', '--force', str(path))
            removed.append(f'worktree={path} uncommitted-files={count}')
    git(folder, 'worktree', 'prune')
    if root.exists():
        shutil.rmtree(root)
    if not any(root.parent.iterdir()):
        root.parent.rmdir()
    with log.open('a') as output:
        output.write(f'{name} {root} {size} {datetime.now(timezone.utc).isoformat()} ' + '; '.join(removed) + '\n')
    print(f'Scratch removed: {root} ({size} bytes)\n{retained}')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['close'])
    parser.add_argument('task_folder', type=Path)
    parser.add_argument('record')
    args = parser.parse_args(argv)
    try:
        close(args.task_folder, args.record)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f'scratch: refused; {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
