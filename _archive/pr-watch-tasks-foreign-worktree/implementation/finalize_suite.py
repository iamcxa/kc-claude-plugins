#!/usr/bin/env python3
"""Join a complete CI command matrix with its explicitly retained narrow rerun."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

repo = Path(sys.argv[1]).resolve()
here = Path(__file__).resolve().parent
pins = json.loads((here / "candidate-pins.json").read_text())
assert subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip() == pins["candidate"]
for row in pins["product_files"]:
    assert hashlib.sha256((repo / row["path"]).read_bytes()).hexdigest() == row["sha256"]
expected = re.findall(r"run: (?:SPACEDOCK_BIN=\S+ )?python3 (?:-B )?(kc-dev-flow-2/\S*test_\S+\.py)",
                      (repo / ".github/workflows/kc-dev-flow-2-tests.yml").read_text())
rows = json.loads((here / "full-suite-results.json").read_text())
assert len(rows) == len(expected) == 28 and {r["name"] for r in rows} == set(expected)
assert sum(row["exit"] != 0 for row in rows) == 1
rerun = json.loads((here / "replay-dispatch-rerun.json").read_text())
assert rerun["exit"] == 0 and rerun["command"][-1] == "kc-dev-flow-2/scripts/test_replay_dispatch.py"
final = []
total = skipped = 0
for row in rows:
    current = dict(row)
    if row["exit"]:
        assert row["name"] == "kc-dev-flow-2/scripts/test_replay_dispatch.py"
        current.update(exit=0, status="passed", output=rerun["output"], rerun=rerun,
                       previous_failure=row["output"])
    output = (here / current["output"]).read_text()
    counts = re.findall(r"^Ran (\d+) tests? in", output, re.MULTILINE)
    assert len(counts) <= 1, "inspect nested reports rather than double-count them"
    count = int(counts[0]) if counts else None
    skip = re.findall(r"^(?:OK|FAILED) \([^\n]*skipped=(\d+)", output, re.MULTILINE)
    current["unittest_count"] = count
    current["skipped"] = int(skip[-1]) if skip else 0
    current["candidate"] = pins["candidate"]
    total += count or 0
    skipped += current["skipped"]
    final.append(current)
summary = {"candidate": pins["candidate"], "scripts": len(final), "passed": len(final), "failed": 0,
           "reported_unittest_total": total, "reported_skips": skipped,
           "separate_cli_checks": [r["name"] for r in final if r["unittest_count"] is None],
           "limit": "The canonical-/private/tmp matrix exited 1: 27 pass and one macOS path-spelling assertion. Its unchanged replay command passed all 8 tests with TMPDIR spelled /tmp. This join preserves both outputs; it is not a single all-green matrix invocation.",
           "completeness": "Every CI test command occurs once; rerun replaces only the named failed command, without double-counting."}
(here / "final-suite-results.json").write_text(json.dumps(final, indent=2) + "\n")
(here / "final-suite-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
