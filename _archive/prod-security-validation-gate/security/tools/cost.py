import json,glob,re
D='/Users/kent/.claude/projects/-Users-kent-conductor-workspaces-kc-claude-plugins-colombo/5c030106-8d82-4542-855e-1498b2563c69/subagents/'
P={'claude-sonnet-5-5':(2,10),'claude-opus-5-5':(4,20),'claude-fable-5-1':(10,50)}
HARN={'b-sonnet-relay-1':(92488,138.5),'b-sonnet-relay-2':(103680,133.4),'b-sonnet-control':(43265,19.5),'b-opus-relay-1':(102320,249.1),'b-fable-relay-1':(137642,358.7),'sonnet-relay-1':(56380,103.5),'sonnet-relay-2':(55949,107.5),'sonnet-control':(47442,57.3),'opus-relay-1':(74877,313.8),'opus-relay-2':(65963,267.0),'opus-control':(63601,256.8),'fable-relay-1':(82939,367.5),'fable-relay-2':(81175,293.4),'fable-control':(64374,269.2)}
seen={}
for f in glob.glob(D+'agent-*.jsonl'):
    m=re.search(r'RUN_TAG: psvg-((?:b-)?[a-z]+-[a-z]+(?:-\d)?)',open(f).read(4000))
    if m: seen[m.group(1)]=f
tot=0
for t in ['b-sonnet-relay-1','b-sonnet-relay-2','b-sonnet-control','b-opus-relay-1','b-fable-relay-1','sonnet-relay-1','sonnet-relay-2','sonnet-control','opus-relay-1','opus-relay-2','opus-control','fable-relay-1','fable-relay-2','fable-control']:
    rows=[json.loads(l) for l in open(seen[t])]
    a=[d for d in rows if d.get('type')=='assistant' and d['message'].get('usage')]
    mdl=a[0]['message']['model']; pi,po=P[mdl]
    fi=sum(d['message']['usage'].get('input_tokens',0) for d in a)
    cc=sum(d['message']['usage'].get('cache_creation_input_tokens',0) for d in a)
    cr=sum(d['message']['usage'].get('cache_read_input_tokens',0) for d in a)
    rec=sum(d['message']['usage'].get('output_tokens',0) for d in a)
    chars=0
    for d in a:
        for x in d['message']['content']:
            if x.get('type')=='text': chars+=len(x['text'])
            elif x.get('type')=='tool_use': chars+=len(json.dumps(x['input']))
            elif x.get('type')=='thinking': chars+=len(x.get('thinking',''))
    est_out=chars/3.5
    ub=((fi+cc+cr)*pi+est_out*po)/1e6
    hl=HARN[t][0]
    ass=((fi*pi+cc*1.25*pi+cr*0.1*pi)/1e6+est_out*po/1e6)
    print(f"{t:18} ASSUMED-cache-mult ${ass:.2f} " ,end='')
    print(f"{t:15} req {len(a):2} fresh {fi:5} cache_w {cc:7} cache_r {cr:8} out_rec {rec:5} out_est~{int(est_out):5} harness_tot {hl} dur {HARN[t][1]:.0f}s  list-price upper bound ${ub:.2f}  ; harness-total-as-tokens@input ${hl*pi/1e6:.3f}")
