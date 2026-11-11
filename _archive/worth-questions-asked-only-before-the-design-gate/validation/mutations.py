#!/usr/bin/env python3
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

OUT = Path(__file__).resolve().parent
META = json.loads((OUT / "identity.json").read_text())
ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else META["scratch"])
source = ROOT / "candidate/kc-dev-flow-2/scripts"
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", SPACEDOCK_BIN="/Users/kent/.local/bin/spacedock",
           TMPDIR=str(ROOT / "tmp"))
new = """        if text.lstrip("\\ufeff\\n").startswith("---\\n"):
            try:
                stage = worth_stage(path)
                needed = stage == "ideation" or (needed and stage in (None, "", "backlog"))
            except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
                needed = False
                errors.append(f"{path.name}: cannot read stage for Worth questions: {exc}")
"""
old = """        if not needed and text.lstrip("\\ufeff\\n").startswith("---\\n"):
            try:
                needed = worth_stage(path) == "ideation"
            except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
                errors.append(f"{path.name}: cannot read stage for Worth questions: {exc}")
"""
text = (source / "design_surfaces.py").read_text()
assert text.count(new) == 1
edits = [
    ("revert-stage", new, old, "test_frontmatter_past_the_design_gate_does_not_require_worth_questions"),
    ("never-require", 'needed = stage == "ideation" or (needed and stage in (None, "", "backlog"))',
     "needed = False", "test_frontmatter_requires_worth_questions_before_the_design_gate"),
    ("drop-reader-error", '                errors.append(f"{path.name}: cannot read stage for Worth questions: {exc}")\n',
     "", "test_unreadable_stage_refuses_with_one_reader_error_and_no_worth_line"),
]
results = []
for name, before, after, test in edits:
    target = ROOT / "mutants" / name / "scripts"
    shutil.copytree(source, target)
    assert text.count(before) == 1
    (target / "design_surfaces.py").write_text(text.replace(before, after))
    command = ["python3", "-B", "-m", "unittest", "test_design_surfaces.WorthQuestionsTests." + test]
    r = subprocess.run(command, cwd=target, env=env, capture_output=True, text=True)
    results.append({"mutation": name, "command": command, "exit": r.returncode,
                    "stdout": r.stdout, "stderr": r.stderr, "killed": r.returncode == 1 and "FAIL:" in r.stderr and "ERROR:" not in r.stderr})
    assert results[-1]["killed"], results[-1]
(OUT / "mutations.json").write_text(json.dumps(results, indent=2) + "\n")
print("AC-2/3: reverse-stage, never-require and dropped-reader-error mutants all fail the relevant tests")

