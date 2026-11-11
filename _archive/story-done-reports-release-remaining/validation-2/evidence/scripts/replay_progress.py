import os
from pathlib import Path
import subprocess,json,os,time
OUT=Path(os.environ.get('EVIDENCE_ROOT','/tmp/opencode-story-done'));ROOT=Path(os.environ.get('PRODUCT_WT','/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-story-done-reports-release-remaining'));C=ROOT/'kc-journey-map/lib/journey-progress.mjs';B=OUT/'base/kc-journey-map/lib/journey-progress.mjs';NODE=subprocess.check_output(['which','node'],text=True).strip()
results=[]
def run(label,argv,env=None):
 start=time.monotonic();p=subprocess.run([str(a) for a in argv],capture_output=True,text=True,env=env,timeout=100)
 (OUT/(label+'.stdout')).write_text(p.stdout);(OUT/(label+'.stderr')).write_text(p.stderr)
 results.append({'name':label,'exit':p.returncode,'seconds':round(time.monotonic()-start,3)})
 (OUT/'replay-runs.json').write_text(json.dumps(results,indent=2)+'\n')
 return p

def args(name,script=C,report=None):
 root=OUT/'replays'/name;map=root/'docs/journey'/('spacedock-review.yaml' if name=='relay' else 'qnow.yaml')
 return [NODE,script,map,'--workflow-dir',root/'docs/dev2',*(['--report',report] if report else [])]

def observe(name):
 p=run(name+'-final',args(name));d=json.loads(p.stdout);assert d['diagnostic'] is None,d['diagnostic'];return d
relay=json.loads((OUT/'relay-final.stdout').read_text()) if os.getenv('REUSE_OBSERVATION') else observe('relay');qnow=json.loads((OUT/'qnow-final.stdout').read_text()) if os.getenv('REUSE_OBSERVATION') else observe('qnow')
for name,new in [('relay',relay),('qnow',qnow)]:
 old=json.loads((OUT/(name+'-base.json')).read_text())
 assert old['diagnostic'] is None
 for part,keys in [('stories',['journey','release','story','status','requiredTasks','doneTasks','taskIds']),('releases',['release','status','acceptance'])]:
  assert [{k:r.get(k) for k in keys} for r in new[part]]==[{k:r.get(k) for k in keys} for r in old[part]],(name,part)
 for label,script in [('base',B),('candidate',C)]:
  root=OUT/'replays'/name;map=root/'docs/journey'/('spacedock-review.yaml' if name=='relay' else 'qnow.yaml')
  p=run(name+'-due-'+label,['python3','-B',ROOT/'kc-dev-flow-2/extensions/release-acceptance/release_acceptance.py','due','--workflow-dir',root/'docs/dev2','--progress',script,map]);assert p.returncode==0,p.stderr
 assert (OUT/(name+'-due-base.stdout')).read_text()==(OUT/(name+'-due-candidate.stdout')).read_text(),name
ss=relay['stories'];counts=[sum(s['members']['tasks']>0 and s['members']['tasks']==s['members']['done'] for s in ss),sum(s['members']['tasks']>s['members']['done'] for s in ss),sum(s['members']['tasks']==0 for s in ss)]
assert counts==[11,6,167],counts
agent=next(s for s in ss if s['story']=='agent-reviews-from-link');assert (agent['members']['tasks'],agent['members']['done'])==(6,5)
before=run('AC1-before',args('relay',report='inbox-home'));assert before.returncode==0,before.stdout+before.stderr
assert 'story inbox-home: 0 of 1 filed tasks done;' in before.stdout and 'release owner-account: 0 of 4' in before.stdout
set_task=run('AC1-set',['spacedock','status','--workflow-dir',OUT/'replays/relay/docs/dev2','--set','inbox-home','status=done','pr=pr-merge:999']);assert set_task.returncode==0,set_task.stderr
post=run('AC1-after',args('relay',report='inbox-home'));assert post.returncode==0,post.stdout+post.stderr
for text in ['story inbox-home: 1 of 1 filed tasks done; declared: exists','pull requests: spacedock-dev/subspace-relay#999','release owner-account: 1 of 4 stories have every filed task done; 1 in progress; 2 have no task','done: inbox-home (spacedock-dev/subspace-relay#999)','in progress: switch-any-account 0/1']:assert text in post.stdout,text
q=run('AC5-release-only',args('qnow',report='production-operations'));assert q.returncode==0,q.stdout+q.stderr
assert not any(l.startswith('story ') for l in q.stdout.splitlines())
l=run('qnow-listing',['spacedock','status','--workflow-dir',OUT/'replays/qnow/docs/dev2','--archived','--all-fields','--limit','0','--json']);assert l.returncode==0
rows=json.loads(l.stdout)['entities'];rows=[t for t in rows if t.get('journey')==qnow['journey'] and t.get('journey-release')=='r12' and not t.get('journey-story')]
assert f"release tasks with no story: {sum(t['status']=='done' for t in rows)} of {len(rows)} done" in q.stdout
short=run('AC6-short',args('relay',report='account-publish-ceiling'));assert short.returncode==0,short.stdout+short.stderr
assert len(short.stdout.strip().splitlines())<=9 and len(short.stdout.split())<=160
old=run('AC7-old-cli',args('relay',B,'inbox-home'));assert old.returncode==2
failed=run('AC7-no-spacedock',args('relay',report='inbox-home'),{**os.environ,'PATH':''});assert failed.returncode==1 and failed.stdout.startswith('journey progress not run:') and len(failed.stdout.splitlines())==1
(OUT/'progress-replay-result.json').write_text(json.dumps({'status':'passed','relay_members':counts,'agent_reviews_members':agent['members'],'release_only_tasks':len(rows),'short_report_lines':len(short.stdout.strip().splitlines()),'short_report_words':len(short.stdout.split()),'checks':['AC-1','AC-2','AC-3','AC-5','AC-6','AC-7','AC-9']},indent=2)+'\n')
print('progress replay passed')
