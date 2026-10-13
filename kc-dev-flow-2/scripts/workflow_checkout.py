#!/usr/bin/env python3
"""Compare a workflow README on disk with the trunk's copy of the same file.

Usage: workflow_checkout.py <workflow README>
Fetches origin/<trunk> (trunk: from the README's frontmatter), then compares the bytes of the README on disk
with the trunk's blob at the same repository-relative path.
Exit 0 when they are equal. Exit 1 when they differ (behind, ahead or edited): stdout names the remedy and the
dispatch holds. Exit 2 when the comparison cannot be made (usage, not a git work tree, no trunk: key, origin
unreachable, README not on origin/<trunk>): stdout names the cause and the dispatch holds. Only this one file
is compared, not the rest of the workflow directory.
"""
import os
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from number_guards import Misconfigured, frontmatter  # noqa: E402


class Unverifiable(Exception):
    pass


def git(top, *args):
    done = subprocess.run(["git", "-C", str(top), *args], capture_output=True, text=True)
    if done.returncode:
        raise Unverifiable(f"git {' '.join(args)}: {done.stderr.strip() or 'failed'}")
    return done.stdout.strip()


def fetch(top, trunk):
    git(top, "fetch", "origin", f"+refs/heads/{trunk}:refs/remotes/origin/{trunk}")


def checkout_root(readme, prefix):
    """The checkout's top as the caller spelled it, so the printed remedy runs as typed."""
    lexical = Path(os.path.abspath(readme)).parent
    for _ in Path(prefix).parts:
        lexical = lexical.parent
    return lexical


def remedy(top, trunk):
    branch = subprocess.run(["git", "-C", str(top), "symbolic-ref", "-q", "--short", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    if branch:
        return f"bring branch {branch} level with origin/{trunk} (merge or rebase), then rerun"
    return f"git -C {shlex.quote(str(top))} checkout --detach origin/{trunk}"


def compare(readme):
    here = readme.resolve().parent
    try:
        prefix = git(here, "rev-parse", "--show-prefix")
        top = git(here, "rev-parse", "--show-toplevel")
    except Unverifiable:
        raise Unverifiable(f"{readme} is not inside a git work tree")
    try:
        trunk = frontmatter(readme).get("trunk")
    except Misconfigured as err:
        raise Unverifiable(str(err))
    if not trunk:
        raise Unverifiable(f"{readme} declares no trunk: key in its frontmatter")
    try:
        fetch(top, trunk)
    except Unverifiable as err:
        raise Unverifiable(f"cannot fetch origin/{trunk}, so the README cannot be compared with it: {err}")
    path = f"{prefix}{readme.name}"
    try:
        theirs = git(top, "rev-parse", f"origin/{trunk}:{path}")
    except Unverifiable:
        raise Unverifiable(f"{path} is not tracked on origin/{trunk}")
    ours = git(top, "hash-object", "--no-filters", str(readme.resolve()))
    head = git(top, "rev-parse", "--short", "HEAD")
    if ours == theirs:
        return 0, f"README matches origin/{trunk} ({ours[:8]}; checkout HEAD {head})"
    return 1, (f"README differs from origin/{trunk}: on disk {ours[:8]}, origin/{trunk} {theirs[:8]} "
               f"(checkout HEAD {head}). Dispatch holds. Remedy: "
               f"{remedy(checkout_root(readme, prefix), trunk)}")


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1 or not Path(args[0]).is_file():
        print(__doc__.strip())
        return 2
    try:
        code, message = compare(Path(args[0]))
    except Unverifiable as err:
        print(f"cannot verify the workflow README against its trunk: {err}. Dispatch holds.")
        return 2
    print(message)
    return code


if __name__ == "__main__":
    sys.exit(main())
