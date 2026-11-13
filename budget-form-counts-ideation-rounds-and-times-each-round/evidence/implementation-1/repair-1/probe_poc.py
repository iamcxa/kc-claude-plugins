import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/"kc-dev-flow-2/scripts"))
import test_poc_readme as tests
original=tests.poc.derive
tests.poc.derive=lambda text: original(text).replace("[N ideation, ]N implementation", "N implementation")
suite=unittest.defaultTestLoader.loadTestsFromModule(tests)
result=unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(not result.wasSuccessful())
