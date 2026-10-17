#!/usr/bin/env python3
"""Post-hoc sensitivity re-score, written after the 30 runs; it does not replace the registered deciders.

P1: no bare script name in the record (the rule probed), without requiring two names.
P2: the revision appears anywhere in the answer, and each finding's segment names its evidence file.
Other probes are unchanged. Usage: python3 -B -I sensitivity.py  (reads runs/*.jsonl and results.json)
"""
import json
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = "/opt/kdf2/kc-dev-flow-2"


def answer(run):
    for line in (HERE / "runs" / f"{run}.jsonl").read_text().splitlines():
        event = json.loads(line)
        if event.get("type") == "result":
            return event["result"]


def p1(text):
    record = text.split("=== COMMANDS ===")[0]
    names = list(re.finditer(r"[A-Za-z0-9_\-]+\.py\b", record))
    bare = [m for m in names if record[max(0, m.start() - len(PKG + "/scripts/")):m.start()] != PKG + "/scripts/"]
    return bool(names) and not bare


def p2(text):
    i1, i2 = text.find("F1"), text.find("F2")
    if min(i1, i2) < 0 or "aa6fcc91" not in text:
        return False
    first, second = sorted((i1, i2))
    seg = {("F1" if i1 < i2 else "F2"): text[first:second], ("F2" if i1 < i2 else "F1"): text[second:]}
    return "cap.py" in seg["F1"] and "backoff.py" in seg["F2"]


rows = json.loads((HERE / "results.json").read_text())
tally = defaultdict(lambda: defaultdict(int))
for r in rows:
    ok = r["followed"]
    if r["probe"] == "P1":
        ok = p1(answer(r["run"]))
    if r["probe"] == "P2":
        ok = p2(answer(r["run"]))
    tally[r["probe"]][r["arm"]] += ok
for probe in sorted(tally):
    print(probe, "A", tally[probe]["A"], "B", tally[probe]["B"])
print("total A", sum(t["A"] for t in tally.values()), "B", sum(t["B"] for t in tally.values()))
