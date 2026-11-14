#!/usr/bin/env python3
"""Opt-in git guards for public state writes. Nothing is installed on import.

install CHECKOUT [--shared] [--refuse CLASSES] [--warn CLASSES]
check CHECKOUT reports missing, stale or partial protection.
scan CHECKOUT --event pre-commit|pre-push is the installed hooks' entry.
KC_DEV2_IDENTIFIERS overrides the out-of-repository identifiers.tsv list;
each line is class<TAB>literal or class<TAB>re:pattern. All classes default to warn.
"""

import argparse
import gzip
import json
import os
from pathlib import Path
import re
import subprocess
import sys

CLASSES = ('home', 'email', 'private-repo', 'private-slug', 'tailnet-host')
MARKER = '# kc-dev-flow-2 state guard\n'


def rewrite_home(text):
    # see docs/adr/0087-public-state-writes-and-an-opt-in-git-guard.md
    home = str(Path.home())
    if home == '/':
        return text
    pattern = r'(?<![\w./~\\-])' + re.escape(home) + r'(?=/|$|[\s`\'"<>()\[\]{}:;,])'
    return re.sub(pattern, '~', text)


def git(root, *args, data=None, optional=False):
    done = subprocess.run(['git', '-C', str(root), *args], input=data, capture_output=True)
    if done.returncode and not optional:
        raise ValueError('git cannot read guard input')
    return done.stdout.rstrip(b'\n') if optional else done.stdout


def branch(root):
    return git(root, 'symbolic-ref', '--quiet', '--short', 'HEAD', optional=True).decode()


def git_path(root, flag):
    path = Path(os.fsdecode(git(root, 'rev-parse', flag).rstrip(b'\n')))
    return (path if path.is_absolute() else root / path).resolve()


def identifier_path():
    config = Path(os.environ.get('XDG_CONFIG_HOME') or Path.home() / '.config')
    return Path(os.environ.get('KC_DEV2_IDENTIFIERS') or config / 'kc-dev-flow-2/identifiers.tsv').expanduser().resolve()


def patterns(root):
    values = [('home', str(Path.home()))]
    email = git(root, 'config', 'user.email', optional=True).decode()
    if email:
        values.append(('email', email))
    source = identifier_path()
    if source.exists():
        for number, line in enumerate(source.read_text().splitlines(), 1):
            if not line or line.startswith('#'):
                continue
            kind, separator, value = line.partition('\t')
            if not separator or kind not in CLASSES[2:] or not value:
                raise ValueError(f'identifier list line {number} has an invalid class or value')
            values.append((kind, value))
    compiled = []
    for kind, value in values:
        expression = value[3:] if kind in CLASSES[2:] and value.startswith('re:') else re.escape(value)
        try:
            compiled.append((kind, re.compile(expression.encode(), re.I)))
        except re.error:
            raise ValueError('identifier list has an invalid pattern') from None
    return compiled, source.is_file()


def outside_repository(path):
    parent = path.parent
    while not parent.exists():
        parent = parent.parent
    return not any(git(parent, 'rev-parse', flag, optional=True) == b'true'
                   for flag in ('--is-inside-work-tree', '--is-inside-git-dir'))


def modes_for(args):
    modes = dict.fromkeys(CLASSES, 'warn')
    for mode in ('refuse', 'warn'):
        for kind in filter(None, getattr(args, mode, '').split(',')):
            if kind not in CLASSES:
                raise ValueError('unknown identifier class; use ' + ','.join(CLASSES))
            modes[kind] = mode
    return modes


def hook_text(root, script, event, shared):
    return (f'#!{sys.executable}\n' + MARKER +
            'import subprocess, sys\nfrom pathlib import Path\n' +
            f'root = {str(root)!r}\nscript = {str(script)!r}\nshared = {str(shared)!r}\n' +
            f"data = sys.stdin.buffer.read() if {event!r} == 'pre-push' else None\n" +
            'if Path(shared).is_file() and Path(shared).stat().st_mode & 0o111:\n' +
            '    previous = subprocess.run([shared, *sys.argv[1:]], input=data)\n' +
            '    if previous.returncode:\n        sys.exit(previous.returncode)\n' +
            "branch = subprocess.run(['git', '-C', root, 'symbolic-ref', '--quiet', '--short', 'HEAD'], capture_output=True).stdout\n" +
            "if not branch.startswith(b'spacedock-state/'):\n    sys.exit(0)\n" +
            f"sys.exit(subprocess.run([sys.executable, '-B', script, 'scan', root, '--event', {event!r}], input=data).returncode)\n")


