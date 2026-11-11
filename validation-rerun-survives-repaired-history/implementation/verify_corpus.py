import json
from pathlib import Path
import sys

data = json.loads(Path(sys.argv[1]).read_text())
summary = data["summary"]
assert summary["checked"] == 161, summary
assert summary["tasks"] == 73, summary
assert summary["pairs"] == {"0->0": 97, "1->1": 46, "2->0": 3, "2->2": 15}, summary
assert summary["errors"] == 0, data["errors"]
changed = [e for e in data["events"] if e["checked"] and e["sides"][0] != e["sides"][1]]
tasks = {(e["repo"], Path(e["task"]).stem) for e in changed}
assert tasks == {("qnow", "owner-cancels-booking"), ("kcp", "fo-interviews-extension")}, tasks
print("PASS: all 161 predicate events across 73 tasks match the approved corpus pairs; only the two named tasks change")
