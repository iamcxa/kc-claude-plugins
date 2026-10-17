import json,glob,sys,os,re
D='/Users/kent/.claude/projects/-Users-kent-conductor-workspaces-kc-claude-plugins-colombo/5c030106-8d82-4542-855e-1498b2563c69/subagents/'
tags=[f'psvg-{p}{m}-{k}' for p in ('','b-') for m in('sonnet','opus','fable') for k in('relay-1','relay-2','control')]
out={}
for f in glob.glob(D+'agent-*.jsonl'):
    try: head=open(f).read(4000)
    except: continue
    m=re.search(r'RUN_TAG: (psvg-(?:b-)?[a-z]+-[a-z]+(?:-\d)?)',head)
    if m: out.setdefault(m.group(1),f)
os.makedirs('/tmp/psvg-tools/out',exist_ok=True)
for t in tags:
    f=out.get(t)
    if not f: print(t,'no transcript'); continue
    rows=[json.loads(l) for l in open(f)]
    a=[d for d in rows if d.get('type')=='assistant' and d['message'].get('usage')]
    hb=[x['input'].get('message','') for d in a for x in d['message']['content'] if isinstance(x,dict) and x.get('type')=='tool_use' and x['name']=='SubagentHandback']
    done=bool(hb) or (bool(a) and a[-1]['message'].get('stop_reason') in('end_turn','stop_sequence','refusal'))
    models={d['message'].get('model') for d in a}
    u=lambda k:sum(d['message']['usage'].get(k,0) for d in a)
    ts=[d['timestamp'] for d in rows if d.get('timestamp')]
    from datetime import datetime
    p=lambda s:datetime.fromisoformat(s.replace('Z','+00:00'))
    dur=(p(ts[-1])-p(ts[0])).total_seconds()
    last=''
    for d in a:
        c=d['message']['content']
        tx=''.join(x.get('text','') for x in c if isinstance(x,dict) and x.get('type')=='text')
        if tx.strip(): last=tx
    if hb: last=hb[-1]
    stops=[d['message'].get('stop_reason') for d in a][-3:]
    open(f'/tmp/psvg-tools/out/{t}.txt','w').write(last)
    tools=sum(1 for d in a for x in d['message']['content'] if isinstance(x,dict) and x.get('type')=='tool_use')
    print(t,'done' if done else 'RUNNING',models,'req',len(a),'tools',tools,'in',u('input_tokens'),'cc',u('cache_creation_input_tokens'),'cr',u('cache_read_input_tokens'),'out',u('output_tokens'),'sec',round(dur),'stop',stops,'lastlen',len(last),os.path.basename(f))
