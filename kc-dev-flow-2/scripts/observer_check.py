#!/usr/bin/env python3
"""Check that a task's observer report is committed in the state checkout.

Usage: observer_check.py <state checkout> <task slug> [--rev REV]
Reads the committed tree at REV (default HEAD), not the disk. The report is <slug>/observer.md before the
task is archived and _archive/<slug>/observer.md after.
Exit 0 when that file is committed and not blank; stdout names it, and repeats the first line when it
starts "observer not run:". Exit 1 when it is not: stdout names the observer dispatch and the save command.
Exit 2 when the check cannot be made (usage, not a git work tree, REV names no commit, the slug has no task at
REV): stdout names the cause. Nothing here changes the checkout.
"""
import shlex
import subprocess
import sys
from pathlib import Path

WAIVER = "observer not run:"


class Unverifiable(Exception):
    pass


def git(state, *args):
    done = subprocess.run(["git", "-C", str(state), *args], capture_output=True)
    return done.returncode, done.stdout.decode("utf-8", "replace")


def kind(state, rev, path):
    code, out = git(state, "cat-file", "-t", f"{rev}:./{path}")
    return out.strip() if code == 0 else None


def parse(args):
    rev = "HEAD"
    if "--rev" in args:
        at = args.index("--rev")
        if at + 1 >= len(args):
            raise Unverifiable("usage: --rev needs a value")
        rev = args[at + 1]
        args = args[:at] + args[at + 2:]
    if len(args) != 2 or "/" in args[1] or args[1] in ("", ".", ".."):
        raise Unverifiable("usage: observer_check.py <state checkout> <task slug> [--rev REV]")
    return Path(args[0]), args[1], rev


def locate(state, slug, rev):
    if git(state, "rev-parse", "--is-inside-work-tree")[1].strip() != "true":
        raise Unverifiable(f"{state} is not a git work tree")
    code, _ = git(state, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}")
    if code:
        raise Unverifiable(f"--rev {rev} names no commit in {state}")
    live = kind(state, rev, f"{slug}.md") == "blob" or kind(state, rev, slug) == "tree"
    archived = kind(state, rev, f"_archive/{slug}.md") == "blob" or kind(state, rev, f"_archive/{slug}") == "tree"
    if not (live or archived):
        raise Unverifiable(f"no task file or folder for {slug} at {rev} in {state}, so a missing report "
                           "cannot be told from a mistyped slug")
    return not live and archived


def check(state, slug, rev):
    archived = locate(state, slug, rev)
    path = f"_archive/{slug}/observer.md" if archived else f"{slug}/observer.md"
    code, out = git(state, "show", f"{rev}:./{path}")
    if code == 0 and out.strip():
        first = out.strip().splitlines()[0].strip()
        note = f" {first}" if first.startswith(WAIVER) else ""
        return 0, f"observer report committed: {path} at {rev}.{note}"
    where = "blank" if code == 0 else "not committed"
    if archived:
        how = (f"{slug} is archived, so its state is publish-only: dispatch kc-dev-flow-2:observer over both path "
               f"pairs ({slug}.md and {slug}/, then _archive/{slug}.md and _archive/{slug}/), save the report "
               f"unedited as {path}, then `git -C {shlex.quote(str(state))} add {shlex.quote(path)} && "
               f"git -C {shlex.quote(str(state))} commit -m \"<message>\" -- {shlex.quote(path)}` and `spacedock state commit {slug} --workflow-dir <workflow dir>` to publish it.")
    else:
        how = (f"dispatch kc-dev-flow-2:observer with only the state checkout, {slug} and the workflow README, "
               f"save the report unedited as {path}, run `spacedock state commit {slug} --workflow-dir "
               f"<workflow dir>`, then rerun this check before the sentinel.")
    return 1, f"observer report {where}: {path} at {rev}. Remedy: {how}"


def main(argv=None):
    args = sys.argv[1:] if argv is None else list(argv)
    try:
        state, slug, rev = parse(args)
        code, message = check(state, slug, rev)
    except Unverifiable as err:
        print(f"cannot tell whether the observer report is committed: {err}. Hold and report the cause.")
        return 2
    print(message)
    return code


if __name__ == "__main__":
    sys.exit(main())
