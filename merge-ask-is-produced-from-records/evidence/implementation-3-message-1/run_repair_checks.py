from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import json, os, re, subprocess

WT = Path(os.environ["PRODUCT_WORKTREE"])
PKG = Path(os.environ["PACKAGE_ROOT"])
WF = Path(os.environ["WORKFLOW_DIR"])
OUT = Path(__file__).parent
env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "TMPDIR": str(OUT)}
head = subprocess.check_output(["git", "-C", str(WT), "rev-parse", "HEAD"], text=True).strip()
assert not subprocess.check_output(["git", "-C", str(WT), "status", "--porcelain"], text=True)
commands = [
    ("lint", ["python3", "-B", "kc-dev-flow-2/scripts/lint-skills.py"]),
    ("delivery", ["python3", "-B", "kc-dev-flow-2/scripts/test_delivery_gate.py"]),
    ("poc", ["python3", "-B", "kc-dev-flow-2/scripts/test_poc_readme.py"]),
    ("comments", ["python3", "-B", str(PKG / "scripts/comment_ratio.py"),
                  "c2f035b6612f5edb42220576b3414e993531ffd6", "HEAD", "--workflow-dir", str(WF)]),
]
def run(item):
    name, command = item
    done = subprocess.run(command, cwd=WT, env=env, text=True, capture_output=True)
    output = done.stdout + done.stderr
    (OUT / (name + ".log")).write_text(output)
    totals, skipped = re.findall(r"Ran (\d+) tests? in", output), re.findall(r"skipped=(\d+)", output)
    return dict(name=name, command=command, candidate=head, exit=done.returncode,
                status="passed" if done.returncode == 0 else "failed", output=name + ".log",
                tests=int(totals[-1]) if totals else None, skipped=int(skipped[-1]) if skipped else 0)
rows = []
with ThreadPoolExecutor(max_workers=4) as pool:
    for future in as_completed([pool.submit(run, item) for item in commands]):
        row = future.result(); rows.append(row)
        (OUT / "checks.json").write_text(json.dumps(rows, indent=2) + "\n")
        print(row["name"], row["exit"], flush=True)
assert len(rows) == 4 and all(row["exit"] == 0 for row in rows)
assert subprocess.check_output(["git", "-C", str(WT), "rev-parse", "HEAD"], text=True).strip() == head
assert not subprocess.check_output(["git", "-C", str(WT), "status", "--porcelain"], text=True)
