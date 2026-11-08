import importlib.util
import json
from pathlib import Path
import sys

root, out = Path(sys.argv[1]), Path(sys.argv[2])
spec = importlib.util.spec_from_file_location('candidate_adr_tests', root / 'kc-adr/scripts/test_adr_lint.py')
tests = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tests)
fixture = tests.ProtectedPathTests()
adrs = {'0002-a.md': tests.protecting(2, 'tests/status.py', status='Superseded by 0003'),
        '0003-b.md': tests.protecting(3, 'tests/status.py')}
prefix = '# see docs/adr/0003-b.md\n'
cases = [
    ('same-line escaped status assertion', 'assert "## Status\\n\\nSuperseded by 0003" in Path("docs/adr/0002-a.md").read_text()\n', 0, None),
    ('multiline assertion remains rejected', 'assert "Superseded by 0003" in (\n    Path("docs/adr/0002-a.md").read_text())\n', 1, 'points at ADR 0002, Superseded by 0003'),
    ('regex assertion remains rejected', 'assert re.search(r"Superseded by \\d{4}", Path("docs/adr/0002-a.md").read_text())\n', 1, 'points at ADR 0002, Superseded by 0003'),
    ('same-line authority comment exception is intentional', '# see docs/adr/0002-a.md; Superseded by 0003\n', 0, None),
    ('wrong successor retains pointer diagnostic', 'assert "Superseded by 0004" in Path("docs/adr/0002-a.md").read_text()\n', 1, 'point it at 0003 or the record in force'),
    ('overlong successor remains rejected', 'assert "Superseded by 00030" in Path("docs/adr/0002-a.md").read_text()\n', 1, 'points at ADR 0002, Superseded by 0003'),
    ('authority elsewhere remains rejected', 'assert "Superseded by 0003" in Path("docs/adr/0002-a.md").read_text()\n# see docs/adr/0002-a.md\n', 1, 'points at ADR 0002, Superseded by 0003'),
]
rows = []
for name, body, expected, message in cases:
    actual, output = fixture.lint(adrs, {'tests/status.py': prefix + body})
    passed = actual == expected and (message is None or message in output)
    rows.append({'name': name, 'status': 'passed' if passed else 'failed', 'exit': actual,
                 'expected': expected, 'input': prefix + body, 'output': output})
    out.write_text(json.dumps(rows, indent=2) + '\n')
    assert passed, rows[-1]
    print(f'{name}: exit {actual}, expected {expected}')
