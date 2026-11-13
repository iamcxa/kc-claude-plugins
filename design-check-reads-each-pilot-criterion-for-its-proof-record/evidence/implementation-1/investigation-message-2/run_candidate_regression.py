from pathlib import Path
import sys,importlib.util,unittest
root=Path(__file__).parent
sys.path.insert(0,str(root/"all-safe/kc-dev-flow-2/scripts"))
import test_design_surfaces as tests
spec=importlib.util.spec_from_file_location("exact_candidate",root/"reference/kc-dev-flow-2/scripts/design_surfaces.py")
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
tests.ds=module
result=unittest.TextTestRunner().run(unittest.TestSuite([tests.PilotProofTests("test_each_declared_id_gets_a_proof_check")]))
sys.exit(0 if result.wasSuccessful() else 1)
