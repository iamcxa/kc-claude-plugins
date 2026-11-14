#!/usr/bin/env python3
"""Per class, count commits in REV_RANGE whose added lines (gzip blobs decompressed) hold a listed identifier,
split by whether the hit path is under _archive/ (archived) or not (live), and by commit subject prefix.
Prints counts and seconds per commit only, never matched text."""
import gzip, subprocess, sys, time
from collections import Counter, defaultdict
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from scan import load, classes
pats, repo, rng = load(sys.argv[1]), sys.argv[2], sys.argv[3]
def git(*a): return subprocess.run(["git", "-C", repo, *a], check=True, capture_output=True).stdout
commits = git("rev-list", "--no-merges", rng).decode().split()
hits, timings = defaultdict(Counter), []
for c in commits:
    start = time.monotonic()
    subject = git("log", "-1", "--format=%s", c).decode().split(":", 1)[0]
    kind = subject if subject in ("dispatch", "state", "gate") else "other"
    added = defaultdict(list); cur = None
    for raw in git("diff-tree", "-M", "-p", "-U0", "--no-color", "--no-ext-diff", "--root", c).decode("utf-8", "replace").splitlines():
        if raw.startswith("+++ "): cur = raw[6:]
        elif raw.startswith("+") and cur: added[cur].append(raw[1:])
    for line in git("diff-tree", "-r", "-M", "--root", "--no-commit-id", c).decode().splitlines():
        meta, path = line.split("\t", 1)
        new = meta.split()[3]; path = path.split("\t")[-1]
        if path.endswith(".gz") and set(new) != {"0"}:
            try: added[path].append(gzip.decompress(git("cat-file", "blob", new)).decode("utf-8", "replace"))
            except OSError: pass
    found = set()
    for path, lines in added.items():
        where = "archived" if path.startswith("_archive/") else "live"
        for k in classes(pats, "\n".join(lines)): found.add((k, where))
    for k, where in found:
        hits[k][where + "/" + kind] += 1
    timings.append(time.monotonic() - start)
print(f"commits scanned: {len(commits)} ({rng}); seconds per commit: median {sorted(timings)[len(timings)//2]:.2f}, max {max(timings):.2f}")
for k in ("home", "email", "private-repo", "private-slug", "tailnet-host"):
    print(f"{k}: {dict(hits[k]) or 'none'}")
