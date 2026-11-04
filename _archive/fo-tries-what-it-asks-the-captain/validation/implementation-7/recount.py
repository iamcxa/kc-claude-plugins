import ast
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

WT = Path(os.environ.get('CAPTAIN_STEPS_WORKTREE', '/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-fo-tries-what-it-asks-the-captain'))
BASE = '713d4e6ed6381e65fa6d8305e08b282ceb56a8fb'
OUT = Path(__file__).resolve().parent
def before(path):
    return subprocess.check_output(['git', '-C', str(WT), 'show', f'{BASE}:{path}'], text=True)
def now(path):
    return (WT / path).read_text()
def words(text):
    return len(text.split())
def section(text, title):
    return re.search(r'^## ' + title + r'\n(.*?)(?=^## |\Z)', text, re.M | re.S)[1]
def ask(text):
    tree = ast.parse(text)
    return next(ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'ASK' for t in node.targets))
path = 'kc-dev-flow-2/references/sd/workflow.md'
b, c = before(path), now(path)
mod = 'kc-dev-flow-2/references/sd/mods/kc-dev-flow-2.md'
assert before(mod) == now(mod)
rows = [{'moment': 'Startup and resume, workflow plus mod', 'before': words(b)+words(before(mod)), 'after': words(c)+words(now(mod))}]
assert words(b) == 5781 and words(c) == 5836 and words(c) - words(b) == 55
old = re.search(r'Before the gate, FO runs the\s+(.*?)\n  Before recommending', b, re.S)[0].rsplit('Before recommending', 1)[0]
new = re.search(r'Before the gate, FO runs the\s+(.*?)\n  Before recommending', c, re.S)[0].rsplit('Before recommending', 1)[0]
old_words, new_words = words(old), words(new)
assert (old_words, new_words) == (64, 33), (old_words, new_words)
steps_words = words('## Captain steps\n' + section(c, 'Captain steps'))
assert steps_words == 86, steps_words
rows += [{'moment': 'Validation gate passage', 'before': old_words, 'after': new_words},
         {'moment': 'Captain steps section at startup', 'before': 0, 'after': steps_words},
         {'moment': 'Steps pass line', 'before': 0, 'after': words('captain steps complete: 3 steps, 1 left to him')}]
# Recount the mandated success line with the same whitespace split.
assert rows[-1]['after'] == 9
unchanged = ['kc-dev-flow-2/scripts/pr_watch.py', mod]
assert all(before(p) == now(p) for p in unchanged)
assert ask(before('kc-dev-flow-2/scripts/delivery_gate.py')) == ask(now('kc-dev-flow-2/scripts/delivery_gate.py'))
for moment in ['Idle on open PR', 'Idle on merged PR', 'After archive', 'Merge ask']:
    rows.append({'moment': moment, 'before': 'unchanged', 'after': 'unchanged', 'evidence': 'pr_watch.py and mod byte-identical; merge ASK literal and check() byte-identical'})
def function(text, name):
    tree = ast.parse(text)
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.get_source_segment(text, node)
assert function(before('kc-dev-flow-2/scripts/delivery_gate.py'), 'check') == function(now('kc-dev-flow-2/scripts/delivery_gate.py'), 'check')
assert words(c + ' extra') - words(b) != 55
(OUT / 'word-counts.json').write_text(json.dumps({'base': BASE, 'workflow': {'before': words(b), 'after': words(c), 'delta': words(c)-words(b)}, 'mod_words': words(now(mod)), 'moments': rows, 'correction': 'The mandated success line is 9 whitespace-split words, not the design table\'s 8; no behavior or workflow budget change.', 'falsifier': 'Adding one word makes the +55 assertion false.'}, indent=2) + '\n')
print(json.dumps({'base_words': words(b), 'candidate_words': words(c), 'delta': words(c)-words(b), 'validation': [old_words, new_words], 'section': steps_words, 'pass_line': rows[3]['after']}))
