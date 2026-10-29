from pathlib import Path
import re,sys,json,subprocess
repo=Path(sys.argv[1]); p=repo/'kc-dev-flow-2'; sd=Path('/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3')
sys.path.insert(0,str(p/'scripts'))
import test_pr_watch as t
def section(text,heading):
    m=re.search(r'^## '+re.escape(heading)+r'\n',text,re.M); e=re.search(r'^## ',text[m.end():],re.M)
    return text[m.start():m.end()+e.start() if e else len(text)]
def read(path): return path.read_text()
parts={'workflow':read(p/'references/sd/workflow.md'),'dev':read(p/'skills/dev/SKILL.md'),'mod':read(p/'references/sd/mods/kc-dev-flow-2.md'),'paseo':read(p/'extensions/paseo/EXTENSION.md'),'learn':read(p/'extensions/learn/EXTENSION.md'),'startup':section(read(sd/'mods/pr-merge.md'),'Hook: startup'),'idle':section(read(sd/'mods/pr-merge.md'),'Hook: idle'),'delivery':section(read(p/'references/sd/workflow.md'),'Delivery authority'),'extensions':section(read(p/'references/sd/workflow.md'),'Extensions'),'lifecycle':read(sd/'skills/fo-gate-lifecycle/SKILL.md'),'present':read(sd/'skills/present-gate/SKILL.md')}
outputs={}
for kind in ('open','merged','archive'):
    test=t.TasksTests(); test.setUp()
    try:
        if kind=='archive': test.readme('learn'); test.archive('some-task'); code,lines=test.tasks({})
        else:
            test.readme('roborev'); test.task('some-task',pr='o/r#7'); code,lines=test.tasks({'pr view 7':t.view('MERGED' if kind=='merged' else 'OPEN')})
        assert code==0,(code,lines)
        outputs[kind]='\n'.join(lines)
    finally: test.doCleanups()
outputs['four-gates']='\n'.join(t.watch.sittings([{'readiness':'awaiting-captain','current':'validation','slug':x} for x in ('a','b','c','d')]))
counts={k:len(v.split()) for k,v in parts.items()}; out={k:len(v.split()) for k,v in outputs.items()}
rows={'startup':sum(counts[k] for k in ('workflow','dev','mod','startup','paseo'))+out['open'],'idle/open':sum(counts[k] for k in ('mod','idle','delivery','extensions','paseo'))+out['open'],'idle/merged':sum(counts[k] for k in ('mod','idle','delivery','extensions','paseo'))+out['merged'],'archive':sum(counts[k] for k in ('mod','learn','paseo'))+out['archive'],'merge':sum(counts[k] for k in ('delivery','extensions','lifecycle','present','paseo'))+out['four-gates']}
print(json.dumps({'parts':counts,'outputs':out,'rows':rows},indent=2))
assert list(rows.values())==[7521,1424,1395,895,2970]
