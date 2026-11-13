import importlib, json, os, pathlib, sys, unittest
sys.path.insert(0, sys.argv[1])
name = sys.argv[2]
rows = []
class Results(unittest.TextTestResult):
    def addSuccess(self, test):
        super().addSuccess(test); rows.append(dict(name=test.id(), status="passed"))
    def addFailure(self, test, error):
        super().addFailure(test, error); rows.append(dict(name=test.id(), status="failed", message=self._exc_info_to_string(error, test)))
    def addError(self, test, error):
        super().addError(test, error); rows.append(dict(name=test.id(), status="failed", message=self._exc_info_to_string(error, test)))
    def addSkip(self, test, reason):
        super().addSkip(test, reason); rows.append(dict(name=test.id(), status="skipped", message=reason))
suite = unittest.defaultTestLoader.loadTestsFromName(name)
result = unittest.TextTestRunner(verbosity=1, resultclass=Results).run(suite)
pathlib.Path(sys.argv[3]).write_text(json.dumps(rows, indent=2))
sys.exit(not result.wasSuccessful())
