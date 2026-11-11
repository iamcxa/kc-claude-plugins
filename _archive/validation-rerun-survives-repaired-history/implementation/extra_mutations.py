import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from replay import compare, git, module

source, scratch, output, package = map(Path, sys.argv[1:])
old = module(scratch / "tag/kc-dev-flow-2/scripts/dispatch_records.py", "old")
results = []
for key in ("qnow", "web"):
    git(scratch, "clone", "--quiet", "--no-checkout", str(scratch / key), str(scratch / (key + "-falsifier")))
mutant = module(scratch / "mutations/remove-historical-catch/dispatch_records.py", "no_catch")
for rev in ("071fe3b6", "cf9560fc", "744eaa08", "5868a574", "b99a7543"):
    pair = compare(scratch / "qnow-falsifier", rev, "owner-cancels-booking/dispatch/validation-3.md", old, mutant)
    assert [r["exit"] for r in pair] == [2, 2], pair
    results.append({"mutation": "remove-historical-catch", "commit": rev, "sides": pair})
mutant = module(scratch / "mutations/identity-always-absent/dispatch_records.py", "no_identity")
pair = compare(scratch / "web-falsifier", "fda02ff5", "_archive/number-tag-shows-send-time/dispatch/validation-999.md", old, mutant)
assert [r["exit"] for r in pair] == [2, 0], pair
results.append({"mutation": "identity-always-absent", "commit": "fda02ff5", "outside-approved-corpus-change": True, "sides": pair})
root = scratch / "mutations/allow-same-commit-ruling"
shutil.copytree(source / "kc-dev-flow-2/scripts", root, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
p = root / "dispatch_records.py"
s = p.read_text()
before = "all(c != report_commit and ancestor(report_commit, c) for c in appearances)"
assert s.count(before) == 1
p.write_text(s.replace(before, "all(ancestor(report_commit, c) for c in appearances)"))
done = subprocess.run([sys.executable, "-B", "-m", "unittest", "test_dispatch_records.LiveValidationRulingTests.test_old_and_same_commit_rulings_do_not_clear"],
                      cwd=root, capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
(output / "mutation-existing-suite.log").write_text(done.stdout + done.stderr)
assert done.returncode == 1 and "FAIL:" in done.stderr and "ERROR:" not in done.stderr
results.append({"mutation": "allow-same-commit-ruling", "exit": done.returncode, "killed": True})
adr = "docs/adr/0045-validation-reruns-require-a-later-recorded-captain-ruling.md"
p = scratch / adr
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text((source / adr).read_text().replace("**Recommended:**", "**Recommendation omitted:**", 1))
done = subprocess.run([sys.executable, "-B", str(package / "scripts/adr_lint.py"), str(p.parent), "--root", str(scratch), "--require", "0045"], capture_output=True, text=True)
(output / "mutation-adr-lint-only.log").write_text(done.stdout + done.stderr)
assert done.returncode == 1 and "Decision needs a '**Recommended:**' line" in done.stdout
assert "no pointer" not in done.stdout
results.append({"mutation": "omit-required-adr-recommendation", "exit": done.returncode, "killed": True})
(output / "extra-mutations.json").write_text(json.dumps(results, indent=2) + "\n")
print("qnow five repaired commits held by no-catch mutant; web unruled rerun exposed by absent-identity mutant; existing-suite and ADR falsifiers killed", flush=True)
