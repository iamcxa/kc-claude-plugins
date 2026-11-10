import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

out = Path(__file__).parent
name, cwd, *argv = sys.argv[1:]
root = Path(cwd)
def identity():
    return dict(head=subprocess.check_output(["git", "-C", cwd, "rev-parse", "HEAD"], text=True).strip(),
                pattern_sha256=hashlib.sha256((root / "kc-dev-flow-2/scripts/count_tokens.py").read_bytes()).hexdigest())
meta = dict(name=name, cwd=cwd, argv=argv, before=identity(),
            started=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            env={key: os.environ[key] for key in ("SPACEDOCK_BIN", "PYTHONDONTWRITEBYTECODE") if key in os.environ})
with (out / (name + ".log")).open("w") as log:
    process = subprocess.Popen(argv, cwd=cwd, stdout=log, stderr=subprocess.STDOUT)
    meta["pid"] = process.pid
    (out / (name + "-running.json")).write_text(json.dumps(meta, indent=2) + "\n")
    code = process.wait()
meta.update(exit=code, after=identity(), ended=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            log=name + ".log", sha256=hashlib.sha256((out / (name + ".log")).read_bytes()).hexdigest())
(out / (name + ".json")).write_text(json.dumps(meta, indent=2) + "\n")
print(json.dumps(meta))
sys.exit(code)
