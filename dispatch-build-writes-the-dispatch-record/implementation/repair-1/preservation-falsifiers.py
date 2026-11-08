#!/usr/bin/env python3
"""Revert the preservation repair in disposable copies and rerun each regression."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--code-root", type=Path, required=True)
parser.add_argument("--output-dir", type=Path, required=True)
args = parser.parse_args()
args.output_dir.mkdir(parents=True, exist_ok=True)
methods = ["test_preexisting_untracked_record_survives_refused_build",
           "test_preexisting_staged_record_survives_refused_build",
           "test_preexisting_index_entry_without_worktree_file_is_preserved"]
old = subprocess.run(["git", "-C", str(args.code_root), "show",
                       "afa4523468a2e86e6c6e0467591df00bf8e51d35:kc-dev-flow-2/scripts/dispatch_stage.py"],
                      check=True, capture_output=True).stdout
results = []
for method in methods:
    with tempfile.TemporaryDirectory(prefix="dispatch-preservation-mutant-") as directory:
        root = Path(directory) / "kc-dev-flow-2"
        shutil.copytree(args.code_root / "kc-dev-flow-2", root, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        (root / "scripts/dispatch_stage.py").write_bytes(old)
        result = subprocess.run([sys.executable, "-B", str(root / "scripts/test_dispatch_stage.py"),
                                 f"DispatchStageTests.{method}"], env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
                                capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        (args.output_dir / f"{method}.log").write_text(output)
        caught = result.returncode != 0 and "AssertionError" in output and "FAILED (failures=1)" in output
        results.append(dict(name=method, status="passed" if caught else "failed", exit=result.returncode,
                            message="Restoring the old writer is rejected by the preservation regression"))
(args.output_dir / "results.json").write_text(json.dumps(results, indent=2) + "\n")
print(json.dumps(dict(caught=sum(row["status"] == "passed" for row in results), total=len(results))))
sys.exit(any(row["status"] != "passed" for row in results))
