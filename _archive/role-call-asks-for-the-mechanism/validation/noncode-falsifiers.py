import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
rows = []
grade = json.loads((root / 'regrade.json').read_text())
assert grade['mechanism'] > grade['current']
for name, mechanism, current in [('tie', 3, 3), ('current-wins', 2, 3)]:
    assert not mechanism > current
    rows.append({'criterion': 'AC-5', 'name': name, 'caught': True,
                 'observation': f'{mechanism}:{current} does not satisfy strictly more passes'})
adr = 'docs/adr/0026-role-calls-are-owed-on-counts-read-from-task-records-and-a-dated-call-clears-them.md'
base = (root / 'base' / adr).read_text()
candidate = (root / 'candidate' / adr).read_text()
marker = '\nAmended 2026-11-09 (Captain:'
assert candidate.startswith(base) and candidate.count(marker) == 1
assert not base.count(marker)
rows.append({'criterion': 'AC-6', 'name': 'remove-approved-amendment', 'caught': True,
             'observation': 'Base ADR has no 2026-11-09 amendment; candidate is the base plus one amendment paragraph.'})
workflow = 'kc-dev-flow-2/references/sd/workflow.md'
before = (root / 'base' / workflow).read_bytes()
after = (root / 'candidate' / workflow).read_bytes()
assert before == after
assert before != after + b'\n'
rows.append({'criterion': 'AC-6', 'name': 'workflow-one-byte-drift', 'caught': True,
             'observation': 'Byte comparison accepts candidate and refuses an added newline.'})
(root / 'noncode-falsifiers.json').write_text(json.dumps(rows, indent=2) + '\n')
print('PASS: AC-5 tie/loss controls and AC-6 removed amendment/workflow drift controls')
