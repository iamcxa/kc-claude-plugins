import ast
import difflib
import json
from pathlib import Path
import sys

wt, out, inputs = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve()
sys.path.insert(0, str(wt / 'kc-dev-flow-2/scripts'))
import laws_check as lc
from design_surfaces import move_defects

tree = ast.parse((out / 'investigate.py').read_text())
model = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'proposed_delta')
scope = {}
exec(compile(ast.Module(body=[model], type_ignores=[]), '<analysis-only proposal>', 'exec'), scope)
delta = scope['proposed_delta']
repos = {row['name']: row for row in json.loads(inputs.read_text())}
rows = []
for name, short in [('dev2', 'a113aa3e9'), ('dev2', '7326e2a11'), ('dev2', 'bf8c73be9'),
                    ('qnow', '3a384063e'), ('qnow', '4ad692922'), ('qnow', '4993b5b60'), ('relay', '06cadae76')]:
    repo = repos[name]
    before, after = lc.commit_of(repo['state'], short + '^'), lc.commit_of(repo['state'], short)
    ctx = lc.Context(repo['state'], before[:12] + '..' + after[:12], lc.walk(repo['state'], before, after), repo['readme'])
    count, heads, violations = lc.judge(ctx, 'L4', lc.LAWS['L4'])
    assert count == 1, (short, heads, violations)
    pairs = []
    for commit, changes in ctx.commits:
        for old, new in lc.amendment_pairs(changes):
            previous = move_defects(lc.amendment_blob(ctx, before, old).split('\n'))
            current = move_defects(lc.amendment_blob(ctx, after, new).split('\n'))
            observed = [defect for defect in current if defect not in set(previous)]
            proposed = delta(previous, current)
            assert proposed == observed, (short, previous, current, observed, proposed)
            if observed:
                assert previous == [], (short, previous)
                pairs.append({'old_path': old, 'new_path': new, 'previous_defects': previous,
                              'current_added': observed, 'proposed_added': proposed})
    assert len(pairs) == 1, (short, pairs)
    rows.append({'repository': name, 'before': before, 'after': after, 'heads': heads,
                 'violations': violations, 'event_tasks': pairs, 'proposed_named_event_unchanged': True})
(out / 'seven-events.json').write_text(json.dumps(rows, indent=2) + '\n')
(out / 'seven-events.log').write_text('\n\n'.join(row['repository'] + '\n' + '\n'.join(row['heads'] + row['violations']) for row in rows) + '\n')

source = (wt / 'kc-dev-flow-2/scripts/laws_check.py').read_text()
old = '            previous = set(move_defects(before))\n            added = [defect for defect in move_defects(after) if defect not in previous]\n'
new = '''            previous = set(move_defects(before))
            added = []
            for defect in move_defects(after):
                if defect[0] == "reused":
                    prior_ids = {ident for old in previous if old[:2] == defect[:2] for ident in old[2]}
                    fresh = tuple(ident for ident in defect[2] if ident not in prior_ids)
                    if fresh:
                        added.append((*defect[:2], fresh))
                elif defect not in previous:
                    added.append(defect)
'''
assert source.count(old) == 1
patch = ''.join(difflib.unified_diff(source.splitlines(keepends=True), source.replace(old, new).splitlines(keepends=True),
                                     fromfile='a/kc-dev-flow-2/scripts/laws_check.py', tofile='b/kc-dev-flow-2/scripts/laws_check.py'))
(out / 'proposed-runtime.diff').write_text(patch)
assert source == (wt / 'kc-dev-flow-2/scripts/laws_check.py').read_text()
print('All seven named first-parent events are unchanged by the analysis-only per-id delta; no product patch applied')
