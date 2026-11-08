#!/usr/bin/env python3
"""Run an existing unittest file and retain its per-test outcomes as JSON."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

path, destination = map(Path, sys.argv[1:])
sys.path.insert(0, str(path.parent))
spec = importlib.util.spec_from_file_location(path.stem, path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
rows = []

class Results(unittest.TextTestResult):
    def addSuccess(self, test):
        super().addSuccess(test)
        rows.append(dict(name=test.id(), status="passed"))
    def addFailure(self, test, error):
        super().addFailure(test, error)
        rows.append(dict(name=test.id(), status="failed", message=self._exc_info_to_string(error, test)))
    def addError(self, test, error):
        super().addError(test, error)
        rows.append(dict(name=test.id(), status="failed", message=self._exc_info_to_string(error, test)))
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        rows.append(dict(name=test.id(), status="skipped", message=reason))

outcome = unittest.TextTestRunner(verbosity=2, resultclass=Results).run(unittest.defaultTestLoader.loadTestsFromModule(module))
destination.write_text(json.dumps(rows, indent=2) + "\n")
sys.exit(not outcome.wasSuccessful())
