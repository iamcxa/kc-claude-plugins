#!/usr/bin/env python3
import importlib.util
import json
from pathlib import Path
import sys
import unittest

repo = Path(sys.argv[1]).resolve()
here = Path(__file__).resolve().parent
temporary = []


def audit(event, args):
    if event == "tempfile.mkdtemp":
        temporary.append(str(args[0]))


sys.addaudithook(audit)
spec = importlib.util.spec_from_file_location("test_pr_watch", repo / "kc-dev-flow-2/scripts/test_pr_watch.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
result = unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromModule(module))
cleanup = [{"path": p, "exists_after_suite": Path(p).exists()} for p in temporary]
(here / "suite-cleanup.json").write_text(json.dumps(cleanup, indent=2) + "\n")
(here / "suite-result.json").write_text(json.dumps({"tests": result.testsRun, "failures": len(result.failures),
    "errors": len(result.errors), "skipped": len(result.skipped), "temporary_roots_remaining": sum(r["exists_after_suite"] for r in cleanup)}, indent=2) + "\n")
sys.exit(0 if result.wasSuccessful() and not any(r["exists_after_suite"] for r in cleanup) else 1)
