import importlib.util,json,subprocess,sys
from pathlib import Path
from datetime import timedelta
wt=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-captain-question-outside-a-gate-is-an-open-record')
scratch=Path('/tmp/dev2/kc-claude-plugins-3042bb224e995ded/captain-question-outside-a-gate-is-an-open-record/implementation-1')
state=Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state')
rows=json.loads((state/'captain-question-outside-a-gate-is-an-open-record/evidence/ideation-1/day-2026-11-13.json').read_text())
replay=scratch/'replay-state-copy'
selected={r['task'] for r in rows if r['src']=='gate'}
for pattern in ('*.md','*/index.md','_archive/*.md','_archive/*/index.md'):
 for path in replay.glob(pattern):
  slug=path.parent.name if path.name=='index.md' else path.stem
  if slug not in selected: path.unlink()

sys.path.insert(0,str(wt/'kc-dev-flow-2/scripts'))
import task_timeline as tt
# Cache actual read-only git log results at this clone's pinned HEAD; no dates or
# rows are invented. The product function still folds every as-of independently.
real_run=subprocess.run
history_cache={}
def cached_history(command,*args,**kwargs):
    cacheable=isinstance(command,list) and command[:1]==['git'] and 'log' in command and '-S' in command
    if not cacheable:return real_run(command,*args,**kwargs)
    key=tuple(command)
    if key not in history_cache:history_cache[key]=real_run(command,*args,**kwargs)
    return history_cache[key]
tt.subprocess.run=cached_history
proof=[]
for source in (r for r in rows if r['src']=='gate'):
    closed=tt.when(source['answered_at'])
    key=source['briefing']
    at=closed-timedelta(seconds=1)
    listed=tt.gate_rows(replay,at)
    matches=[r for r in listed if r['key']==key]
    if matches:
        since=tt.when(matches[0]['waiting_since'])
        assert since <= at < closed,(key,since,at,closed)
        assert len(matches)==1,key
    else:
        # Some original native resolutions were recorded less than one second after
        # first naming; check immediately at that whole-second lower bound instead.
        stamps=subprocess.check_output(['git','-C',str(replay),'log','--reverse','--format=%aI','-S',key],text=True).splitlines()
        assert stamps,key
        since=tt.when(stamps[0])
        assert since<=closed,(key,since,closed)
        matches=[r for r in tt.gate_rows(replay,since) if r['key']==key]
        assert len(matches)==1,key
    assert not [r for r in tt.gate_rows(replay,closed) if r['key']==key],key
    proof.append(dict(key=key,since=tt.iso(since),closed=source['answered_at'],wait_bound='at least'))
    print(f'{len(proof)} gate attempts checked',flush=True)
(scratch/'gate-replay.json').write_text(json.dumps(proof,indent=2))
print(f'{len(proof)} original gate attempts: one open row before closure, zero after closure, zero negative waits')
