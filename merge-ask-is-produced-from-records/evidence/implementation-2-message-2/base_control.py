from pathlib import Path
import hashlib,io,json,os,subprocess,sys,types,unittest
WT=Path(os.environ['PRODUCT_WORKTREE']);S=Path(__file__).parent
sys.path.insert(0,str(WT/'kc-dev-flow-2/scripts'));import test_delivery_gate as t
base='de564ef9e2b608d4106d96c56448e22f31a6fc5b'
source=subprocess.check_output(['git','-C',str(WT),'show',base+':kc-dev-flow-2/scripts/delivery_gate.py'],text=True)
m=types.ModuleType('delivery_base');m.__file__=str(WT/'kc-dev-flow-2/scripts/delivery_gate.py');exec(compile(source,m.__file__,'exec'),m.__dict__);t.gate=m
out=io.StringIO();result=unittest.TextTestRunner(stream=out,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(t.RecordRouteParityTests))
(S/'base-control.log').write_text(out.getvalue());data=dict(base=base,tests_run=result.testsRun,expected_failures=len(result.failures),unexpected_errors=len(result.errors),tests_that_catch_base=sorted({case.id().split(' (',1)[0].split('.')[-1] for case,_ in result.failures}),test_source_sha256=hashlib.sha256((WT/'kc-dev-flow-2/scripts/test_delivery_gate.py').read_bytes()).hexdigest(),scope='original checker in isolated in-memory module with final tests; product unchanged')
(S/'base-control.json').write_text(json.dumps(data,indent=2)+'\n');assert data['tests_run']==6 and len(data['tests_that_catch_base'])==6 and not result.errors,data
print('All six final regression tests reject the original checker; no test errors.')
