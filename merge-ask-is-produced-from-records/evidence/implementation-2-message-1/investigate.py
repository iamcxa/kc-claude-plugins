from pathlib import Path
import contextlib,hashlib,importlib.util,io,json,os,re,sys
from unittest import mock
WT=Path(os.environ["PRODUCT_WORKTREE"])
S=Path(__file__).parent
sys.path.insert(0,str(WT/'kc-dev-flow-2/scripts'))
import test_delivery_gate as t
g=t.gate

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
cx=load('codex_fixture',WT/'kc-dev-flow-2/extensions/codex/test_codex_review.py')
cp=load('copilot_fixture',WT/'kc-dev-flow-2/extensions/copilot/test_copilot_review.py')
HEAD=t.HEAD40
BASE_Q=f'Review this candidate. Deliver it? Squash merge with --match-head-commit {HEAD}, and removing its clean, pushed worktree, unless he says he merges or holds.\n'
DECL='Second reviewer: copilot because the change touches review rules.\n'
API_BRANCH='''elif a[0] == "api" and any(x in json.load(open(os.path.join(d,"review-data.json"))) for x in a):
    data=json.load(open(os.path.join(d,"review-data.json")))
    key=next(x for x in a if x in data)
    print(json.dumps([data[key]] if "--slurp" in a else data[key]))
'''
GH=t.STUB_GH.replace('elif a[0] == "api":\n',API_BRANCH+'elif a[0] == "api":\n')
assert GH!=t.STUB_GH

def reviews(kind):
 codex=[cx.review(HEAD,body="Codex Review: Didn't find any major issues.")]
 copilot=[cp.review(2,cp.APPROVAL,commit=HEAD)]
 lines=[]
 if kind=='codex-p1':
  codex=[cx.review(HEAD)];line=cx.finding(HEAD,badge='P1');line.update(original_commit_id=HEAD,commit_id=HEAD);lines=[line]
 if kind=='copilot-high':
  copilot=[cp.review(2,cp.CHANGES,commit=HEAD)];line=cp.line(10,2);line['body']='High: a current-head synthetic finding is unresolved.';lines=[line]
 if kind=='copilot-quota':copilot=[cp.review(17,cp.QUOTA,commit=HEAD,at='2026-10-27T00:00:00Z')]
 return {f'repos/o/r/pulls/9/reviews':codex+copilot,f'repos/o/r/pulls/9/comments':lines,
         'repos/o/r/issues/9/comments':[],'repos/o/r/issues/9/reactions':[],'repos/o/r/issues/9/timeline':[]}

results=[]
RESULT_NAME="results.json"
def capture(label,fn):
 out=io.StringIO()
 with contextlib.redirect_stdout(out):code=fn()
 (CURRENT/(label+'.log')).write_text(out.getvalue())
 return code,out.getvalue()

