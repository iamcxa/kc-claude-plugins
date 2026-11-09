import argparse, datetime, hashlib, json, os, signal, subprocess, time
from pathlib import Path

R=Path(__file__).resolve().parent
def stamp(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
p=argparse.ArgumentParser()
p.add_argument('host',choices=['codex','claude'])
p.add_argument('arm',choices=['base','candidate'])
p.add_argument('number',type=int)
p.add_argument('scratch')
a=p.parse_args()
assert len(list((R/'runs').glob('*/meta.json'))) < 16, 'hard stop 16'
assert (R/'preregistration.json').exists()
scratch=Path(a.scratch).resolve()
out=R/'runs'/f'{a.host}-{a.arm}-{a.number}'
out.mkdir(parents=True)
entity=scratch/'wf/.spacedock-state/dispatch-build-writes-the-dispatch-record.md'
before=entity.read_text()
dispatch=scratch/'dispatch.md'
prompt=f'$spacedock:ensign; then Read {dispatch} and treat its content as your assignment.'
if a.host=='codex':
    argv=['/Users/kent/.npm-global/bin/codex','exec','-m','gpt-6-astra','-c','model_reasoning_effort=xhigh','-s','workspace-write','--add-dir',str(scratch),'--json','--ephemeral','-o',str(out/'last-message.txt'),'-']
else:
    argv=['/Users/kent/.local/bin/claude','-p','--model','claude-opus-5-5','--output-format','stream-json','--verbose','--permission-mode','dontAsk','--add-dir',str(scratch),prompt]
env={**os.environ,'PATH':str(R/'bin')+os.pathsep+os.environ['PATH'],'REPLAY_GH_LOG':str(out/'gh.jsonl'),'PYTHONDONTWRITEBYTECODE':'1'}
meta={'host':a.host,'arm':a.arm,'wording':0 if a.arm=='base' else 1,'argv':argv,'cwd':str(scratch/'code'),'normal_HOME':True,'start':stamp(),'dispatch_sha256':hashlib.sha256(dispatch.read_bytes()).hexdigest(),'timeout_seconds':1800,'tokens':None}
(out/'meta.json').write_text(json.dumps(meta,indent=2)+'\n')
(out/'prompt.txt').write_text(prompt+'\n')
start=time.monotonic()
with (out/'events.jsonl').open('w') as stdout,(out/'stderr.log').open('w') as stderr:
    child=subprocess.Popen(argv,cwd=scratch/'code',env=env,stdin=subprocess.PIPE,stdout=stdout,stderr=stderr,text=True,start_new_session=True)
    try:
        child.communicate(prompt if a.host=='codex' else '',timeout=1800)
        meta['exit']=child.returncode
    except subprocess.TimeoutExpired:
        os.killpg(child.pid,signal.SIGTERM)
        try:child.wait(timeout=10)
        except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
        meta['exit']=124;meta['timeout']=True
after=entity.read_text()
meta['report_written']=after!=before and '## Stage Report: validation' in after[len(before):]
if meta['report_written']:
    (out/'report.md').write_text(after[len(before):].strip()+'\n')
for line in (out/'events.jsonl').read_text().splitlines():
    try:event=json.loads(line)
    except ValueError:continue
    if event.get('type')=='turn.completed':meta['tokens']=event.get('usage')
    if event.get('type')=='result':
        meta['tokens']={k:event.get(k) for k in ['usage','modelUsage','total_cost_usd']}
meta.update(end=stamp(),elapsed_seconds=time.monotonic()-start)
(out/'meta.json').write_text(json.dumps(meta,indent=2)+'\n')
print(json.dumps(meta))
raise SystemExit(0 if meta['exit']==0 and meta['report_written'] else 1)
