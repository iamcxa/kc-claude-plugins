#!/usr/bin/env python3
"""Count the comment lines a candidate adds against the non-blank code lines it adds, per file and in total."""
import argparse
import collections
import subprocess
import sys

LINE = {".ts": ("//",), ".tsx": ("//",), ".js": ("//",), ".mjs": ("//",), ".sql": ("--",), ".py": ("#",)}
BLOCK = {".ts", ".tsx", ".js", ".mjs", ".sql"}


def suffix(path):
    dot = path.rfind(".")
    return path[dot:] if dot >= 0 else ""


def count(diff):
    added, comments, path, in_block = collections.Counter(), collections.Counter(), None, False
    for raw in diff.splitlines():
        if raw.startswith("+++ "):
            path, in_block = raw[6:].strip(), False
            continue
        if not raw.startswith("+") or path is None:
            continue
        text = raw[1:].strip()
        if not text:
            continue
        ext = suffix(path)
        added[path] += 1
        if in_block:
            comments[path] += 1
            in_block = "*/" not in text
        elif ext in BLOCK and text.startswith(("/*", "{/*")):
            comments[path] += 1
            in_block = "*/" not in text
        elif text.startswith(LINE.get(ext, ())) or (ext in BLOCK and text.startswith("*")):
            comments[path] += 1
    return added, comments


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base")
    parser.add_argument("candidate")
    parser.add_argument("--repo", default=".")
    args = parser.parse_args(argv)
    pathspec = [f"*{ext}" for ext in LINE]
    diff = subprocess.run(
        ["git", "-C", args.repo, "diff", "-U0", f"{args.base}...{args.candidate}", "--", *pathspec],
        capture_output=True, text=True, check=True,
    ).stdout
    added, comments = count(diff)
    total, total_comments = sum(added.values()), sum(comments.values())
    ratio = 100 * total_comments / total if total else 0.0
    print(f"code lines {total}, comment lines {total_comments}, {ratio:.1f}%")
    for path, n in comments.most_common():
        print(f"{n:4d}/{added[path]:4d} {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
