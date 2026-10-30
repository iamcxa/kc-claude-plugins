import json, subprocess, sys
from pathlib import Path
repo, task, sibling, host = sys.argv[1:5]
base = 'a6612948936a4f075625147b21aabd3b10b19eee'
t, b = Path(task).read_text(), Path(sibling).read_text()
def source(name):
    return subprocess.check_output(['git', '-C', repo, 'show', base + ':kc-dev-flow-2/extensions/' + name + '/EXTENSION.md'], text=True)
def block(text, marker):
    part = text.split('<!-- ' + marker + '-start -->', 1)[1].split('<!-- ' + marker + '-end -->', 1)[0]
    return part.split('```markdown\n', 1)[1].rsplit('```', 1)[0]
p, x = source('peers'), source('paseo')
added = block(t, 'candidate-fresh-peers')
p_s = p.split('## Paseo binding', 1)[0] + block(b, 'candidate-peers') + '\n## Other host binding' + p.split('## Other host binding', 1)[1]
x_s = block(b, 'candidate-paseo') + '\n## Codex workers through Paseo' + x.split('## Codex workers through Paseo', 1)[1]
p_only = p.replace('## Claude Code binding', added + '\n## Claude Code binding', 1)
p_all = p_s.replace('## Claude Code binding', added + '\n## Claude Code binding', 1)
h = Path(host).read_text(); w = lambda z: len(z.split())
hw = sum(w(k + h.split(k, 1)[1].split('\n## ', 1)[0]) for k in ['## Connected hosts', '## Agents', '## Waiting', '## CLI semantics'])
assert '<!-- candidate-fresh-paseo-start -->' not in t.split('## Stage Report:', 1)[0].splitlines()
print(json.dumps({'peers': [w(p),w(p_only),w(p_s),w(p_all)], 'paseo': [w(x),w(x),w(x_s)], 'host': hw, 'added': w(added), 'unlisted': [w(p)+hw,w(p_s)+hw,w(p_all)+hw], 'listed': [w(p+x)+hw,w(p_s+x_s)+hw,w(p_all+x_s)+hw]}, indent=2))
