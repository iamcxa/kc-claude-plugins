#!/usr/bin/env python3
"""Count the comment lines a candidate adds against the non-blank code lines it adds, per file and in total.

Exit 1 when the ratio is above the maximum (with at least FLOOR code lines added) or an added comment
cites task numbering, review provenance, a PR or issue number, or a file:line. Exit 2 on a bad maximum.
Maximum: --max, else `comment-ratio-max:` in the workflow README frontmatter, else DEFAULT_MAX.
"""
import argparse
import collections
import math
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from number_guards import Misconfigured, frontmatter

LINE = {".ts": ("//",), ".tsx": ("//",), ".js": ("//",), ".mjs": ("//",), ".sql": ("--",), ".py": ("#",)}
BLOCK = {".ts", ".tsx", ".js", ".mjs", ".sql"}
DEFAULT_MAX = 5.0
FLOOR = 20
CITES = {
    "task numbering": re.compile(r"\b(?:Decision|AC|Round|Cycle|Finding|Task)[ -]\d+\b", re.IGNORECASE),
    "review provenance": re.compile(r"\bCodex\b|\breview of\b|\breview follow-up\b|\breviewer's\b", re.IGNORECASE),
    "PR or issue number": re.compile(r"#\d+\b"),
    "file:line": re.compile(r"\.(?:py|ts|tsx|js|mjs|sql|md|json|ya?ml|sh):\d+\b"),
}
ADR = re.compile(r"\bADR \d{4}\b|docs/adr/\d{4}")


def suffix(path):
    dot = path.rfind(".")
    return path[dot:] if dot >= 0 else ""


def count(diff, found=None):
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
        else:
            continue
        if found is not None:
            found.append((path, text))
    return added, comments


def cited(found):
    return [(path, text) for path, text in found
            if not ADR.search(text) and any(pattern.search(text) for pattern in CITES.values())]


def percent(text):
    value = float(text)
    if not math.isfinite(value) or value < 0:
        raise ValueError(text)
    return value


def maximum(args):
    if args.max is not None:
        return args.max, "--max"
    if args.workflow_dir:
        readme = Path(args.workflow_dir) / "README.md"
        raw = frontmatter(readme).get("comment-ratio-max")
        if raw is not None:
            try:
                return percent(raw), f"comment-ratio-max in {readme}"
            except ValueError:
                raise Misconfigured(f"comment-ratio-max in {readme} is not a non-negative number: {raw!r}")
    return DEFAULT_MAX, "package default"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base")
    parser.add_argument("candidate")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--max", type=percent, help="maximum added-comment percent; overrides the README key")
    parser.add_argument("--workflow-dir", help="workflow directory whose README may declare comment-ratio-max")
    args = parser.parse_args(argv)
    try:
        limit, source = maximum(args)
    except Misconfigured as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    pathspec = [f"*{ext}" for ext in LINE]
    diff = subprocess.run(
        ["git", "-C", args.repo, "diff", "-U0", f"{args.base}...{args.candidate}", "--", *pathspec],
        capture_output=True, text=True, check=True,
    ).stdout
    found = []
    added, comments = count(diff, found)
    total, total_comments = sum(added.values()), sum(comments.values())
    ratio = 100 * total_comments / total if total else 0.0
    print(f"code lines {total}, comment lines {total_comments}, {ratio:.1f}%")
    for path, n in comments.most_common():
        print(f"{n:4d}/{added[path]:4d} {path}")
    failed = False
    if total < FLOOR:
        print(f"maximum {limit:g}% ({source}) not enforced: {total} code lines added, fewer than {FLOOR}")
    elif ratio > limit:
        print(f"FAIL: {ratio:.1f}% is above the maximum {limit:g}% ({source})")
        failed = True
    else:
        print(f"maximum {limit:g}% ({source}) met")
    for path, text in cited(found):
        print(f"CITE {path}: {text}")
        failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
