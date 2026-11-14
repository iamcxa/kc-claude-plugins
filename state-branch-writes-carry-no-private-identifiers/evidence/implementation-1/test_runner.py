import json
import sys
import unittest
from pathlib import Path

scripts, report = map(Path, sys.argv[1:3])
sys.path.insert(0, str(scripts))
rows = []
class RecordingResult(unittest.TextTestResult):
    def addSuccess(self, test):
        super().addSuccess(test)
        rows.append(dict(name=test.id(), status='passed'))
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        rows.append(dict(name=test.id(), status='skipped', message=reason))
    def addError(self, test, error):
        super().addError(test, error)
        rows.append(dict(name=test.id(), status='failed', message=self._exc_info_to_string(error,test)))
    def addFailure(self, test, error):
        super().addFailure(test, error)
        rows.append(dict(name=test.id(), status='failed', message=self._exc_info_to_string(error,test)))
    def addSubTest(self, test, subtest, error):
        super().addSubTest(test, subtest, error)
        if error:
            rows.append(dict(name=subtest.id(), status='failed', message=self._exc_info_to_string(error,test)))

suite = unittest.TestSuite(unittest.defaultTestLoader.discover(str(scripts), pattern=name) if name.endswith('.py')
                          else unittest.defaultTestLoader.loadTestsFromName(name)
                          for name in sys.argv[3:])
result = unittest.TextTestRunner(verbosity=2, resultclass=RecordingResult).run(suite)
report.write_text(json.dumps(dict(tests=rows, run=result.testsRun, failures=len(result.failures),
                                  errors=len(result.errors), skipped=len(result.skipped)), indent=2)+'\n')
sys.exit(not result.wasSuccessful())
