import json,pathlib,subprocess,sys,datetime
root=pathlib.Path(__file__).resolve().parent
state=pathlib.Path('/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state')
source=state/'captain-question-outside-a-gate-is-an-open-record/evidence/implementation-1/gate-replay.json'
fixtures=json.loads(source.read_text())
sys.path.insert(0,str(root/'candidate/kc-dev-flow-2/scripts'))
import task_timeline as tt
real_run=subprocess.run
head=real_run(['git','-C',str(state),'rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip()
paths=real_run(['git','-C',str(state),'ls-tree','-r','--name-only',head],capture_output=True,text=True,check=True).stdout.splitlines()
export=root/'gate-state';export.mkdir(exist_ok=True)
slugs={f['key'].split(':')[1] for f in fixtures}
for path in paths:
    parts=path.split('/')
    slug=(parts[1] if parts[0]=='_archive' else parts[0]).removesuffix('.md')
    if slug not in slugs or not (path.endswith('.md') and len(parts)<=3 or path.endswith('index.json') and '/review/' in path):continue
    dest=export/path;dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(real_run(['git','-C',str(state),'show',head+':'+path],capture_output=True,text=True,check=True).stdout)
cache={}
def cached(cmd,**kwargs):
    if cmd[:3]==['git','-C',str(export)] and 'log' in cmd:
        replaced=['git','-C',str(state),*cmd[3:],head]
        key=tuple(replaced)
        if key not in cache:cache[key]=real_run(replaced,**kwargs)
        return cache[key]
    return real_run(cmd,**kwargs)
tt.subprocess.run=cached
results=[]
for f in fixtures:
    key=f['key']
    run=cached(['git','-C',str(export),'log','--reverse','--format=%aI','-S',key],capture_output=True,text=True,check=True)
    since=tt.when(run.stdout.splitlines()[0]);closed=tt.when(f['closed'])
    clock=since+(closed-since)/2
    before=[r for r in tt.open_rows(export,clock,gates=True) if r['key']==key]
    at_close=[r for r in tt.open_rows(export,closed,gates=True) if r['key']==key]
    pre=[r for r in tt.open_rows(export,since-datetime.timedelta(seconds=1),gates=True) if r['key']==key]
    ok=len(before)==1 and not at_close and not pre and before[0]['waiting_bound']=='at least' and before[0]['waiting_min']>=0 and tt.when(before[0]['waiting_since'])<=closed
    results.append(dict(key=key,since=tt.iso(since),closed=f['closed'],before_count=len(before),at_close_count=len(at_close),pre_count=len(pre),passed=ok))
result=dict(state_head=head,attempts=len(results),read_only_log_cache=len(cache),results=results)
(root/'gate-replay.json').write_text(json.dumps(result,indent=2)+'\n')
print('gate attempts:',len(results),'passed:',sum(r['passed'] for r in results),'state:',head)
assert all(r['passed'] for r in results)
