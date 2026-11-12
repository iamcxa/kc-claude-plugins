#!/usr/bin/env python3
"""Close a dispatch: retain cited evidence, then remove its derived scratch root."""

import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys

BASE = Path('/tmp').resolve() / 'dev2'
RECORD = re.compile(r'[a-z][a-z0-9_-]*-[1-9][0-9]*(?:-message-[1-9][0-9]*)?')


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], capture_output=True,
                          text=True, check=True).stdout.strip()


def repository(repo):
    url = git(repo, 'remote', 'get-url', 'origin').rstrip('/')
    name = re.split(r'[/\\:]', url)[-1].removesuffix('.git')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', name):
        raise ValueError('origin has no usable repository name')
    return name


def dispatch_name(record):
    if not RECORD.fullmatch(record):
        raise ValueError('invalid dispatch record name')
    return re.sub(r'-message-[1-9][0-9]*$', '', record)


def root_for(repo, slug, record):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', slug):
        raise ValueError('invalid task folder name')
    return BASE / repository(repo) / slug / dispatch_name(record)


def safe_path(path):
    if any(p.is_symlink() for p in (path, *path.parents)) or path.resolve() != path:
        raise ValueError(f'symlinked or non-derived path: {path}')


def notes_for(repo, folder, record, notes, package):
    root = root_for(repo, folder.name, record)
    safe_path(root)
    for raw in re.findall(r'(?<![\w/])/(?:private/)?tmp/[^\s`\'"<>()\[\]{};,]+', notes):
        path = Path(os.path.abspath(raw.rstrip('.')))
        if str(path).startswith('/tmp/'):
            path = Path('/tmp').resolve() / path.relative_to('/tmp')
        if not path.is_relative_to(root):
            raise ValueError(f'scope notes name a /tmp path outside {root}: {raw}')
    command = shlex.join(['python3', str(package / 'scripts/scratch.py'), 'close', str(folder), record])
    # see docs/adr/0079-dispatch-close-out-retains-public-evidence-and-removes-scratch.md
    return (notes + '\nScratch: ' + str(root).replace(str(BASE.parent), '/tmp', 1) + '\n'
            "Put every file or checkout you create outside the task worktree and the state checkout under that folder. "
            f"Copy what your report cites into evidence/{record}/ in the task folder, and nothing that holds a secret or "
            "a person's data: for that, write `Not archived (private): <what>; reproduce: <command>`. "
            f"Before your report, run `{command}` and paste the lines it prints.\n")


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
    sums = []
    for path in (p for p in paths if p.is_file()):
        name = path.relative_to(target).as_posix()
        compressed = name.endswith('.gz') and name[:-3] in previous and not path.with_suffix('').exists()
        data = gzip.decompress(path.read_bytes()) if compressed else path.read_bytes()
        original = name[:-3] if compressed else name
        digest = hashlib.sha256(data).hexdigest()
        if compressed and digest != previous[original]:
            raise ValueError(f'evidence digest differs: {path}')
        sums.append(f'{digest}  {original}\n')
        if not compressed and len(data) > 256 * 1024:
            destination = path.with_name(path.name + '.gz')
            if destination.exists():
                raise ValueError(f'evidence compression would overwrite {destination}')
            destination.write_bytes(gzip.compress(data, mtime=0))
            path.unlink()
    target.mkdir(parents=True, exist_ok=True)
    manifest.write_text(''.join(sums))
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
    root = root_for(folder, folder.name, name)
    safe_path(root)
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