def run(name,*,kind='clean',config='extensions: [codex, copilot]\nsecond-reviewer: copilot\n',q_extra='',summary_extra=None,
        body_extra='',task_transform=None,pr_changes=None,setup=None,after_check=None,rounds='External rounds: 1\n',source=True,
        reviewer_rows=None,trunk=None,required=None):
 global CURRENT
 pair={}
 for route in ('legacy','record'):
  CURRENT=S/(name+'-'+route);CURRENT.mkdir()
  task=CURRENT/'task.md';q=CURRENT/'question.txt';summary=CURRENT/'summary.txt';combined=CURRENT/'combined.txt'
  task.write_text(t.TASK+f'\n## Stage Report: validation\n- DONE: candidate {HEAD}\n### Summary\nPASSED at {HEAD}.\n'+body_extra)
  if task_transform:task.write_text(task_transform(task.read_text()))
  t.readme(CURRENT,config);proof=t.captain_record(task)
  q.write_text(BASE_Q+(q_extra.replace('Second reviewer: not triggered.\n','') if route=='legacy' else q_extra))
  decl=DECL if 'second-reviewer: copilot' in config else 'Second reviewer: codex because authority changes.\n' if 'second-reviewer: codex' in config else ''
  extra='Copilot review:2. Codex review:5.\n' if summary_extra is None else summary_extra
  summary.write_text(t.CLAUSES+rounds+decl+extra+proof)
  combined.write_text(q.read_text()+summary.read_text())
  if source:
   saved,line=t.refusal(cp.QUOTA,head=HEAD);path=g.task_folder(task)/'review/copilot-not-run.txt';path.parent.mkdir(parents=True);path.write_text(saved)
  if setup:setup(CURRENT,task,q,summary,combined,route)
  pr=t.pr_json(head=HEAD,**(pr_changes or {}))
  with mock.patch.object(t,'STUB_GH',GH),t.stubbed(CURRENT,pr=pr) as fixtures,t.quiet_roles(),contextlib.ExitStack() as stack:
   (fixtures/'review-data.json').write_text(json.dumps(reviews(kind)))
   if trunk is not None:stack.enter_context(mock.patch.object(g,'trunk_position',return_value=trunk))
   if required is not None:stack.enter_context(mock.patch.object(g,'required_checks',return_value=required))
   if reviewer_rows is not None:stack.enter_context(mock.patch.object(g,'reviewer_facts',return_value=reviewer_rows))
   cmd=['check',str(task),'--pr','o/r#9','--text-file',str(q if route=='record' else combined)]
   if route=='record':cmd+=['--record-facts']
   code,out=capture('check',lambda:g.main(cmd))
   files=sorted((g.task_folder(task)/'merge').glob('ask-*.json'))
   observations=sorted((g.task_folder(task)/'merge').glob('observation-*.json'))
   record=json.loads(files[-1].read_text()) if files else json.loads(observations[-1].read_text()) if observations else None
   if after_check:after_check(CURRENT,task,q,summary,combined,route,files or observations)
   qcmd=['question',str(task),'--text-file',str(q)]
   if route=='record':qcmd+=['--facts-record',str((files or observations)[-1])] if files or observations else ['--facts-record',str(CURRENT/'missing.json')]
   else:qcmd+=['--summary-file',str(summary)]
   qcode,qout=capture('question',lambda:g.main(qcmd))
   pair[route]={'check_exit':code,'question_exit':qcode,'check_output':str((CURRENT/'check.log').relative_to(S)),
                'question_output':str((CURRENT/'question.log').relative_to(S)),'reviewers':record.get('reviewers',[]) if record else [],
                'result':record.get('result') if record else None,'summary_has_unchecked_count':'Unchecked counts:' in summary.read_text(),
                'combined_has_unchecked_count':'Unchecked counts:' in combined.read_text(),
                'question_has_unchecked_count':'Unchecked counts:' in q.read_text(),'question_has_scope_mark':'（未對過紀錄）' in q.read_text(),
                'record_top_level':sorted(record) if record else [],'summary_warning_mark':'（未對過紀錄）' in summary.read_text(),
                'validation':record.get('validation') if record else None,'external_rounds':record.get('external_rounds') if record else None,
                'merge_result':record.get('merge_result') if record else None,
                'summary_unchecked_count':next((x for x in summary.read_text().splitlines() if x.startswith('Unchecked counts:')),None),
                'combined_unchecked_count':next((x for x in combined.read_text().splitlines() if x.startswith('Unchecked counts:')),None)}
  pair[route]['question_sha256']=hashlib.sha256(q.read_bytes()).hexdigest()
 results.append({'case':name,'kind':kind,'routes':pair})
 (S/RESULT_NAME).write_text(json.dumps(results,indent=2)+'\n')
 return pair

if __name__=='__main__':
 run('clean-control')
 run('codex-p1-undisposed',kind='codex-p1')
 run('copilot-high-undisposed',kind='copilot-high')
 run('codex-p1-no-decision-or-outcome',kind='codex-p1',config='extensions: [codex, copilot]\nsecond-reviewer: codex\n',summary_extra='')
 run('copilot-high-no-decision-or-outcome',kind='copilot-high',summary_extra='')
 _,line=t.refusal(cp.QUOTA,head=HEAD)
 run('quota-refusal-no-unread-or-retry',kind='copilot-quota',summary_extra=line)
 run('quota-refusal-disclosed-control',kind='copilot-quota',summary_extra=line+t.RETRY+'\n',q_extra='Proceed with Copilot unread? '+t.RETRY+'\n')
 # The intentionally removed quote/source requirement is distinguished from the retained retry duty.
 run('quota-refusal-no-saved-output',kind='copilot-quota',summary_extra=line+t.RETRY+'\n',source=False)
 print(json.dumps({'cases':len(results),'scope':'package GH test double with real unmodified review adapters and check/question entrypoints; synthetic public fixture; no live PR or gate writes'}))
