#!/usr/bin/env python3
"""List the documents (Markdown anywhere, any file under docs/) that mention what a change touched, for a per-document verdict."""
import argparse
import json
import re
import subprocess
import sys

DECLARATION = [
    re.compile(r"^(?:export\s+)?(?:default\s+)?(?:async\s+)?(?:function\*?|class|interface|type|enum|const|let|var)\s+([A-Za-z_]\w*)"),
    re.compile(r"^(?:async\s+)?(?:def|class)\s+([A-Za-z_]\w*)"),
    re.compile(r"(?i)\b(?:create|alter|drop)\s+(?:or\s+replace\s+)?(?:table|function|view|trigger|index|policy|role)\s+(?:if\s+(?:not\s+)?exists\s+)?\"?([a-z_][a-z0-9_]*)"),
]
# A name must be distinctive to count: camelCase, PascalCase with a second capital, or snake_case.
DISTINCT = re.compile(r"^(?=.{6,}$)(?:[a-z]+[A-Z]\w*|[A-Z][a-z0-9]+[A-Z]\w*|[a-z0-9]+_[a-z0-9_]+)$")
IGNORED = ("CHANGELOG.md",)


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], check=True, capture_output=True, text=True).stdout


def terms_for(repo, base, head, changed):
    terms = set()
    for path in changed:
        if not path.endswith(".md"):
            terms.add(path)
    for line in git(repo, "diff", "--unified=0", base, head).split("\n"):
        if line[:1] in "+-" and not line.startswith(("+++", "---")):
            for pattern in DECLARATION:
                terms.update(t for t in pattern.findall(line[1:]) if DISTINCT.match(t))
    return terms


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base")
    parser.add_argument("head")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    changed = [p for p in git(args.repo, "diff", "--name-only", args.base, args.head).split("\n") if p]
    terms = terms_for(args.repo, args.base, args.head, changed)
    rows = {}
    words = sorted(t for t in terms if "/" not in t)
    paths = sorted(t for t in terms if "/" in t)
    for group, flags in ((words, ["-w"]), (paths, [])):
        if not group:
            continue
        patterns = [arg for t in group for arg in ("-e", t)]
        found = subprocess.run(["git", "-C", args.repo, "grep", "-o", "-F", *flags, *patterns, args.head, "--", "*.md", "docs/"],
                               capture_output=True, text=True).stdout
        for line in found.split("\n"):
            if not line:
                continue
            _, doc, term = line.split(":", 2)
            if doc.endswith(IGNORED) or "node_modules/" in doc:
                continue
            rows.setdefault(doc, set()).add(term)
    rows = [{"doc": d, "state": "updated" if d in changed else "review", "terms": sorted(t)} for d, t in sorted(rows.items())]
    if args.json:
        print(json.dumps(rows, indent=1))
    else:
        for row in rows:
            print(f"{row['doc']}\t{row['state']}\t{', '.join(row['terms'])}")
        print(f"{len(rows)} document(s) mention what changed; each needs 'updated' or 'unaffected: <reason>'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
