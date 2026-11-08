#!/usr/bin/env python3
"""Run the package's checked-in CI Python commands locally, without installing tools."""
import argparse
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--code-root", type=Path, required=True)
parser.add_argument("--output-dir", type=Path, required=True)
args = parser.parse_args()
args.output_dir.mkdir(parents=True, exist_ok=True)
workflow = (args.code_root / ".github/workflows/kc-dev-flow-2-tests.yml").read_text()
commands = re.findall(r"^        run: (.*python3 .*)$", workflow, re.M)
assert commands
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
env.pop("SD_PLUGIN_ROOT", None)
results = []
for number, command in enumerate(commands, 1):
    words = shlex.split(command)
    if words[0].startswith("SPACEDOCK_BIN="):
        words.pop(0)
    assert words[0] == "python3"
    words[:1] = [sys.executable, "-B"]
    words = [os.environ["SD_PLUGIN_ROOT"] if word == "$GITHUB_WORKSPACE/.sd-plugin-root" else word for word in words]
    name = Path(words[2]).stem
    result = subprocess.run(words, cwd=args.code_root, env=env, capture_output=True, text=True, timeout=240)
    output = result.stdout + result.stderr
    (args.output_dir / f"{number:02d}-{name}.log").write_text(output)
    count = re.search(r"Ran (\d+) tests? in", output)
    skips = re.search(r"OK \(skipped=(\d+)\)", output)
    row = dict(name=name, status="passed" if result.returncode == 0 else "failed", exit=result.returncode,
               tests=int(count[1]) if count else None, skipped=int(skips[1]) if skips else 0,
               command=words, message="CI command replay; optional SD_PLUGIN_ROOT unset as in CI")
    results.append(row)
    (args.output_dir / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(row), flush=True)
sys.exit(any(row["exit"] for row in results))
