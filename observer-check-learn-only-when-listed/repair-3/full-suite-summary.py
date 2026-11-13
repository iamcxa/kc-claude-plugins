#!/usr/bin/env python3
"""Account for every script in the repository-declared local unit command."""
import json
from pathlib import Path
import re

root = Path(__file__).parent
run = json.loads((root / "full-suite-exit.json").read_text())
manifest = json.loads((root / "full-suite-files.json").read_text())
text = (root / "full-suite.log").read_text()
blocks = list(re.finditer(r"Ran (\d+) tests? in [^\n]+\n\n(OK(?: \(skipped=(\d+)\))?|FAILED[^\n]*)", text))
assert run["exit"] == 0, run
assert len(blocks) == manifest["total"] == len(set(manifest["files"])), (len(blocks), manifest["total"])
rows = []
for file, block in zip(manifest["files"], blocks):
    assert block[2].startswith("OK"), (file, block[2])
    total, skipped = int(block[1]), int(block[3] or 0)
    rows.append({"file": file, "total": total, "passed": total - skipped, "skipped": skipped, "status": "passed"})
result = {"command_exit": run["exit"], "scripts": len(rows), "duplicates": 0,
          "total": sum(row["total"] for row in rows), "passed": sum(row["passed"] for row in rows),
          "skipped": sum(row["skipped"] for row in rows), "results": rows,
          "boundary": "repository merge-test command; three pinned-Spacedock integration scripts excluded by that command"}
(root / "full-suite-summary.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({key: result[key] for key in ["command_exit", "scripts", "duplicates", "total", "passed", "skipped"]}))
