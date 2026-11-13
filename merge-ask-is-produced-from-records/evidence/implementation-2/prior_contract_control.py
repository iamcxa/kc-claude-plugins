import os
from pathlib import Path
import io,json,subprocess,sys,types,unittest
WT=Path(os.environ["PRODUCT_WORKTREE"]);S=Path(__file__).parent
sys.path.insert(0,str(WT/'kc-dev-flow-2/scripts'))
rev='c9cf0cc3b05b0f32bc980f1682629b33308b8fc6'
p=subprocess.run(['git','-C',str(WT),'cat-file','-e',rev+':kc-dev-flow-2/references/delivery-record.md'],capture_output=True,text=True)
assert p.returncode!=0
old=types.ModuleType('prior_poc');old.__file__=str(WT/'kc-dev-flow-2/scripts/test_poc_readme.py')
source=subprocess.check_output(['git','-C',str(WT),'show',rev+':kc-dev-flow-2/scripts/test_poc_readme.py'],text=True)
exec(compile(source,old.__file__,'exec'),old.__dict__);out=io.StringIO()
result=unittest.TextTestRunner(stream=out).run(old.DeriveTests('test_delivery_recipe_holds_nonzero_and_forwards_checked_summary_in_both_routes'))
(S/'prior-poc-control.log').write_text(out.getvalue());assert result.failures and not result.errors
(S/'prior-contract-control.json').write_text(json.dumps({'prior_candidate':rev,'contract_file_absent_exit':p.returncode,'old_recipe_tests':result.testsRun,'old_recipe_failures':len(result.failures),'old_recipe_errors':len(result.errors),'current_recipe':'test_poc_readme.py direct-file entrypoint in ci-tests.json','limit':'Prior extractor code exercised against current record-route workflow; not a full checkout or whole-suite comparison.'},indent=2)+'\n')
