import json, subprocess, sys
from pathlib import Path
repo, host = sys.argv[1:3]
base = '422caef5a9b115a14f8391836499520d9fba6d91'
head = '39fdbb28b411d44a323741f645c7c1d75c653be1'
paths = {'peers': 'extensions/peers/EXTENSION.md', 'paseo': 'extensions/paseo/EXTENSION.md', 'dev': 'skills/dev/SKILL.md', 'workflow': 'references/sd/workflow.md'}
def words(rev, path):
    return len(subprocess.check_output(['git', '-C', repo, 'show', rev + ':kc-dev-flow-2/' + path], text=True).split())
c = {k: [words(base, p), words(head, p)] for k, p in paths.items()}
h = Path(host).read_text()
hw = sum(len((k + h.split(k, 1)[1].split('\n## ', 1)[0]).split()) for k in ['## Connected hosts', '## Agents', '## Waiting', '## CLI semantics'])
c.update(host=hw, unlisted=[p + hw for p in c['peers']], listed=[p + x + hw for p, x in zip(c['peers'], c['paseo'])])
assert c['peers'] == [1091, 1348] and c['dev'] == [763, 801]
assert c['paseo'] == [389, 389] and c['workflow'] == [5781, 5781] and hw == 607
print(json.dumps(c, indent=2))
