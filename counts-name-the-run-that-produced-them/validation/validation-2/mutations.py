"""Require the amendment probe to fail at both protected behavior boundaries."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

root = Path(sys.argv[1])
fixture = Path(sys.argv[2])
out = Path(__file__).parent
source = (root / "kc-dev-flow-2/scripts/count_tokens.py").read_text()
scan = r'COUNT.finditer(SEQUENCE_NUMBER.sub(r"\1#", sentence))'
assert source.count(scan) == 1
results = []
for name, replacement in (("ordinal-exclusion-removed", "COUNT.finditer(sentence)"), ("plain-count-scan-removed", "()")):
    with tempfile.TemporaryDirectory(prefix=name + "-", dir=root / ".context") as temporary:
        mutant = Path(temporary)
        scripts = mutant / "kc-dev-flow-2/scripts"
        shutil.copytree(root / "kc-dev-flow-2/scripts", scripts, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        (mutant / ".context").mkdir()
        (scripts / "count_tokens.py").write_text(source.replace(scan, replacement))
        argv = [sys.executable, "-B", str(out / "probe.py"), str(mutant), str(fixture)]
        done = subprocess.run(argv, cwd=root, capture_output=True, text=True,
                              env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"), timeout=60)
        log = out / (name + ".log")
        log.write_text(done.stdout + done.stderr)
        assert done.returncode == 1 and "AssertionError" in done.stderr, done
        assert "ImportError" not in done.stderr and "SyntaxError" not in done.stderr, done.stderr
        assert not list(mutant.rglob("*.pyc"))
        results.append(dict(name=name, exit=done.returncode, detected=True, argv=argv, log=log.name,
                            sha256=hashlib.sha256(log.read_bytes()).hexdigest()))
print(json.dumps(dict(mutants=results), indent=2))