def install(args):
    # see docs/adr/0087-public-state-writes-and-an-opt-in-git-guard.md
    root = args.checkout
    own, common = git_path(root, '--git-dir'), git_path(root, '--git-common-dir')
    if own == common or not branch(root).startswith('spacedock-state/'):
        raise ValueError('install needs a linked worktree on spacedock-state/*')
    if not outside_repository(identifier_path()):
        raise ValueError('identifier list must be outside every git repository')
    patterns(root)
    if not args.shared and git(root, 'config', '--bool', 'extensions.worktreeConfig', optional=True) != b'true':
        raise ValueError('extensions.worktreeConfig is off; ask the clone owner to enable it '
                         '(move core.bare/core.worktree to the main config.worktree when set), '
                         'or use install --shared for branch-scoped shared hooks')
    hooks = common / 'hooks' if args.shared else own / 'state-guard'
    current = git(root, 'config', '--path', 'core.hooksPath', optional=True)
    if current and (root / os.fsdecode(current)).resolve() not in (hooks, common / 'hooks'):
        raise ValueError('existing core.hooksPath differs; ask its owner before replacing it')
    config = modes_for(args)
    folder = hooks / 'state-guard' if args.shared else hooks
    folder.mkdir(parents=True, exist_ok=True)
    script = folder / 'state_guard.py'
    script.write_bytes(Path(__file__).read_bytes())
    (folder / 'modes.json').write_text(json.dumps(config, sort_keys=True) + '\n')
    for event in ('pre-commit', 'pre-push'):
        hook = hooks / event
        shared = common / 'hooks' / event
        if args.shared:
            shared = hooks / (event + '.before-state-guard')
            if hook.exists() and MARKER not in hook.read_text(errors='replace'):
                if shared.exists():
                    raise ValueError('saved shared hook already exists; ask its owner')
                hook.rename(shared)
        hook.write_text(hook_text(root if not args.shared else Path('.'), script, event, shared))
        hook.chmod(0o755)
    if not args.shared:
        git(root, 'config', '--worktree', 'core.hooksPath', str(hooks))
    print('state guard: installed (' + ', '.join(f'{k}={v}' for k, v in config.items()) + ')')


def installed(root):
    value = git(root, 'config', '--path', 'core.hooksPath', optional=True)
    hooks = Path(os.fsdecode(value)) if value else git_path(root, '--git-common-dir') / 'hooks'
    if not hooks.is_absolute():
        hooks = root / hooks
    folder = hooks if (hooks / 'state_guard.py').is_file() else hooks / 'state-guard'
    return hooks.resolve(), folder.resolve()


def read_modes(folder):
    modes = json.loads((folder / 'modes.json').read_text())
    if set(modes) != set(CLASSES) or any(value not in ('warn', 'refuse') for value in modes.values()):
        raise ValueError('installed modes are invalid')
    return modes


def check(root):
    hooks, folder = installed(root)
    for event in ('pre-commit', 'pre-push'):
        hook = hooks / event
        if not hook.is_file() or not os.access(hook, os.X_OK):
            return 1, f'state guard: unguarded: {event} missing'
        shared = git_path(root, '--git-common-dir') / 'hooks' / event
        if hooks == shared.parent:
            shared = hooks / (event + '.before-state-guard')
        expected = hook_text(root if hooks != shared.parent else Path('.'), folder / 'state_guard.py', event, shared)
        if hook.read_text() != expected:
            return 1, 'state guard: stale: installed hook differs from this package'
    if not (folder / 'state_guard.py').is_file() or (folder / 'state_guard.py').read_bytes() != Path(__file__).read_bytes():
        return 1, 'state guard: stale: installed copy differs from this package'
    try:
        modes = read_modes(folder)
    except (OSError, ValueError):
        return 1, 'state guard: stale: installed modes missing or invalid'
    _, present = patterns(root)
    if not present:
        return 1, 'state guard: partial: identifier list absent'
    return 0, 'state guard: guarded (' + ', '.join(f'{k}={v}' for k, v in modes.items()) + ')'


