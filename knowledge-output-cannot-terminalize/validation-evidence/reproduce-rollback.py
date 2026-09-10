#!/usr/bin/env python3
"""Test-only overlay. Never edits the candidate. Exit 1 reproduces lost peer data."""
import json, os, pathlib, subprocess, sys, tempfile
candidate = pathlib.Path(sys.argv[1]).resolve()
evidence = pathlib.Path(__file__).resolve().parent
output = pathlib.Path(sys.argv[2]).resolve()
output.mkdir(parents=True, exist_ok=True)
source = candidate / "internal/status/merge_guard_test.go"
with tempfile.TemporaryDirectory(prefix="knowledge-validation-overlay-") as temporary:
    temp = pathlib.Path(temporary)
    overlay_source = temp / "merge_guard_test.go"
    overlay_source.write_text(source.read_text() + (evidence / "rollback-prelock-test.patch").read_text())
    overlay = temp / "overlay.json"
    overlay.write_text(json.dumps({"Replace": {str(source): str(overlay_source)}}))
    env = dict(os.environ, VALIDATION_ARCHIVED_CAPTURE=str(output / "before-commit.md"), VALIDATION_ROLLBACK_CAPTURE=str(output / "after-failure.md"))
    command = ["go", "test", "-overlay", str(overlay), "./internal/status", "-run", "^TestValidationKnowledgeRollbackPreservesPreLockPeerEdit$", "-count=1", "-v"]
    result = subprocess.run(command, cwd=candidate, env=env, capture_output=True, text=True)
    (output / "result.json").write_text(json.dumps({"command": command, "rc": result.returncode, "stdout": result.stdout, "stderr": result.stderr}, indent=2) + "\n")
    print(result.stdout, result.stderr)
    sys.exit(result.returncode)
