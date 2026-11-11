"""Small CLI counterexamples for the two reported bypasses and native-reader failures."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

candidate, rejected, output = map(Path, sys.argv[1:4])
output.mkdir(parents=True, exist_ok=True)
rows = []
body = """---
title: Worth probe
variant: kc-dev-flow-2
profile: pilot
status: {status}
---
## FO alignment
Surfaces: none
Visible change: none
## PRFAQ
A bounded command.
{heading}
## Acceptance criteria
**AC-1** A bounded command. Evidence: run it.
"""
with tempfile.TemporaryDirectory(prefix="worth-cli-") as temporary:
    folder = Path(temporary)
    task = folder / "task.md"
    for name, status, heading, expected in (
        ("plain-missing", "ideation", "", (1, 1)),
        ("commented-status-missing", "ideation # ready for review", "", (1, 0)),
        ("quoted-status-missing", "'ideation' # review", "", (1, 0)),
        ("commented-heading", "ideation", "<!--\n### Worth questions\n-->", (1, 0)),
        ("visible-control", "ideation # ready for review", "### Worth questions\nAsked, without, premise.", (0, 0)),
    ):
        task.write_text(body.format(status=status, heading=heading))
        before = task.read_bytes()
        native = subprocess.run([os.environ["SPACEDOCK_BIN"], "status", "--workflow-dir", str(folder), "--read", str(task), "--json"], capture_output=True, text=True)
        assert native.returncode == 0, native.stderr
        assert json.loads(native.stdout)["frontmatter"]["status"] == "ideation"
        for root, wanted in zip((candidate, rejected), expected):
            run = subprocess.run([sys.executable, "-B", str(root / "kc-dev-flow-2/scripts/design_surfaces.py"), "check", str(task)], capture_output=True, text=True)
            row = dict(case=name, version=root.name, exit=run.returncode, expected=wanted, stdout=run.stdout, stderr=run.stderr, native=json.loads(native.stdout), unchanged=task.read_bytes() == before)
            rows.append(row)
            assert run.returncode == wanted and row["unchanged"], row
            print(f"{root.name}: {name}: exit {run.returncode}")
    task.write_text(body.format(status="ideation # note", heading=""))
    for name, program in (("exit-failure", "import sys; sys.stderr.write('reader refused'); sys.exit(7)"), ("timeout", "import time; time.sleep(35)")):
        stub = folder / name
        stub.write_text(f"#!{sys.executable}\n{program}\n")
        stub.chmod(0o755)
        run = subprocess.run([sys.executable, "-B", str(candidate / "kc-dev-flow-2/scripts/design_surfaces.py"), "check", str(task)], capture_output=True, text=True, env={**os.environ, "SPACEDOCK_BIN": str(stub)}, timeout=40)
        row = dict(case=name, version=candidate.name, exit=run.returncode, stdout=run.stdout, stderr=run.stderr)
        rows.append(row)
        assert run.returncode == 1 and "cannot read stage for Worth questions" in run.stdout, row
        print(f"{name}: refused with exit 1")
(output / "worth-probe.json").write_text(json.dumps(rows, indent=2) + "\n")