def changes(root, commit=None):
    if commit:
        parents = git(root, 'rev-list', '--parents', '-n', '1', commit).split()
        command = ['diff-tree', '--no-commit-id', '-r', '--root']
        revisions = [parents[1].decode(), commit] if len(parents) > 1 else [commit]
    else:
        command, revisions = ['diff', '--cached'], []
    raw = git(root, *command, '--raw', '-z', '--no-abbrev', '-M', *revisions).split(b'\0')
    entries, index = [], 0
    while index < len(raw) and raw[index]:
        metadata, name = raw[index].split(), raw[index + 1]
        index += 2
        if metadata[4][:1] in (b'R', b'C'):
            name, index = raw[index], index + 1
        before, after = metadata[2:4]
        if after.strip(b'0') and before != after and metadata[1] != b'160000':
            entries.append((name, before, after))
    return entries


def added_bytes(root, before, after):
    data = git(root, 'cat-file', 'blob', after.decode())
    if data.startswith(b'\x1f\x8b'):
        try:
            while data.startswith(b'\x1f\x8b'):
                data = gzip.decompress(data)
            return data
        except (OSError, EOFError):
            raise ValueError('changed gzip blob cannot be decompressed') from None
    try:
        data.decode('utf-8')
    except UnicodeError:
        return data
    if b'\0' in data or not before.strip(b'0'):
        return data
    patch = git(root, 'diff', '--no-ext-diff', '--no-textconv', '--no-color', '-U0', before.decode(), after.decode())
    in_hunk, added = False, []
    for line in patch.splitlines():
        if line.startswith(b'@@'):
            in_hunk = True
        elif in_hunk and line.startswith(b'+'):
            added.append(line[1:])
    return b'\n'.join(added)


def safe_name(name, compiled):
    for kind, expression in compiled:
        name = expression.sub(('[' + kind + ']').encode(), name)
    return json.dumps(os.fsdecode(name), ensure_ascii=True)


def scan(args):
    root = args.checkout
    if not branch(root).startswith('spacedock-state/'):
        return 0
    compiled, present = patterns(root)
    if not present:
        print('state guard: partial: identifier list absent', file=sys.stderr)
    _, folder = installed(root)
    modes = read_modes(folder)
    commits = [None]
    if args.event == 'pre-push':
        commits = []
        for line in sys.stdin.buffer:
            fields = line.split()
            if len(fields) != 4:
                raise ValueError('invalid pre-push input')
            _, new, ref, old = fields
            if not ref.startswith(b'refs/heads/spacedock-state/') or not new.strip(b'0'):
                continue
            revisions = [new.decode()] + (['^' + old.decode()] if old.strip(b'0') else [])
            commits.extend(git(root, 'rev-list', '--reverse', *revisions).decode().splitlines())
        commits = list(dict.fromkeys(commits))
    refused = False
    for commit in commits:
        for name, before, after in changes(root, commit):
            data = added_bytes(root, before, after)
            for kind in sorted({kind for kind, expression in compiled if expression.search(data)}):
                mode = modes[kind]
                refused |= mode == 'refuse'
                at = f' commit {commit[:12]};' if commit else ''
                print(f'state guard: {"refused" if mode == "refuse" else "warning"};{at} '
                      f'{safe_name(name, compiled)} adds a {kind} identifier', file=sys.stderr)
    if refused:
        print('Write the home directory as ~ or a state-relative path; drop private names, or record '
              'Not archived (private): <what>; reproduce: <command>. Then commit again.', file=sys.stderr)
        if args.event == 'pre-push':
            print('Unpushed commits checked: ' + ' '.join(c[:12] for c in commits) +
                  '. Rewrite locally only when all are yours; if any belongs to a peer, stop and ask FO.', file=sys.stderr)
    return int(refused)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('install', 'check', 'scan'))
    parser.add_argument('checkout', type=Path)
    parser.add_argument('--shared', action='store_true')
    parser.add_argument('--refuse', default='')
    parser.add_argument('--warn', default='')
    parser.add_argument('--event', choices=('pre-commit', 'pre-push'))
    args = parser.parse_args(argv)
    args.checkout = args.checkout.resolve()
    if args.command == 'scan' and not args.event:
        parser.error('scan needs --event')
    try:
        if args.command == 'install':
            install(args)
            return 0
        if args.command == 'check':
            status, message = check(args.checkout)
            print(message)
            return status
        return scan(args)
    except (OSError, ValueError, UnicodeError) as error:
        print('state guard: refused; ' + (str(error) if isinstance(error, ValueError) else 'guard input unreadable'), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
