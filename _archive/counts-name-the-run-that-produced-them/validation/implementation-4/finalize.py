"""Check producer receipts and publish this repair's evidence under its task."""
import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess

root = Path.cwd()
out = root / ".context/implementation-4"
state = Path("/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state")
task = state / "counts-name-the-run-that-produced-them.md"
target = state / "counts-name-the-run-that-produced-them/validation/implementation-4"
identity = json.loads((out / "identity.json").read_text())
head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
assert head == identity["candidate"]
assert not subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"], text=True)
receipts = []
for name in ("suite", "probe", "lint", "adr", "design", "comments", "numbers-refreshed", "doc-impact",
             "mutations", "retained-mutations", "words", "learn-replay", "gate-replay", "replay-differences", "acceptance"):
    meta = json.loads((out / (name + ".json")).read_text())
    assert meta["exit"] == 0, meta
    assert meta["before"] == meta["after"], meta
    assert meta["before"]["head"] == head, meta
    assert meta["before"]["pattern_sha256"] == identity["pattern_sha256"], meta
    assert hashlib.sha256((out / meta["log"]).read_bytes()).hexdigest() == meta["sha256"], meta
    receipts.append(meta)
suite = (out / "suite.log").read_text()
assert re.search(r"Ran 1050 tests in [\d.]+s\n\nOK \(skipped=7\)", suite), suite[-3000:]
assert "warning: state fetch failed" not in (out / "numbers-refreshed.log").read_text()
before = (out / "task-before.md").read_text()
current = task.read_text()
frontmatter = lambda text: text.split("---", 2)[1]
assert frontmatter(before) == frontmatter(current)
assert current.count("**AC-9** Amended by Captain, amendment 2.") == 1
assert current.replace(current[current.index("**AC-9**"):current.index("## Needs decision")], "") == before
started = datetime.datetime.fromisoformat(json.loads((out / "baseline-corrected.json").read_text())["started"]).timestamp()
caches = []
for path in (root / "kc-dev-flow-2/scripts").rglob("*.pyc"):
    assert path.stat().st_mtime < started, path
    caches.append(dict(path=str(path.relative_to(root)), modified=path.stat().st_mtime,
                       sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
cached = root / "kc-dev-flow-2/scripts/__pycache__/count_tokens.cpython-311.pyc"
if cached.exists():
    header = cached.read_bytes()[:16]
    flags, timestamp, size = struct.unpack("<III", header[4:])
    source = root / "kc-dev-flow-2/scripts/count_tokens.py"
    assert flags == 0 and (timestamp != int(source.stat().st_mtime) or size != source.stat().st_size)
(out / "cache-inventory.json").write_text(json.dumps(dict(pre_existing=caches, changed_module_cache_invalid=True), indent=2) + "\n")
verification = dict(candidate=head, recorded=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    task_frontmatter_unchanged=True, prior_task_text_unchanged=True,
                    repair_files=identity["repair_files"], worktree_clean=True, primary_checks=receipts)
(out / "verification.json").write_text(json.dumps(verification, indent=2) + "\n")
probe = json.loads((out / "probe.log").read_text())
(out / "tests.json").write_text(json.dumps(probe["tests"], indent=2) + "\n")
for source in sorted(out.iterdir()):
    if source.is_file() and source.name != "task-before.md" and not source.name.endswith("-running.json"):
        shutil.copyfile(source, target / source.name)
files = [dict(path=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest()) for path in sorted(target.iterdir())
         if path.is_file() and path.name != "manifest.json"]
(target / "manifest.json").write_text(json.dumps(dict(candidate=head, files=files), indent=2) + "\n")
print(json.dumps(dict(candidate=head, target=str(target), verified=True)))
