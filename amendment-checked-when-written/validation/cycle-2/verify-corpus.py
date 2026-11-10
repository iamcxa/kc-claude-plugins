from pathlib import Path
import json
import re

out = Path(__file__).resolve().parent
expected = {'a113aa3e9', '7326e2a11', 'bf8c73be9', '3a384063e', '4ad692922', '4993b5b60', '06cadae76'}
rows, actual, total = [], set(), 0
for repo in json.loads((out / 'corpus-inputs.json').read_text()):
    name = repo['name']
    text = (out / f'corpus-{name}.log').read_text()
    result = json.loads((out / f'corpus-{name}-exit.json').read_text())
    heads = [s for s in text.splitlines() if s.startswith('L4 ')]
    assert len(heads) == 1 and 'cannot judge' not in heads[0], heads
    match = re.fullmatch(r'L4 amendment-moves-use-fresh-ids: (\d+) events judged in ([0-9a-f.]+), (\d+) violated', heads[0])
    assert match and match[1] == match[3], heads
    count = int(match[1])
    assert count == {'dev2': 3, 'qnow': 3, 'relay': 1}[name], heads
    violations = [s for s in text.splitlines() if s.startswith('violation: L4 ')]
    commits = {re.search(r'commit=([0-9a-f]{12})', s)[1][:9] for s in violations}
    assert len(commits) == count, violations
    actual.update(commits)
    total += count
    assert result['exit'] == 2 and 'L3 amendment-append-only: cannot judge' in text, result
    rows.append({**repo, 'CLI_exit': result['exit'], 'L4_events': count, 'heads': heads, 'violations': violations})
assert total == 7 and actual == expected, {'total': total, 'missing': sorted(expected - actual), 'extra': sorted(actual - expected)}
(out / 'corpus-reconciliation.json').write_text(json.dumps(rows, indent=2) + '\n')
print('PASS: seven expected events, 3/3/1, no extra event; complete CLI exits 2 on existing L3 history debt')
