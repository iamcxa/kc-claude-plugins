"""Disposable ideation replay: python3 -B replay.py <code repo> <owner/repo> <merged-prs.json>
Prints the verdict the designed audit would give each merged PR. Reads committed refs only."""
import json, re, subprocess, sys

def git(repo, *a):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True).stdout

repo, slug, prs_file = sys.argv[1:4]
ASK = re.compile(r"(?:^|/)merge/ask-\d+\.json$")
TASK_PR = re.compile(r"^pr:\s*(?:pr-merge:)?#?(\d+)\s*$", re.M)
SYNC = re.compile(r"^chore\([\w.-]+\): sync workflow to kc-dev-flow-2 v")
records, owners = {}, {}
refs = git(repo, "for-each-ref", "--format=%(refname) %(committerdate:iso-strict)",
           "refs/heads/spacedock-state/", "refs/remotes/origin/spacedock-state/").splitlines()
print("# read:", "; ".join(refs))
for ref in (r.split()[0] for r in refs):
    for path in git(repo, "ls-tree", "-r", "--name-only", ref).split():
        if ASK.search(path):
            try:
                rec = json.loads(git(repo, "show", f"{ref}:{path}"))
            except ValueError:
                continue
            records.setdefault(rec.get("pr"), []).append((str(rec.get("head", "")).lower(), f"{ref.split('/', 2)[2]}:{path}"))
        elif path.endswith(".md") and path.count("/") <= 1 and not path.startswith((".", "_debriefs")):
            m = TASK_PR.search(git(repo, "show", f"{ref}:{path}").split("\n---", 1)[0])
            if m:
                owners.setdefault(int(m.group(1)), f"{ref.split('/', 2)[2]}:{path}")
counts = {}
for pr in sorted(json.load(open(prs_file)), key=lambda p: p["number"]):
    n, head, branch, title = pr["number"], pr["headRefOid"].lower(), pr["headRefName"], pr["title"]
    recs = records.get(f"{slug}#{n}", [])
    hit = [src for h, src in recs if len(h) >= 7 and head.startswith(h)]
    if hit:
        verdict, note = "carried", hit[0]
    elif branch.startswith("release-please--branches--"):
        verdict, note = "release", branch
    elif SYNC.match(title):
        verdict, note = "sync", title
    elif re.fullmatch(r"learning/[0-9a-f]{64}", branch):
        verdict, note = "learning", branch[:22]
    elif recs:
        verdict, note = "head differs", "; ".join(f"{h[:12]} in {s}" for h, s in recs)
    else:
        verdict, note = "no ask record", owners.get(n, "no task in readable state")
    counts[verdict] = counts.get(verdict, 0) + 1
    print(f"{verdict} | #{n} | merged {pr['mergedAt']} head {head[:12]} | {note}")
print("# counts:", counts, "total", sum(counts.values()))
