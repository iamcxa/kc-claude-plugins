import io, json, os, sys, unittest
from pathlib import Path
scripts, pattern, target = sys.argv[1:]
sys.path.insert(0, scripts)
rows = []
class Result(unittest.TextTestResult):
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
suite = unittest.defaultTestLoader.discover(scripts, pattern=pattern)
result = unittest.TextTestRunner(verbosity=1, resultclass=Result).run(suite)
Path(target).write_text(json.dumps(rows, ensure_ascii=False, indent=2))
sys.exit(0 if result.wasSuccessful() else 1)
