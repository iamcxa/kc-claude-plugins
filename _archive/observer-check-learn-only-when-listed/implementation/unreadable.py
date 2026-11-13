#!/usr/bin/env python3
"""Exercise a real unreadable README without touching an adopter or product file."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

p = argparse.ArgumentParser()
p.add_argument("--code", type=Path, required=True)
p.add_argument("--scratch", type=Path, required=True)
a = p.parse_args()
assert a.scratch.resolve().is_relative_to(a.code.resolve())
a.scratch.mkdir(exist_ok=True)
env = {**os.environ, "GIT_AUTHOR_NAME": "Fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
       "GIT_COMMITTER_NAME": "Fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
       "PYTHONDONTWRITEBYTECODE": "1"}
with tempfile.TemporaryDirectory(dir=a.scratch) as folder:
    root = Path(folder)
    state = root / "state"
    (state / "_archive").mkdir(parents=True)
    (state / "_archive/example.md").write_text("---\ntitle: fixture\n---\n")
    readme = root / "README.md"
    readme.write_text("---\nentity-type: task\nextensions: [learn]\n---\n")
    for args in [("init", "-b", "main"), ("add", "--", "_archive/example.md"), ("commit", "-m", "fixture")]:
        subprocess.run(["git", "-C", str(state), *args], capture_output=True, env=env, check=True)
    readme.chmod(0)
    try:
        done = subprocess.run(["python3", "-B", str(a.code / "kc-dev-flow-2/scripts/observer_check.py"),
                               str(state), "example", "--readme", str(readme)],
                              capture_output=True, text=True, env=env)
        result = {"exit": done.returncode, "permission_denied_observed": "Permission denied" in done.stdout,
                  "diagnostic_present": "workflow README unreadable" in done.stdout,
                  "next_actions": sum(line.startswith("next:") for line in done.stdout.splitlines()),
                  "stderr_empty": not done.stderr}
        print(json.dumps(result, indent=2))
        assert result == {"exit": 2, "permission_denied_observed": True, "diagnostic_present": True,
                          "next_actions": 0, "stderr_empty": True}
    finally:
        readme.chmod(0o600)
a.scratch.rmdir()
