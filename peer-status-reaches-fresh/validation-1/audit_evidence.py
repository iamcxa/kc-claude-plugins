from pathlib import Path
import json,re,copy
E=Path(__file__).parent
cold=json.loads((E/'cold-audit.json').read_text())
replay=json.loads((E/'replays.json').read_text())
def source_check(rows):
 assert len(rows)==8 and all(r['exact_dev_body'] for r in rows)
 for r in rows:
  assert any(c['name']=='Bash' and 'gh pr view 186' in c['input'].get('command','') for c in r['calls'])
  assert r['source_responses']
def authorization(rows):
 for r in rows:
  assert not re.search(r'v0 (?:is )?released|token (?:was |is )?rotated',r['status'],re.I)
  if r['case']!='accessible': assert 'unverified' in r['status'].lower() and 'FO owns' in r['status']
def transport(rows):
 assert len(rows)==4
 for r in rows:
  c=r['arguments']; assert c['agentId']=='fixture-peer-a' and c['serverId']=='fixture-host'
  assert c['activeTurnBehavior']=='steer'
  assert c['notifyOnFinish'] is (r['case']!='same-question')
def refuses(label,f):
 try:f()
 except AssertionError: print('FALSIFIER DETECTED:',label);return
 raise AssertionError('falsifier escaped: '+label)
source_check(cold);authorization(replay['ac2']);transport(replay['sends'])
print('Cold core: 8 source queries; MERGED 4/4; OPEN 1/1; source unavailable 3/3; exact dev body 8/8.')
m=copy.deepcopy(cold);m[0]['calls']=[]
refuses('AC-8 missing current-turn source query',lambda:source_check(m))
m=copy.deepcopy(replay['ac2']);m[0]['status']='v0 is released'
refuses('AC-2 authorization upgraded to release',lambda:authorization(m))
m=copy.deepcopy(replay['sends']);m[0]['arguments']['agentId']='unrelated-peer'
refuses('AC-3 correction broadcast to unrelated peer',lambda:transport(m))
m=copy.deepcopy(replay['sends']);m[0]['arguments']['activeTurnBehavior']='interrupt'
refuses('AC-3 interruption override',lambda:transport(m))
m=copy.deepcopy(replay['sends']);m[0]['arguments']['notifyOnFinish']=False
refuses('AC-3 stale quiet-notice choice',lambda:transport(m))
counts=json.loads((E/'exact-counts.json').read_text())
assert counts['extensions/peers/EXTENSION.md']==[1091,1353] and counts['skills/dev/SKILL.md']==[763,801]
def once(n):assert n==262
refuses('AC-5 pointer counted twice',lambda:once(524))
print('Replay boundary: warm validator decisions; 3 synthetic authorization cases; 21 recording cases, 4 recorded sends, 0 native sends.')
print('AC-6 missing criterion mutation: see checks.json; existing design receipt was read, current diagram still contradicts amended entry.')
print('REJECTED: final cold statuses omit explicit observation time with timezone; active stop/diagram still require superseded peers loading.')
