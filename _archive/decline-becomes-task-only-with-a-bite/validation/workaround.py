#!/usr/bin/env python3
"""Reproduce the approved ADR pointer-scan workaround in a disposable export."""
import ast, json, os, subprocess, sys, tempfile, shutil
from pathlib import Path
out = Path(__file__).resolve().parent
c = json.loads((out / "context.json").read_text())
candidate = Path(sys.argv[1])
pkg = Path(sys.argv[2])
rel = Path("kc-dev-flow-2/scripts/test_sd_dispatch.py")
old = 'ROOT.parent / "docs/adr/0047-repository-stage-model-rosters-keep-readme-defaults-when-absent.md"'
new = 'ROOT.parent / "docs/adr" / "0047-repository-stage-model-rosters-keep-readme-defaults-when-absent.md"'
source = (candidate / rel).read_text()
assert source.count(new) == 1 and old not in source
root = candidate / "kc-dev-flow-2"
assert eval(old, {"ROOT": root}) == eval(new, {"ROOT": root})
line = next(x.strip() for x in source.splitlines() if new in x)
exec(line, {"ROOT": root})
with tempfile.TemporaryDirectory(prefix="pr800-workaround-", dir="/tmp") as tmp:
    temp = Path(tmp)
    shutil.copytree(candidate, temp, dirs_exist_ok=True)
    (temp / rel).write_text(source.replace(new, old, 1))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", GIT_DIR=c["git_dir"],
               GIT_WORK_TREE=str(temp), GIT_OPTIONAL_LOCKS="0")
    r = subprocess.run(["python3", "-B", str(pkg / "scripts/adr_lint.py"), "docs/adr",
                        "--root", str(temp), "--since", c["base_sha"], "--require", "0064"],
                       cwd=temp, env=env, text=True, capture_output=True)
    (out / "workaround-literal-path.log").write_text(r.stdout+r.stderr)
    assert r.returncode == 1 and len(r.stdout.strip().splitlines()) == 1 and "points at ADR 0047, Superseded by 0050" in r.stdout, r.stdout
    adr = eval(new, {"ROOT": temp / "kc-dev-flow-2"})
    adr.write_text(adr.read_text().replace("Superseded by 0050", "Accepted", 1))
    try:
        exec(line, {"ROOT": temp / "kc-dev-flow-2"})
    except AssertionError:
        pass
    else:
        raise AssertionError("split path no longer checks ADR 0047 supersession")
print("PASS: both paths read the same ADR; split assertion still rejects Accepted; literal path reproduces the lint false positive.")
