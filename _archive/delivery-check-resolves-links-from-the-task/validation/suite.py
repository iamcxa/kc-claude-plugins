import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys

wt = Path(sys.argv[1]).resolve()
sdroot = Path(sys.argv[2]).resolve()
out = Path(sys.argv[3] if len(sys.argv) > 3 else Path(__file__).resolve().parent)
workflow = (wt / ".github/workflows/kc-dev-flow-2-tests.yml").read_text()
commands = re.findall(r"^\s+run: (python3 .+|SPACEDOCK_BIN=.+python3 .+)$", workflow, re.M)
rows = []
for raw in commands:
    raw = raw.replace('"$GITHUB_WORKSPACE/.sd-plugin-root"', shlex.quote(str(sdroot)))
    if raw.startswith("SPACEDOCK_BIN="):
        raw = "python3 " + raw.split("python3 ", 1)[1]
    args = shlex.split(raw)
    args[:1] = [sys.executable, "-B"]
    name = Path(args[2]).stem
    log = out / (name + ".log")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", SPACEDOCK_BIN="/Users/kent/.local/bin/spacedock")
    try:
        run = subprocess.run(args, cwd=wt, env=env, capture_output=True, text=True, timeout=240)
        text = run.stdout + run.stderr
        code = run.returncode
    except subprocess.TimeoutExpired as error:
        text = str(error)
        code = 124
    log.write_text(text)
    count = sum(int(n) for n in re.findall(r"Ran (\d+) tests?", text))
    rows.append({"name": name, "status": "passed" if code == 0 else "failed",
                 "message": f"exit={code}; {count} unittest cases; {log}", "file": str(args[2]),
                 "exit": code, "count": count, "command": shlex.join(args)})
    (out / "suite.json").write_text(json.dumps(rows, indent=2))
    print(f"{name}: exit={code}, tests={count}", flush=True)
sys.exit(0 if all(r["exit"] == 0 for r in rows) else 1)

