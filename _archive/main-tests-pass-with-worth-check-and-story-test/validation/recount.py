#!/usr/bin/env python3
import hashlib, json, os, re, sys
from pathlib import Path

root, sd, out = map(Path, sys.argv[1:4])
root=root/'kc-dev-flow-2'
sys.path.insert(0,str(root/'scripts'))
import test_pr_watch as tests
def part(text,title):
    lines=text.splitlines(keepends=True)
    start=next(i for i,line in enumerate(lines) if line.strip()==title)
    end=next((i for i in range(start+1,len(lines)) if lines[i].startswith('## ')),len(lines))
    return ''.join(lines[start:end])
w=(root/'references/sd/workflow.md').read_text();u=(sd/'mods/pr-merge.md').read_text()
texts={'workflow':w,'dev':(root/'skills/dev/SKILL.md').read_text(),'mod':(root/'references/sd/mods/kc-dev-flow-2.md').read_text(),'startup':part(u,'## Hook: startup'),'idle':part(u,'## Hook: idle'),'delivery':part(w,'## Delivery authority'),'extensions':part(w,'## Extensions'),'learn':(root/'extensions/learn/EXTENSION.md').read_text(),'gate':(sd/'skills/fo-gate-lifecycle/SKILL.md').read_text(),'present':(sd/'skills/present-gate/SKILL.md').read_text()}
counts={k:len(v.split()) for k,v in texts.items()}
outputs={}
for label,state in [('open','OPEN'),('merged','MERGED'),('archive',None),('sitting',None)]:
    f=tests.TasksTests();f.setUp()
    try:
        if state:
            f.readme('roborev');f.task('t',pr='o/r#7');code,lines=f.tasks({'pr view 7':tests.view(state)})
        elif label=='archive':
            f.readme('learn');f.archive('some-task');code,lines=f.tasks({})
        else:
            f.readme('');f.gates(*[(f't{i}','validation','awaiting-captain') for i in range(4)]);code,lines=f.tasks({})
        assert code==0,(label,lines)
        outputs[label]={'exit':code,'stdout':lines,'words':len(' '.join(lines).split())}
    finally:f.doCleanups()
total=lambda names:sum(counts[k] for k in names)
totals={'startup':total(['workflow','dev','mod','startup'])+outputs['open']['words'],'idle_open':total(['mod','idle','delivery','extensions'])+outputs['open']['words'],'idle_merged':total(['mod','idle','delivery','extensions'])+outputs['merged']['words'],'archive':total(['mod','learn'])+outputs['archive']['words'],'merge_ask':total(['delivery','extensions','gate','present'])+outputs['sitting']['words']}
data={'input_sha256':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in texts.items()},'words':counts,'outputs':outputs,'totals':totals,'spacedock_documents':str(sd)}
out.write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(totals))
