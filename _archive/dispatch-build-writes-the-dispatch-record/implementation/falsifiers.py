#!/usr/bin/env python3
"""Run the task's counterexamples in fresh, bytecode-free candidate copies."""
import argparse
import difflib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--code-root", type=Path, required=True)
parser.add_argument("--output-dir", type=Path, required=True)
args = parser.parse_args()
args.output_dir.mkdir(parents=True, exist_ok=True)
stage = "kc-dev-flow-2/scripts/dispatch_stage.py"
test = "kc-dev-flow-2/scripts/test_dispatch_stage.py"
stamp = "test_stamp_commits_complete_record_and_exact_inputs"
incomplete = "test_incomplete_record_does_not_build_or_change_state"
repeated = "test_identical_retry_reuses_only_at_adding_commit"
mutants = [
    ("AC1-no-stamp", stage,
     'command = [args.spacedock, "dispatch", "build", "--advance" if args.advance else "--stamp"]',
     'command = [args.spacedock, "dispatch", "build"] + (["--advance"] if args.advance else [])', stamp),
    ("AC1-no-model", stage, ', f"Model: {args.model}"', '', stamp),
    ("AC2-drop-scope-line", stage, '+ notes\n',
     '+ notes.replace("Keep this second scope-notes line verbatim.\\n", "")\n', stamp),
    ("AC3-no-removal", stage, 'if wrote:\n', 'if False:\n', incomplete),
    ("AC3-build-before-check", stage, '    checks = [subprocess.run',
     '    subprocess.run([args.spacedock, "dispatch", "build"], capture_output=True)\n    checks = [subprocess.run', incomplete),
    ("AC4-ignore-checker", stage, 'if any(check.returncode for check in checks):', 'if False:',
     "test_validation_candidate_is_required_before_build"),
    ("AC9-no-removal", stage, 'if wrote:\n', 'if False:\n',
     "test_failed_stamp_removes_uncommitted_record_and_passes_error"),
    ("AC9-no-identical-reuse", stage, 'if newest:\n', 'if False:\n', repeated),
    ("AC9-reuse-on-bytes-alone", stage, 'added == git(state, "rev-parse", "HEAD") and ', '', repeated),
    ("AC6-no-state-commit", stage, 'if args.advance:\n        slug', 'if False:\n        slug',
     "test_advance_commits_record_and_withholds_envelope_on_commit_failure"),
]
results = []
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")

def run(name, root, command, needle="FAILED"):
    result = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True, timeout=90)
    output = result.stdout + result.stderr
    (args.output_dir / f"{name}.log").write_text(output)
    caught = result.returncode != 0 and needle in output
    results.append(dict(name=name, status="passed" if caught else "failed", exit=result.returncode,
                        message=f"Mutation rejected; expected {needle!r}" if caught else output,
                        command=list(map(str, command))))

def seed(root):
    shutil.copytree(args.code_root / "kc-dev-flow-2", root / "kc-dev-flow-2",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copytree(args.code_root / "scripts", root / "scripts",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    (root / ".github/workflows").mkdir(parents=True)
    shutil.copyfile(args.code_root / ".github/workflows/kc-dev-flow-2-tests.yml",
                    root / ".github/workflows/kc-dev-flow-2-tests.yml")

for name, file, before, after, method in mutants:
    with tempfile.TemporaryDirectory(prefix=name + "-") as directory:
        root = Path(directory)
        seed(root)
        path = root / file
        source = path.read_text()
        assert source.count(before) == 1, (name, source.count(before))
        changed = source.replace(before, after)
        path.write_text(changed)
        (args.output_dir / f"{name}.patch").write_text("".join(difflib.unified_diff(
            source.splitlines(True), changed.splitlines(True), fromfile=file, tofile=file)))
        run(name, root, [sys.executable, "-B", str(root / test), f"DispatchStageTests.{method}"])

with tempfile.TemporaryDirectory(prefix="AC7-base-readme-") as directory:
    root = Path(directory)
    seed(root)
    source = subprocess.run(["git", "-C", str(args.code_root), "show",
                             "334d91e3165953b2ca7191e3308d80b6c02c4a99:kc-dev-flow-2/references/sd/workflow.md"],
                            check=True, capture_output=True).stdout
    (root / "kc-dev-flow-2/references/sd/workflow.md").write_bytes(source)
    run("AC7-base-passages", root, [sys.executable, "-B", "kc-dev-flow-2/scripts/lint-skills.py"], "5933 words exceeds the budget of 5931")

ci = (args.code_root / ".github/workflows/kc-dev-flow-2-tests.yml").read_text()
step = ('      - name: test_dispatch_stage.py\n'
        '        run: SPACEDOCK_BIN="$HOME/.local/bin/spacedock" python3 kc-dev-flow-2/scripts/test_dispatch_stage.py\n\n')
assert ci.count(step) == 1
assert ci.index(step) > ci.index("      - name: Install pinned Spacedock")
changed = ci.replace(step, "")
assert "test_dispatch_stage.py" not in changed
(args.output_dir / "AC8-no-CI-step.patch").write_text("".join(difflib.unified_diff(
    ci.splitlines(True), changed.splitlines(True), fromfile="workflow.yml", tofile="workflow.yml")))
results.append(dict(name="AC8-no-CI-step", status="passed", message="Deleting the step removes the real-binary seam command; hosted run remains FO-owned"))
missing = subprocess.run([sys.executable, "-B", str(args.code_root / test)],
                         env={key: value for key, value in env.items() if key != "SPACEDOCK_BIN"},
                         capture_output=True, text=True)
(args.output_dir / "AC8-missing-binary.log").write_text(missing.stdout + missing.stderr)
results.append(dict(name="AC8-missing-binary", status="passed" if missing.returncode and "SPACEDOCK_BIN" in missing.stderr else "failed",
                    exit=missing.returncode, message="Unset binary is a hard failure"))
(args.output_dir / "results.json").write_text(json.dumps(results, indent=2) + "\n")
print(json.dumps(dict(caught=sum(item["status"] == "passed" for item in results), total=len(results))))
sys.exit(any(item["status"] != "passed" for item in results))
