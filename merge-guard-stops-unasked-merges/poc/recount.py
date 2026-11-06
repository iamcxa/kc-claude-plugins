"""Record-route recount: python3 recount.py <dev2 state dir> <overlay dir> <#672 briefing index.json> <prs.json>...
For each Release, workflow-sync or learning PR, runs `merge_guard.py record` into the overlay with a question that
names the PR and its head (an assumption: no such chat question is in state), except #672, which gets its only
recorded question. Then replays every merge against the state dir plus the overlay."""
import json, os, subprocess, sys, tempfile
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
state, overlay, briefing, files = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
def kind(ref):
    return ("release" if ref.startswith("release-please") else "sync" if ref.startswith("chore/dev2-sync-")
            else "learning" if ref.startswith("learning/") else "other")
prs, seen = [], set()
for path in files:
    data = json.load(open(path))
    for pr in data if isinstance(data, list) else [data]:
        if pr["number"] not in seen:
            seen.add(pr["number"]); prs.append(pr)
recorded = Counter()
for pr in prs:
    k = kind(pr["headRefName"])
    if k == "other":
        continue
    if pr["number"] == 672:
        q = json.load(open(briefing))["question"]
    else:
        q = f"Merge {k} PR #{pr['number']} at head {pr['headRefOid'][:8]} with --match-head-commit, unless you say you merge or hold?"
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(q)
    r = subprocess.run([sys.executable, os.path.join(HERE, "merge_guard.py"), "record", overlay,
                        "--pr", f"iamcxa/kc-claude-plugins#{pr['number']}", "--head", pr["headRefOid"],
                        "--question-file", f.name, "--answer", "synthetic recount approval"], capture_output=True, text=True)
    recorded[(k, "recorded" if r.returncode == 0 else "refused")] += 1
    if r.returncode or pr["number"] == 672:
        print(pr["number"], k, "record exit", r.returncode, r.stdout.strip().replace("\n", "; "))
print("records:", dict(recorded))
r = subprocess.run([sys.executable, os.path.join(HERE, "replay.py"), f"{state}:{overlay}", *files], capture_output=True, text=True)
print(r.stdout, r.stderr, end="")
