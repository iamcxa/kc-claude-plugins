import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("roborev_gate", Path(__file__).with_name("roborev_gate.py"))
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

FAKE = """#!/usr/bin/env python3
import json, os, sys
cfg = json.load(open(os.environ["FAKE_ROBOREV"]))
cmd = sys.argv[1]
if cmd == "status":
    print("Daemon: running" if cfg["daemon"] else "Daemon: not running"); sys.exit(0)
if cmd == "review":
    sys.stderr.write("Enqueued job 7 for x (agent: codex)\\n"); print("done"); sys.exit(cfg["review_exit"])
if cmd == "show":
    print(json.dumps(cfg["record"])); sys.exit(0)
"""


class RoborevGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        self.repo = t / "repo"
        self.repo.mkdir()
        g = lambda *a: subprocess.run(["git", "-C", str(self.repo), *a], check=True, capture_output=True, text=True).stdout.strip()
        g("init", "-q")
        (self.repo / "a.txt").write_text("a")
        g("add", ".")
        g("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base")
        self.base = g("rev-parse", "HEAD")
        (self.repo / "a.txt").write_text("b")
        g("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qam", "change")
        self.head = g("rev-parse", "HEAD")
        self.fake = t / "roborev"
        self.fake.write_text(FAKE)
        self.fake.chmod(0o755)
        self.cfg = t / "cfg.json"

    def tearDown(self):
        self.tmp.cleanup()

    def check(self, daemon=True, review_exit=0, verdict=1, status="done", ref=None, base=None):
        record = {"verdict_bool": verdict, "output": "## Review Findings\n- **Severity**: High",
                  "job": {"status": status, "git_ref": ref or f"{self.base}..{self.head}"}}
        self.cfg.write_text(json.dumps({"daemon": daemon, "review_exit": review_exit, "record": record}))
        import os
        os.environ["FAKE_ROBOREV"] = str(self.cfg)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = gate.main(["--repo", str(self.repo), "--base", base or self.base, "--roborev", str(self.fake)])
        return code, out.getvalue()

    def test_a_bound_pass_is_clean_and_names_its_job(self):
        code, out = self.check()
        self.assertEqual(code, 0)
        self.assertIn("evidence=roborev:7", out)

    def test_a_bound_fail_is_findings_with_the_review_text(self):
        code, out = self.check(review_exit=1, verdict=0)
        self.assertEqual(code, 1)
        self.assertIn("Severity", out)

    def test_anything_unbound_or_unavailable_is_incomplete_never_clean(self):
        self.assertEqual(self.check(daemon=False)[0], 3)
        self.assertEqual(self.check(ref=f"{self.base}..{self.base}")[0], 3)
        self.assertEqual(self.check(status="failed")[0], 3)
        self.assertEqual(self.check(review_exit=1, verdict=1)[0], 3)
        self.assertEqual(self.check(verdict=None)[0], 3)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(gate.main(["--repo", str(self.repo), "--base", self.base, "--roborev", "/no/such/roborev"]), 3)

    def test_uncommitted_changes_are_incomplete(self):
        (self.repo / "a.txt").write_text("dirty")
        self.assertEqual(self.check()[0], 3)

    def test_a_bad_base_is_a_usage_error(self):
        self.assertEqual(self.check(base="no-such-ref")[0], 2)


if __name__ == "__main__":
    unittest.main()
