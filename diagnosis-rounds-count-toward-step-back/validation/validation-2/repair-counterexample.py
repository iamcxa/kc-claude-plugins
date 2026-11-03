import io,json,subprocess,sys,tarfile
from pathlib import Path
import proof
parent='97cf87965ec052a1c9f2d40a1a1d0ca83e8d2244'
root=proof.WT.parent/'.validation-parent'
root.mkdir(exist_ok=True)
raw=subprocess.run(['git','-C',str(proof.WT),'archive',parent,'kc-dev-flow-2'],capture_output=True,check=True).stdout
with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
 tf.extractall(root,filter='data')
for name in ('test_dispatch_records.py','test_role_triggers.py'):
 (root/'kc-dev-flow-2/scripts'/name).write_bytes((proof.PKG/'scripts'/name).read_bytes())
names=['test_dispatch_records.SymptomDispatchTests.test_one_plain_and_two_messages_count_at_folder_and_named_dispatch_checks',
'test_role_triggers.SymptomRoundsTest.test_one_plain_and_two_message_records_remind_then_owe_a_dated_call',
'test_role_triggers.SymptomRoundsTest.test_message_numbers_order_the_third_round_date_numerically']
r=proof.run(sys.executable,'-B','-m','unittest',*names,cwd=root/'kc-dev-flow-2/scripts')
(proof.OUT/'repair-parent-red.log').write_text(r.stdout+r.stderr)
assert r.returncode==1 and 'FAILED (failures=3)' in r.stdout+r.stderr,(r.returncode,r.stdout,r.stderr)
(proof.OUT/'repair-counterexample.json').write_text(json.dumps({'parent':parent,'candidate':proof.git(proof.WT,'rev-parse','HEAD').strip(),'command':[sys.executable,'-B','-m','unittest',*names],'parent_exit':r.returncode,'parent_failures':3,'candidate_pass_evidence':'acceptance.log'},indent=2))
print('All three new follow-up tests reject the pre-repair parent with assertion failures; the same tests pass at the candidate.')
