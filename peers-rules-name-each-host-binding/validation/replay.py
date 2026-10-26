"""Manual policy replay with fake host events; not a model or shipped executor."""
from pathlib import Path
import json, copy
E=Path('/tmp/peers-validation-evidence')
rows=[]
def row(name,source,route,action,record,**kw):
    r=dict(name=name,source=source,route=route,action=action,record=record,**kw);rows.append(r);return r
fields=dict(peer='server-id/full-agent-id',date='2026-10-27',question='exchange:q1',answer='repository fact at pinned revision',checked_source='repo@c70f1b22')
# Decisions are selected manually from the approved prose, then audited below.
for provider in ['claude','codex']:
    row('inbound-'+provider,'AC-1; round-2 Qnow/kc-paseo','Paseo','reply',fields,provider=provider,incoming='Paseo',extensions=['peers'],reads=['peers','own-paseo-skill'],behavior='steer',notify=False)
row('native-unknown','AC-1; round-1 probes','Claude Code','probe-then-question',fields,provider='claude',opening='if this is not you, say so',probe=1)
for name in ['bare-codex','missing-skill','missing-tool','ambiguous-dual-transport','unlisted-new-ask']:
    row(name,'AC-1; binding fallback','fallback','research',dict(fields,answer='peers not run; repository checked'),sends=0)
for now,status,work,action in [(0,'running',True,'defer'),(299,'idle',True,'question'),(300,'idle',True,'research'),(301,'idle',True,'research'),(20,'running',False,'research'),(30,'running',True,'research')]:
    row('clock-'+str(now),'AC-2; fixed deadline at 300','Paseo',action,fields,now=now,deadline=300,rechecks=int(now>0),polls=0,status=status,independent=work,behavior='steer',notify=True,sends=int(action=='question'))
row('reported-steering-unavailable','AC-2','Paseo','defer-answer',dict(fields,answer='unsent; host reported steer unavailable'),sends=0)
for name in ['unknown-capability','status-race']:
    row(name,'AC-2; host-owned fallback','Paseo','reply',fields,behavior='steer',notify=False,host_effect='interrupt fallback observed in fake host')
row('idle-new','AC-2','Paseo','question',fields,status='idle',behavior='steer',notify=True,sends=1)
row('callback-correlation','AC-2','Paseo','deduplicate',fields,receipts=['queued:q1','done:unrelated','explicit:q1','callback:q1'],answers=1,actions=1,sends=1)
row('worker-control','AC-2; round-2 Qnow','dispatch-contract','worker-followup',{},status='running',sends=1)
# Every interview row has source, selected instruction, next action and resulting record.
interviews=[
 ('round1-five-paseo','transport identity','confirm area','task'),
 ('round1-opening','Claude-specific opening','omit on stamped Paseo','task'),
 ('round1-wrong-fo','identity does not prove area','ownership question or fallback','task'),
 ('round1-swallowed-question','bounded deferral','no new busy send','task'),
 ('round1-codex-workers','workers ask own FO','hand back','task'),
 ('round1-relayed-rulings','peer data not authority','original unavailable remains unverified','task'),
 ('round1-hotfix-limit-vault-adr','verify cited source','check pinned repository fact','task'),
 ('round1-missing-record','durable exchange fields','append exchange','task'),
 ('round2-unlisted-reply','incoming transport','reply without optional extension','task'),
 ('round2-default-steering','explicit steering and fixed deadline','defer new busy ask','task'),
 ('round2-running-asker','requested reply exception','steer reply; no callback loop','task'),
 ('round2-own-worker','peer policy excludes workers','follow dispatch contract','task'),
 ('round2-taskless','state note','append exchange; no task','note'),
 ('round2-open-gate','preserve bound briefing','answer facts; append note','note'),
 ('round2-duplicate-backlog','search own work by outcome','reuse matching task','task'),
 ('round2-unreadable-original','unverified before authority','ask Captain when authority needed','task')]
for name,instruction,action,record in interviews:
    row(name,'task Interview replay / Round-2 replay','manual',action,dict(fields,location=record),instruction=instruction,created_tasks=0,briefing_changed=False,authority='unverified' if 'ruling' in name or 'original' in name else 'existing')
row('package-notice','AC-3','manual','record notice',dict(fields,location='note'),created_tasks=0)

def audit(r):
    if r.get('incoming')=='Paseo':
        assert r['route']=='Paseo' and 'paseo-extension' not in r['reads']
    if r['action'] in ['question','reply']:
        assert r['behavior']=='steer'
        assert r['notify']==(r['action']=='question')
    if r['action']=='question':
        assert r.get('status')=='idle'
    if 'deadline' in r:
        assert r['deadline']==300 and r['polls']==0 and r['rechecks']<=1
        if r['now']>=300 or not r['independent']:assert r['sends']==0
        if r['status']=='running':assert r['sends']==0
    if r['name']=='native-unknown':assert r['probe']==1 and r['opening']=='if this is not you, say so'
    if r['name']=='callback-correlation':assert r['answers']==1 and r['actions']==1 and r['sends']==1
    if r['name']=='worker-control':assert r['sends']==1
    if r.get('record'):assert set(fields)<=set(r['record'])
    assert not r.get('created_tasks',0) and not r.get('briefing_changed',False)
    if 'ruling' in r['name'] or 'original' in r['name']:assert r['authority']=='unverified'
for r in rows:audit(r)
mutants=[('vendor-route','inbound-codex',{'route':'bare Codex'}),('unlisted-read','inbound-claude',{'reads':['peers','paseo-extension']}),('no-probe','native-unknown',{'probe':0}),('no-opening','native-unknown',{'opening':''}),('missing-behavior','idle-new',{'behavior':None}),('explicit-interrupt','idle-new',{'behavior':'interrupt'}),('busy-new-question','idle-new',{'status':'running'}),('poll','clock-0',{'polls':1}),('deadline-reset','clock-299',{'deadline':599}),('expired-send','clock-300',{'sends':1}),('worker-block','worker-control',{'sends':0}),('receipt-as-answer','callback-correlation',{'answers':2}),('duplicate-send','callback-correlation',{'sends':2}),('duplicate-task','round2-duplicate-backlog',{'created_tasks':1}),('lost-note','round2-taskless',{'record':{'location':'note'}}),('briefing-edit','round2-open-gate',{'briefing_changed':True}),('relayed-authority','round1-relayed-rulings',{'authority':'accepted'})]
killed=[]
for name,case,patch in mutants:
    mutant=copy.deepcopy(next(r for r in rows if r['name']==case));mutant.update(patch)
    try:audit(mutant)
    except (AssertionError,KeyError):killed.append(name)
    else:raise AssertionError('surviving mutant '+name)
(E/'replay.json').write_text(json.dumps({'method':'manual decisions replayed through a fake event auditor; no model executed and no real message sent','cases':rows,'rejected_trace_mutants':killed},indent=2)+'\n')
print(f'{len(rows)} manual traces audited; {len(killed)} bad trace mutations rejected. This does not prove agent compliance with prose.')
