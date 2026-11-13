"""rounds_census.py <scripts dir> <state checkout>: per-round census over every archived task."""
import sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import task_timeline as tt
state = Path(sys.argv[2]); archive = state / "_archive"
slugs = {p.stem for p in archive.glob("*.md")} | {p.parent.name for p in archive.glob("*/index.md")}
results, rounds, ideation, mismatch, zero, no_end = Counter(), 0, 0, 0, 0, 0
for slug in sorted(slugs):
    for row in tt.timeline(state, slug)["stages"]:
        for r in row["rounds"]:
            rounds += 1
            results["next <stage>" if r["result"].startswith("next ") else r["result"]] += 1
            zero += r["minutes"] == 0.0
            no_end += r["end"] is None
        if row["stage"] == "ideation":
            ideation += len(row["rounds"])
            mismatch += len(row["rounds"]) != row["dispatches"]
print(f"archived tasks {len(slugs)}; rounds {rounds}; ideation rounds {ideation}; "
      f"ideation rows whose round count differs from dispatches {mismatch}; rounds without end {no_end}; zero-minute rounds {zero}")
print("results: " + "; ".join(f"{k} {v}" for k, v in sorted(results.items())))

assert mismatch == 0 and no_end == 0, (mismatch, no_end)
