import importlib.util,json,subprocess,sys
from pathlib import Path
from datetime import timedelta
wt=Path('/tmp/dev2/kc-claude-plugins-3042bb224e995ded/captain-question-outside-a-gate-is-an-open-record/validation-2/candidate');scratch=Path('/tmp/dev2/kc-claude-plugins-3042bb224e995ded/captain-question-outside-a-gate-is-an-open-record/validation-2')
sys.path.insert(0,str(wt/'kc-dev-flow-2/scripts'))
import task_timeline as tt
rows=json.loads((scratch/'fixture-reconciliation.json').read_text())
root=scratch/'reconciled-input';root.mkdir()
clocks=set()
for i,src in enumerate(rows):
 slug=src['replay'];(root/(slug+'.md')).write_text('---\ntitle: Replay\n---\n')
 answer=tt.when(src['recorded_answer_at']);asked=answer-timedelta(minutes=10+i)
 entry=tt.write_event(root,slug,'ask',dict(asked=src['question'],asked_at='now',by='replay FO',channel='chat',holds=('task','acceptance','nothing')[i%3]),asked)
 tt.write_event(root,slug,'answer',dict(key=entry['key'],channel='chat',words=src['captain_answer'],option=None,resolution=None),answer)
 clocks.update(tt.iso(answer+timedelta(minutes=m)) for m in (-30,-5,0,5))
(root/'clocks.json').write_text(json.dumps(sorted(clocks),indent=2))
reader=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/captain-question-outside-a-gate-is-an-open-record/evidence/validation-1/blind-output/reader.py')
subprocess.run(['python3','-B',str(reader),str(root),str(scratch/'reader-output')],check=True)
expected=json.loads((scratch/'reader-output/output.json').read_text())
errors=[];snapshots=[]
for snap in expected:
 cmd=['python3','-B',str(wt/'kc-dev-flow-2/scripts/task_timeline.py'),str(root),'--open','--json','--as-of',snap['clock']]
 run=subprocess.run(cmd,cwd=wt,capture_output=True,text=True,check=True)
 actual=json.loads(run.stdout);left={r['key']:r for r in actual};right={r['key']:r for r in snap['open']}
 assert len(actual)==len(left)
 assert set(left)==set(right),snap['clock']
 for key,a in left.items():
  for field in ('key','by','waiting_since','waiting_bound','holds','interruptions','state'):assert a[field]==right[key][field],(key,field)
  assert abs(a['waiting_min']-right[key]['waiting_min'])<=0.051
  source=rows[int(key.split('#')[0].removeprefix('replay-'))-1]
  assert a['question']==source['question']
 snapshots.append(dict(clock=snap['clock'],open=actual))
(scratch/'reconciled-product-replay.json').write_text(json.dumps(snapshots,ensure_ascii=False,indent=2))
(scratch/'reconciled-comparison.json').write_text(json.dumps(dict(questions=len(rows),clocks=len(expected),rows=sum(len(s['open']) for s in expected),errors=errors,reader='saved validation-1 contract-only reader, rerun; not a new blind review',comparison_tolerance_minutes=0.051),indent=2))
print('Same fourteen questions; 56 clocks; key/owner/wait/state/holds/interruptions and complete question text match; zero mismatches')
