#!/usr/bin/env python3
"""Prototype identifier scan: print file and class for each hit, never the matched text.

scan.py LIST blobs REPO REV [PATH...]   every file at REV (optionally under PATH)
scan.py LIST added REPO BASE HEAD        added lines between BASE and HEAD
scan.py LIST files FILE...               plain files on disk
Exit 1 when any hit, 0 when none, 2 on a usage or list error.
"""
import re
import subprocess
import sys
from collections import Counter


def load(path):
    groups = {}
    for number, line in enumerate(open(path, encoding="utf-8"), 1):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        kind, _, value = line.partition("\t")
        if not value:
            raise SystemExit(f"scan: list line {number} has no tab-separated value")
        pattern = value[3:] if value.startswith("re:") else (
            r"(?<![A-Za-z0-9])" + re.escape(value) + r"(?![A-Za-z0-9])")
        groups.setdefault(kind, []).append(pattern)
    return {kind: re.compile("|".join(p), re.I) for kind, p in groups.items()}


def classes(patterns, text):
    return sorted(kind for kind, rx in patterns.items() if rx.search(text))


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], check=True, capture_output=True).stdout


def main(argv):
    if len(argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    patterns, mode, rest = load(argv[1]), argv[2], argv[3:]
    hits = Counter()
    if mode == "blobs":
        repo, rev, paths = rest[0], rest[1], rest[2:]
        names = git(repo, "ls-tree", "-r", "-z", "--name-only", rev, "--", *paths).split(b"\0")
        for name in filter(None, names):
            text = git(repo, "cat-file", "blob", f"{rev}:{name.decode()}").decode("utf-8", "replace")
            for kind in classes(patterns, text):
                hits[(name.decode(), kind)] += 1
    elif mode == "added":
        repo, base, head = rest
        current = None
        for raw in git(repo, "diff", "-U0", "--no-color", "--no-ext-diff", base, head).decode("utf-8", "replace").splitlines():
            if raw.startswith("+++ "):
                current = raw[6:] if raw.startswith("+++ b/") else raw[4:]
            elif raw.startswith("+") and current:
                for kind in classes(patterns, raw[1:]):
                    hits[(current, kind)] += 1
    elif mode == "files":
        for name in rest:
            for kind in classes(patterns, open(name, encoding="utf-8", errors="replace").read()):
                hits[(name, kind)] += 1
    else:
        print(__doc__, file=sys.stderr)
        return 2
    for (name, kind), count in sorted(hits.items()):
        print(f"{name}: {kind} ({count})")
    print(f"scan: {len(hits)} file/class hit(s)")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
