import os
from pathlib import Path
import contextlib,hashlib,io,json,sys,unittest
from unittest import mock
WT=Path(os.environ["PRODUCT_WORKTREE"])
S=Path(__file__).parent
sys.path.insert(0,str(WT/'kc-dev-flow-2/scripts'))
import test_delivery_gate as tests
rows=[]
# In-memory source variants leave the product candidate bytes unchanged.
mutant=tests.variant_of('snapshot["external_rounds"] = saved_rounds(task, reviewers)', 'snapshot.pop("ci")\n            snapshot["external_rounds"] = saved_rounds(task, reviewers)')
log=io.StringIO()
with mock.patch.object(tests,'gate',mutant):
 result=unittest.TextTestRunner(stream=log).run(tests.ObservedFactsTests('test_question_only_records_observed_facts_and_no_manual_summary'))
(S/'contract-field-mutation.log').write_text(log.getvalue());assert len(result.failures)==1 and not result.errors,log.getvalue()
rows.append(dict(name='producer omits contract field ci',detected=True,failures=1,output='contract-field-mutation.log'))
original=Path.read_text
for bad in ('--record-factz','--facts-rekord'):
 log=io.StringIO()
 def altered(path,*args,**kw):
  value=original(path,*args,**kw)
  return value.replace('--record-facts','--record-factz') if path==tests.CONTRACT and bad=='--record-factz' else value.replace('--facts-record','--facts-rekord') if path==tests.CONTRACT else value
 with mock.patch.object(Path,'read_text',altered),contextlib.redirect_stderr(log):
  result=unittest.TextTestRunner(stream=log).run(tests.ObservedFactsTests('test_documented_delivery_commands_use_the_tools_argument_parser'))
 (S/(bad[2:]+'-mutation.log')).write_text(log.getvalue());assert result.errors and 'unrecognized arguments' in log.getvalue(),log.getvalue()
 rows.append(dict(name='documented command typo '+bad,detected=True,parser_exit=2,errors=len(result.errors),output=bad[2:]+'-mutation.log'))
(S/'contract-mutations.json').write_text(json.dumps(rows,indent=2)+'\n')
