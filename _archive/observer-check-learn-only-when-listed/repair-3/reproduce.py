#!/usr/bin/env python3
"""Reproduce the reported extension mismatch through real committed fixture history."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess

p = argparse.ArgumentParser()
p.add_argument("--code", type=Path, required=True)
a = p.parse_args()
scripts = a.code / "kc-dev-flow-2/scripts"
spec = importlib.util.spec_from_file_location("law_fixture", scripts / "test_laws_check.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
fixture = module.Base()
fixture.setUp()
try:
    repo, before = fixture.violating("parser-parity")
    fixture.learn.write_text('---\nentity-type: task\nextensions:\n  - "learn" # chosen\n---\n')
    (repo.path / "_archive").mkdir()
    module.git(repo.path, "mv", "t.md", "_archive/t.md")
    module.git(repo.path, "commit", "-m", "archive")
    code, text = fixture.judge(repo, before)
    observer = subprocess.run(["python3", "-B", str(scripts / "observer_check.py"), str(repo.path),
                               "t", "--readme", str(fixture.learn)], capture_output=True, text=True)
    result = {"laws_exit": code, "laws_skips_L1": "README lists no learn" in text,
              "laws_reports_L1_violation": "violation: L1" in text,
              "observer_exit": observer.returncode,
              "observer_prints_learn": "kc-dev-flow-2:learn" in observer.stdout}
    print(json.dumps(result, indent=2))
    assert result == {"laws_exit": 1, "laws_skips_L1": False, "laws_reports_L1_violation": True,
                      "observer_exit": 1, "observer_prints_learn": True}
finally:
    fixture.doCleanups()
