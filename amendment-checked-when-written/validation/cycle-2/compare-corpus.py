import json
from pathlib import Path
import sys

out, prior = Path(__file__).resolve().parent, Path(sys.argv[1]).resolve()
old_inputs = {row['name']: row for row in json.loads((prior / 'corpus-inputs.json').read_text())}
rows = []
for current in json.loads((out / 'corpus-inputs.json').read_text()):
    name = current['name']
    old = old_inputs[name]
    assert old['candidate'] == '72216e2e947e962737a17c6e61ef3800f9d639c4'
    assert {k: v for k, v in current.items() if k != 'candidate'} == {k: v for k, v in old.items() if k != 'candidate'}
    lines = lambda p: [s for s in p.read_text().splitlines() if s.startswith(('L4 ', 'violation: L4 '))]
    expected, actual = lines(prior / f'corpus-{name}.log'), lines(out / f'corpus-{name}.log')
    assert expected == actual, (name, expected, actual)
    rows.append({'name': name, 'candidate': current['candidate'], 'previous_candidate': old['candidate'],
                 'before': current['before'], 'after': current['after'], 'same_L4_lines': True, 'L4_lines': actual})
(out / 'corpus-comparison.json').write_text(json.dumps(rows, indent=2) + '\n')
print('All seven event commits, headlines and grouped diagnostics are unchanged at the same three history ranges.')
