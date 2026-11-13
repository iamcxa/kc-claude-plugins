#!/usr/bin/env python3
"""Check that a task's observer report is committed in the state checkout.

Usage: observer_check.py <state checkout> <task slug> [--rev REV] [--readme FILE]
Reads the committed tree at REV (default HEAD), not the disk. The report is <slug>/observer.md before the
task is archived and _archive/<slug>/observer.md after.
Exit 0 when that file is committed and not blank; stdout names it, and repeats the first line when it
starts "observer not run:"; for an archived task it adds the learn steps when the workflow README lists learn.
The README is FILE, else the nearest ancestor README.md with entity-type: in its frontmatter.
An archived check with no readable workflow README exits 2 rather than guessing the extension selection.
Exit 1 when the report is not committed: stdout
names the observer dispatch and the save command, each as a `next:` line.
Exit 2 when the check cannot be made (usage, not a git work tree, REV names no commit, the slug has no task at
REV): stdout names the cause. Nothing here changes the checkout.
"""
import shlex
import subprocess
import sys
from pathlib import Path

from decision_ledger import split_task
from workflow_extensions import readme_extensions

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
    readme = None
    for flag in ("--rev", "--readme"):
        if flag not in args:
            continue
        at = args.index(flag)
        if at + 1 >= len(args):
            raise Unverifiable(f"usage: {flag} needs a value")
        if flag == "--rev":
            rev = args[at + 1]
        else:
            readme = Path(args[at + 1])
        args = args[:at] + args[at + 2:]
    if len(args) != 2 or "/" in args[1] or args[1] in ("", ".", ".."):
        raise Unverifiable("usage: observer_check.py <state checkout> <task slug> [--rev REV]")
    return Path(args[0]), args[1], rev, readme


def learn_enabled(state, readme):
    try:
        if readme is None:
            for parent in Path(state).resolve().parents:
                candidate = parent / "README.md"
                if not candidate.is_file():
                    continue
                lines, _ = split_task(candidate.read_text())
                if any(line.startswith("entity-type:") for line in lines or []):
                    readme = candidate
                    break
        if readme is None:
            raise Unverifiable("no workflow README above the state checkout; supply --readme FILE")
        return "learn" in readme_extensions(readme)
    except (OSError, ValueError) as err:
        raise Unverifiable(f"workflow README unreadable: {err}") from err


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


def check(state, slug, rev, readme=None):
    archived = locate(state, slug, rev)
    path = f"_archive/{slug}/observer.md" if archived else f"{slug}/observer.md"
    code, out = git(state, "show", f"{rev}:./{path}")
    learn = [f"next: run kc-dev-flow-2:learn for {slug}.",
             "next: send learn's notice, then the observer report unedited, in one message; answer none of its findings."] if archived and learn_enabled(state, readme) else []
    if code == 0 and out.strip():
        first = out.strip().splitlines()[0].strip()
        note = f" {first}" if first.startswith(WAIVER) else ""
        return 0, "\n".join([f"observer report committed: {path} at {rev}.{note}"] + (learn if archived else []))
    where = "blank" if code == 0 else "not committed"
    quoted = shlex.quote(str(state))
    commit = f"spacedock state commit {slug} --workflow-dir <workflow dir>"
    if archived:
        steps = [f"dispatch kc-dev-flow-2:observer over both path pairs, {slug}.md and {slug}/, then _archive/{slug}.md and _archive/{slug}/.",
                 f"save its report unedited as {path}.",
                 f"run `git -C {quoted} add {shlex.quote(path)} && git -C {quoted} commit -m \"<message>\" -- {shlex.quote(path)}`.",
                 f"run `{commit}`.",
                 "tell the Captain the observer ran after the archive."]
        steps = [f"next: {step}" for step in steps] + learn
    else:
        steps = [f"dispatch kc-dev-flow-2:observer with only the state checkout, {slug} and the workflow README.",
                 f"save its report unedited as {path}.",
                 f"if it cannot be dispatched, save the one line `{WAIVER} <reason>` there instead.",
                 f"run `{commit}`.",
                 "run the idle hooks again."]
        steps = [f"next: {step}" for step in steps]
    return 1, "\n".join([f"observer report {where}: {path} at {rev}."] + steps)


def main(argv=None):
    args = sys.argv[1:] if argv is None else list(argv)
    try:
        state, slug, rev, readme = parse(args)
        code, message = check(state, slug, rev, readme)
    except Unverifiable as err:
        print(f"cannot tell whether the observer report is committed: {err}. Hold and report the cause.")
        return 2
    print(message)
    return code


if __name__ == "__main__":
    sys.exit(main())
