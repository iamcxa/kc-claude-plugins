#!/usr/bin/env python3
"""Check amendment 2's bound against a saved fact line and native held query."""
import json
from pathlib import Path
import sys

line = Path(sys.argv[1]).read_text()
rows = json.loads(Path(sys.argv[2]).read_text())
words, maximum = len(line.split()), 3 * len(rows) + 6
print(json.dumps({"words": words, "held_tasks": len(rows), "maximum": maximum, "passed": words <= maximum}))
raise SystemExit(0 if words <= maximum else 1)
