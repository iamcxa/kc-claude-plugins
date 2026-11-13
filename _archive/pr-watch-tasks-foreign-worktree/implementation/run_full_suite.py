#!/usr/bin/env python3
import concurrent.futures
import json
import os
from pathlib import Path
import re
import subprocess
import sys

repo = Path(sys.argv[1]).resolve()
sd_root = Path(sys.argv[2]).resolve()
sd_bin = str(Path(sys.argv[3]).resolve())
here = Path(__file__).resolve().parent
logs = here / "suite"
logs.mkdir(exist_ok=True)
temporary = Path(sys.argv[4]).absolute()
temporary.mkdir(parents=True, exist_ok=False)
workflow = repo / ".github/workflows/kc-dev-flow-2-tests.yml"
scripts = re.findall(r"run: (?:SPACEDOCK_BIN=\S+ )?python3 (?:-B )?(kc-dev-flow-2/\S*test_\S+\.py)", workflow.read_text())
assert len(scripts) == len(set(scripts)) and len(scripts) >= 25
env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "SPACEDOCK_BIN": sd_bin, "TMPDIR": str(temporary)}


def run(script):
    argv = [sys.executable, "-B", script]
    if script.endswith("test_sd_dispatch.py"):
        argv += ["--sd-plugin-root", str(sd_root)]
    out = logs / (script.replace("/", "_") + ".log")
    try:
        done = subprocess.run(argv, cwd=repo, env=env, text=True, capture_output=True, timeout=600)
        text = done.stdout + done.stderr
        code = done.returncode
    except subprocess.TimeoutExpired as failure:
        text = str(failure.stdout or "") + str(failure.stderr or "") + "\nTIMEOUT 600s\n"
        code = 124
    out.write_text(text)
    counts = [int(x) for x in re.findall(r"Ran (\d+) tests? in", text)]
    row = {"name": script, "command": argv, "exit": code, "status": "passed" if code == 0 else "failed",
           "unittest_count": sum(counts) if counts else None, "output": str(out.relative_to(here))}
    print(json.dumps(row), flush=True)
    return row


with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(run, scripts))
(here / "full-suite-results.json").write_text(json.dumps(results, indent=2) + "\n")
(here / "full-suite-summary.json").write_text(json.dumps({"scripts": len(results),
    "passed": sum(r["exit"] == 0 for r in results), "failed": sum(r["exit"] != 0 for r in results),
    "reported_unittest_total": sum(r["unittest_count"] or 0 for r in results),
    "scripts_without_unittest_count": [r["name"] for r in results if r["unittest_count"] is None],
    "pinned_sd_source_commit": "4d158a484ec73e184861067f8ed1e20087fdc26a",
    "temporary_root": str(temporary), "remaining_fixture_children": [str(x) for x in temporary.iterdir()]}, indent=2) + "\n")
sys.exit(0 if all(r["exit"] == 0 for r in results) else 1)
