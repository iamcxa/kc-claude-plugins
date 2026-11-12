#!/usr/bin/env python3
"""Check a saved formatter output against amendment 4 using wc -w."""
import json
from pathlib import Path
import subprocess
import sys

path, count = Path(sys.argv[1]), int(sys.argv[2])
done = subprocess.run(["wc", "-w", str(path)], capture_output=True, text=True, check=True)
words = int(done.stdout.split()[0])
result = {"held_tasks": count, "measured_words": words, "maximum_words": count + 20, "passed": words <= count + 20}
print(json.dumps(result))
raise SystemExit(0 if result["passed"] else 1)
