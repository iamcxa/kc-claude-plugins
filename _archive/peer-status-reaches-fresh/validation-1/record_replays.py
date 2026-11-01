from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
E=Path(__file__).parent
now=datetime.now(timezone.utc).isoformat()
# These are this validator's warm policy decisions, not a second agent or a product interceptor.
ac2=[]
for case,filename,status in [
 ('accessible','accessible-original.txt','The authorization hold is cleared by the original question and answer. Token rotation and v0 release remain unverified; FO will check their own records. No Captain action is currently assigned.'),
 ('unavailable','unavailable-original.txt','The old token authorization wait is unverified because the original question and answer are unavailable. FO owns the source check; no Captain action or release completion is assigned.'),
 ('unrelated','unrelated-original.txt','Dashboard completion does not settle the token authorization. The old wait is unverified; FO owns the original-source check. No Captain action or release completion is assigned.')]:
 source=E/'ac2'/filename
 ac2.append(dict(case=case,source=str(source),source_bytes=source.read_text(),observed_at=now,status=status,source_words=len(source.read_text().split()),status_words=len(status.split())))
# Recording endpoint only: it persists requested sends without contacting a host.
sends=[]
def send(case,peer,reply=False,transition='merged'):
 call=dict(serverId='fixture-host',agentId=peer,activeTurnBehavior='steer',notifyOnFinish=not reply,prompt=f'{transition} correction; source fixture-original; observed {now}; exchange fixture-q1; no acknowledgement requested.')
 sends.append(dict(case=case,tool='send_agent_prompt',arguments=call));return call
cases=[]
def record(case,input,decision,**kw):cases.append(dict(case=case,input=input,decision=decision,**kw))
for t in ['merged','released','unblocked']:
 record(t,'Confirmed Paseo, paseo unlisted; previously involved idle peer A and unrelated idle peer B. Verified original transition.','Send once to A only; keep B out; no worker procedure activated.',calls=[send(t,'fixture-peer-a',transition=t)])
record('same-question','Confirmed running asker A requests correction to fixture-q1; steering available.','Requested reply may reach the running asker; callbacks disabled.',calls=[send('same-question','fixture-peer-a',reply=True)])
record('running-new','A is running; new notice; independent work remains.','Defer; first deferral 10:00 UTC, deadline 10:05 UTC. No send.',calls=[])
record('unknown-new','A status unknown; no independent work remains.','Stop waiting now; persist unsent notice/status unknown. No send.',calls=[])
record('still-busy','Natural independent-work boundary 10:03 UTC; A still running.','One recheck ends deferral; save unsent notice; no poll or automatic retry.',calls=[])
record('expired','First deferral 10:00 UTC; resumed at 10:06 UTC.','Deadline expired; preserve original deadline; save unsent notice.',calls=[])
record('steer-unavailable','Requested reply; steering known unavailable.','Defer even reply; no interrupt override.',calls=[])
record('held-go-live','Confirmed idle A; proposed correction would authorize held go-live.','Record factual unblock only; do not send a go-live instruction. Approval hold remains; no send.',calls=[])
record('uncertain-send','Prior requested correction returned queued receipt; no recipient turn or callback.','Persist uncertain delivery; receipt does not establish delivery.',calls=[])
record('attended-resume','Same uncertain notice; recipient evidence remains unavailable at attended resume.','Inspect unresolved exchange evidence; retain uncertain reason, report gap to FO, no automatic resend.',calls=[])
record('duplicate','Same source revision and fixture-q1 already consumed.','No second action; no receipt acknowledgement.',calls=[])
record('older','Older OPEN observation arrives after source verified MERGED.','Do not restore stale merge action; no acknowledgement.',calls=[])
record('conflict','Newer timestamp says OPEN, source fixture-original currently says MERGED.','Read source fixture-original now; keep merge action cleared; timestamp is not truth.',source_query=True,calls=[])
record('source-down','Conflicting observation, original source unreachable.','Mark unverified; FO owns check, no Captain action.',source_query=True,calls=[])
record('bound-briefing','Source correction arrives while briefing digest is bound.','Append existing peer-exchanges note at authorized write; briefing bytes preserved.',calls=[])
record('finish-only','Information-only notice finishes with no action.','No new acknowledgement or Captain turn; finish does not prove understanding.',calls=[])
record('real-error','Notified notice callback reports receiver failure.','Report material error to FO; preserve failed evidence, no automatic resend.',calls=[])
record('permission-hold','Callback reports another agent permission request.','Report hold to FO; never call respond_to_permission.',calls=[])
record('worker-finish','Our dispatched worker sends its completion signal.','Retain worker completion contract; peer no-action suppression does not swallow it.',calls=[])
result=dict(candidate='1df246fa992ce0864348c2ffe67d93e80ad0a4b8',observed_at=now,boundary='Warm validator follows exact policy; synthetic declared sources and recording endpoint only; no fresh FO, real send, historical authentication, host delivery or permission response.',ac2=ac2,ac3=cases,sends=sends)
(E/'replays.json').write_text(json.dumps(result,indent=2))
(E/'transport.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in sends))
for r in ac2:print('AC-2',r['case'],r['status'])
for r in cases:print('AC-3',r['case'],r['decision'])
print('Recorded sends:',len(sends),'real sends: 0')
