import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import types

wt = Path(sys.argv[1]).resolve()
out = Path(__file__).resolve().parent
scripts = wt / "kc-dev-flow-2/scripts"
sys.path.insert(0, str(scripts))
import design_surfaces as candidate
from laws_check import amendment_slug
baseline = types.ModuleType("baseline_design_surfaces")
baseline.__file__ = str(scripts / "design_surfaces.py")
source = subprocess.check_output(["git", "-C", '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-amendment-checked-when-written', "show", "6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1:kc-dev-flow-2/scripts/design_surfaces.py"], text=True)
exec(compile(source, baseline.__file__, "exec"), baseline.__dict__)
rows = []
for repo in json.loads((out / "corpus-inputs.json").read_text()):
    with tempfile.TemporaryDirectory(prefix="amendment-check-corpus-") as tmp:
        archive = subprocess.check_output(["git", "-C", repo["state"], "archive", repo["after"]])
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            tar.extractall(tmp, filter="data")
        paths = subprocess.check_output(["git", "-C", repo["state"], "ls-tree", "-r", "--name-only", repo["after"]], text=True).splitlines()
        for path in paths:
            if not amendment_slug(path):
                continue
            for seed in (False, True):
                with contextlib.redirect_stdout(io.StringIO()):
                    old = baseline.check_task(Path(tmp) / path, seed=seed)
                    new = candidate.check_task(Path(tmp) / path, seed=seed)
                rows.append({"repository": repo["name"], "path": path, "seed": seed, "same": old == new,
                             "base": old, "candidate": new})
(out / "check-comparison.json").write_text(json.dumps(rows, indent=2) + "\n")
assert all(row["same"] for row in rows), [r for r in rows if not r["same"]]
print(f"{len(rows)} task/mode verdicts unchanged across three pinned state tips")
