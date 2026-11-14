#!/usr/bin/env python3
"""Per class, count commits in REV_RANGE whose added lines (gzip blobs decompressed) hold a listed identifier,
and split those by commit subject prefix (dispatch:, state:, gate:, other). Prints counts only."""
import gzip, re, subprocess, sys
from collections import Counter, defaultdict
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from scan import load, classes
pats, repo, rng = load(sys.argv[1]), sys.argv[2], sys.argv[3]
def git(*a): return subprocess.run(["git", "-C", repo, *a], check=True, capture_output=True).stdout
commits = git("rev-list", "--no-merges", rng).decode().split()
by_class, by_kind = Counter(), defaultdict(Counter)
for c in commits:
    subject = git("log", "-1", "--format=%s", c).decode()
    kind = subject.split(":", 1)[0] if subject.split(":", 1)[0] in ("dispatch", "state", "gate") else "other"
    found, cur = set(), None
    for raw in git("diff-tree", "-p", "-U0", "--no-color", "--no-ext-diff", "--root", c).decode("utf-8", "replace").splitlines():
        if raw.startswith("+++ "): cur = raw[6:]
        elif raw.startswith("+") and cur: found.update(classes(pats, raw[1:]))
    for line in git("diff-tree", "-r", "--root", "--no-commit-id", c).decode().splitlines():
        meta, path = line.split("\t", 1)
        new = meta.split()[3]
        if path.endswith(".gz") and set(new) != {"0"}:
            try: found.update(classes(pats, gzip.decompress(git("cat-file", "blob", new)).decode("utf-8", "replace")))
            except OSError: pass
    for k in found:
        by_class[k] += 1; by_kind[k][kind] += 1
print(f"commits scanned: {len(commits)} ({rng})")
for k in sorted(set(by_class) | {"home", "email", "private-repo", "private-slug", "tailnet-host"}):
    print(f"{k}: {by_class[k]} commits would be refused; by subject {dict(by_kind[k])}")
