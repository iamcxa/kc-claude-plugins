"""Compare task_timeline.py dispatch counts with role_triggers.py 'spent' on every archived task that prints a budget line.
A stage with no dispatch record is listed apart: role_triggers counts records only, task_timeline also counts `entering` commits.
Usage: python3 -B compare_spent.py <task_timeline.py> <package root> <state checkout>"""
import importlib.util, re, subprocess, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("tt", sys.argv[1]); tt = importlib.util.module_from_spec(spec); spec.loader.exec_module(tt)
pkg, state = Path(sys.argv[2]), Path(sys.argv[3])
SPENT = re.compile(r"spent implementation (\d+), validation (\d+)")
same = differ = 0
for f in sorted((state / "_archive").glob("*.md")):
    out = subprocess.run([sys.executable, "-B", str(pkg / "scripts/role_triggers.py"), str(state), f.stem], capture_output=True, text=True).stdout
    m = SPENT.search(out)
    if not m:
        continue
    t = tt.timeline(state, f.stem)
    rows = {r["stage"]: r for r in t["stages"]}
    norec = [s for s in ("implementation", "validation") if s in rows and not rows[s]["dispatch_records"]]
    if norec:
        print(f"no record: {f.stem}: {', '.join(norec)} (role_triggers {m[1]},{m[2]})")
        continue
    pair = tuple(rows[s]["dispatches"] if s in rows else 0 for s in ("implementation", "validation"))
    if pair == (int(m[1]), int(m[2])):
        same += 1
    else:
        differ += 1
        print(f"differ: {f.stem}: role_triggers {m[1]},{m[2]}; task_timeline {pair[0]},{pair[1]}")
print(f"tasks with a budget line: {same + differ}; same: {same}; differ: {differ}")
sys.exit(1 if differ else 0)
