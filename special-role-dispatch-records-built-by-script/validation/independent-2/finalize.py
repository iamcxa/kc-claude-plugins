import json, re, subprocess
from pathlib import Path

home = Path(__file__).resolve().parent
out = home / 'evidence'
root = home / 'candidate'
rows = json.loads((out / 'checks.json').read_text())
assert len(rows) == 27, len(rows)
log = out / 'test_dispatch_stage.log'
text = log.read_text()
assert re.search(r'Ran 40 tests.*\n\nOK\s*$', text, re.S), text[-1000:]
rows.append(dict(name='SPACEDOCK_BIN=/Users/kent/.local/bin/spacedock python3 -B kc-dev-flow-2/scripts/test_dispatch_stage.py',
                 status='passed', exit=0, file=str(log), cases=40, skipped=0))
assert all(x['exit'] == 0 for x in rows)
ran = {re.search(r'(kc-dev-flow-2/\S+test_\S+\.py)', x['name'])[1] for x in rows if 'test_' in x['name']}
needed = {str(p.relative_to(root)) for p in (root / 'kc-dev-flow-2').rglob('test_*.py')}
assert ran == needed, dict(missing=sorted(needed-ran), extra=sorted(ran-needed))
(out / 'checks.json').write_text(json.dumps(rows, indent=2) + '\n')
summary = dict(head='3567082b0ec1eeb59346b2d82887a07bc5ffc2fb',
               commands=len(rows), all_passed=True, cases=sum(x['cases'] for x in rows),
               optional_skips=sum(x['skipped'] for x in rows), package_test_files=len(needed),
               criterion_controls=len(json.loads((out/'mutations.json').read_text())),
               repair_controls=len(json.loads((out/'repair-mutations.json').read_text())))
(out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
report = home / 'validation.md'
report.write_text(report.read_text().replace('PACKAGE_SUMMARY',
    f"All {summary['commands']} package-check commands exited 0, with {summary['cases']} unittest cases including {summary['optional_skips']} optional skips (`evidence/checks.json`, `evidence/summary.json`). The real-binary stage suite has 40 passing cases and no skips (`evidence/test_dispatch_stage.log`)."))
print(json.dumps(summary, indent=2))
