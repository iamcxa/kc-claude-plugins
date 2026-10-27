from pathlib import Path
import json,copy
m=json.loads(Path('/tmp/peers-validation-730-merge-evidence/reading-manifest.json').read_text())
def check(x):
    c=x['candidate']['inputs'];r=x['routes']['candidate']
    peer=c['extensions/peers/EXTENSION.md']['words']
    proactive=c['extensions/paseo/EXTENSION.md']['words']
    upstream=x['upstream_paseo']['words']
    assert upstream==len(Path('/Users/kent/.agents/skills/paseo/SKILL.md').read_text().split())
    assert r['proactive_paseo']==peer+proactive+upstream
    assert r['unlisted_incoming']==r['gate_reply']==peer+upstream
    for k in ('startup_without_exchange','idle_open','idle_merged','after_archive','merge_ask'):
        assert x['routes']['base'][k]==r[k]
check(m)
for name,mutant in [('omit upstream',copy.deepcopy(m)),('omit inbound',copy.deepcopy(m))]:
    if name=='omit upstream':mutant['routes']['candidate']['proactive_paseo']-=1380
    else:mutant['routes']['candidate']['unlisted_incoming']=0
    try:check(mutant)
    except AssertionError:print(name+': REJECTED')
    else:raise AssertionError('survived')
print('Complete route sums PASS; approved ceilings independently checked by recount-independent.py.')
