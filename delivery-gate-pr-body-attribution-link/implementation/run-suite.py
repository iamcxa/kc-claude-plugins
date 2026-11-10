import importlib.util
import json
from pathlib import Path
import sys
import unittest

root = Path(sys.argv[1]).resolve()
scripts = root / "kc-dev-flow-2/scripts"
sys.path.insert(0, str(scripts))
spec = importlib.util.spec_from_file_location("test_delivery_gate", scripts / "test_delivery_gate.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
rows = []
class Recorded(unittest.TextTestResult):
    def addSuccess(self, test):
        super().addSuccess(test)
        rows.append({"name": test.id(), "status": "passed"})
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        rows.append({"name": test.id(), "status": "skipped", "message": reason})
    def addFailure(self, test, err):
        super().addFailure(test, err)
        rows.append({"name": test.id(), "status": "failed", "message": self._exc_info_to_string(err, test)})
    def addError(self, test, err):
        super().addError(test, err)
        rows.append({"name": test.id(), "status": "failed", "message": self._exc_info_to_string(err, test)})
    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err:
            rows.append({"name": subtest.id(), "status": "failed", "message": self._exc_info_to_string(err, test)})
result = unittest.TextTestRunner(verbosity=2, resultclass=Recorded).run(unittest.defaultTestLoader.loadTestsFromModule(module))
Path(__file__).with_name("tests.json").write_text(json.dumps(rows, indent=2))
sys.exit(0 if result.wasSuccessful() else 1)
