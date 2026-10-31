from pathlib import Path
import json,re,copy
E=Path(__file__).parent
cold=json.loads((E/'cold-audit.json').read_text())
replay=json.loads((E/'replays.json').read_text())
def source(rows):
 assert len(rows)==8 and all(r['exact_dev_body'] and r['source_queries'] for r in rows)
def citation(rows):
 return [r['run'] for r in rows if r['run'].startswith(('g-absent','g-notice','g-delayed')) and not r['source_revision_or_link']]
def authorization(rows):
 for r in rows:
  assert not re.search(r'v0 (?:is )?released|token (?:was |is )?rotated',r['status'],re.I)
  if r['case']!='accessible':assert 'unverified' in r['status'].lower() and 'FO owns' in r['status']
def transport(rows):
 assert len(rows)==4
 for r in rows:
  c=r['arguments']
  assert c['agentId']=='fixture-peer-a' and c['serverId']=='fixture-host'
  assert c['activeTurnBehavior']=='steer' and c['notifyOnFinish'] is (r['case']!='same-question')
def refuses(label,f):
 try:f()
 except AssertionError:print('FALSIFIER DETECTED:',label);return
 raise AssertionError('falsifier escaped: '+label)
source(cold);authorization(replay['ac2']);transport(replay['sends'])
print('Cold core: 8/8 exact dev; 8/8 source queries; MERGED 4/4 cleared; OPEN 1/1 retained; unavailable 3/3 FO-owned (independently read outputs).')
assert citation(cold)==['g-absent1','g-absent2']
print('AC-9 SOURCE REVISION/LINK MISSING: '+', '.join(citation(cold)))
m=copy.deepcopy(cold);m[0]['source_queries']=[]
refuses('AC-9 missing current-turn source query',lambda:source(m))
m=copy.deepcopy(cold)
for r in m:r['source_revision_or_link']=True
assert not citation(m)
print('AC-9 citation control: source-reference repair in audit input clears the citation gap; no product repair.')
m=copy.deepcopy(replay['ac2']);m[0]['status']='v0 is released'
refuses('AC-2 authorization upgraded to delivery',lambda:authorization(m))
for label,key,value in [('unrelated recipient','agentId','unrelated-peer'),('interrupt override','activeTurnBehavior','interrupt'),('quiet notice','notifyOnFinish',False)]:
 m=copy.deepcopy(replay['sends']);m[0]['arguments'][key]=value
 refuses('AC-3 '+label,lambda:transport(m))
counts=json.loads((E/'recount.log').read_text())
def count(c):assert c['peers']==[1091,1348] and c['dev']==[763,801] and c['workflow']==[5781,5781]
count(counts)
m=copy.deepcopy(counts);m['peers'][1]+=257
refuses('AC-5 duplicated peer addition',lambda:count(m))
for name in ['base','head']:
 d=json.loads((E/('common-'+name+'-anchored.log')).read_text())
 assert list(d['common-totals'].values())==[442,672,1021,371,776]
exercise=json.loads((E/'exercise-checks.json').read_text())
assert exercise['missing-criteria']['exit']==1
print('AC-6 actual checker: missing-criteria mutation refused (exit 1).')
print('AC-4 not run: no post-delivery natural adopted event. Its real-use falsifier is deferred with the event, not simulated as acceptance.')
print('Replay limits: warm validator; 3 synthetic original-source cases; 21 recording cases, 4 intended calls, 0 native sends.')
print('REJECTED at 39fdbb28b411d44a323741f645c7c1d75c653be1: two MERGED statuses omit the retained source revision/link.')
