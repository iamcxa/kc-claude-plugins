"""Replay merge_guard.verdict over real merged PRs: python3 replay.py <state-dir> <prs.json>..."""
import json, os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["MERGE_GUARD_STATE"] = sys.argv[1]
import merge_guard
merge_guard.LOG = merge_guard.Path(os.devnull)
seen, counts = set(), Counter()
for path in sys.argv[2:]:
    data = json.load(open(path))
    for pr in data if isinstance(data, list) else [data]:
        if pr["number"] in seen:
            continue
        seen.add(pr["number"])
        cmd = f"gh pr merge {pr['number']} --repo iamcxa/kc-claude-plugins --squash --match-head-commit {pr['headRefOid']}"
        result, why = merge_guard.verdict(cmd, "/")
        kind = "release" if pr["headRefName"].startswith("release-please") else "task-or-other"
        counts[(result, kind)] += 1
        if pr["number"] == 672 or result == "stop":
            print(pr["number"], pr["headRefName"][:40], result)
print(dict(counts), "total", len(seen))
