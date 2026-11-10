import contextlib,copy,hashlib,io,json,pathlib,sys,subprocess,tempfile
out=pathlib.Path(__file__).parent
root=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(root/'kc-dev-flow-2/scripts'))
import test_learning as t
from count_tokens import count_sentences,numbers
import delivery_gate as gate
record=json.loads((out/'cycle-record.json').read_text())
decision=next(x for x in record['evaluation']['decisions'] if x['action']=='add')
fixture=t.LearningTests();fixture.setUp()
try:
 fixture.pack['evidence']=decision['evidence'];fixture.write_pack();claim=fixture.claim()
 observed=[]
 for label,content in [('original',decision['entry']['Evidence']),('ordinal-reword',decision['entry']['Evidence'].replace('Cycle 1 FO line','first-cycle FO line'))]:
  d=copy.deepcopy(decision);d['entry']['Evidence']=content
  result=subprocess.run(fixture.argv('complete','--job',claim['job'],'--token',claim['token'],'--result',fixture.result_file([d])),capture_output=True,text=True)
  state=fixture.cli('read','--job',claim['job'])['state']
  observed.append(dict(label=label,exit=result.returncode,result=json.loads(result.stdout),state=state))
 assert [r['exit'] for r in observed]==[1,0],observed
 assert [r['state'] for r in observed]==['pending','completed']
 print(json.dumps(dict(probe='actual historical wording through fresh claim and complete CLI',observed=observed),ensure_ascii=False))
finally: fixture.doCleanups()
# Same bounded checks after deliberately omitting source matching.
assert not count_sentences('cycle 2, round 2')
assert numbers('P1 S1')==set()
assert count_sentences('Cycle 1 FO line')==[('Cycle 1 FO line',{'1'})]
with tempfile.TemporaryDirectory() as d:
 folder=pathlib.Path(d);f=folder/'result.log';f.write_text('3 cells')
 assert gate.count_problems(folder,'3 cells (result.log)')==(1,[])
 assert gate.count_problems(folder,'2 cells (result.log)')==(0,['2 cells (result.log)'])
 assert gate.count_problems(folder,'3 of 6 (result.log)')[1]
print(json.dumps(dict(probe='grammar and source falsifiers',comma_count=count_sentences('cycle 2, round 2'),identifier_numbers=sorted(numbers('P1 S1')),cycle=count_sentences('Cycle 1 FO line')[0][0])))
