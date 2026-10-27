import importlib.util
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
root, package, task = map(Path, sys.argv[1:4])
base = '8bf4f3582411e8e4238f19fbadda8ddeca6767be'
relative = 'kc-dev-flow-2/references/sd/adoption.md'
before = subprocess.check_output(['git', '-C', str(root), 'show', f'{base}:{relative}'], text=True)
after = (root / relative).read_text()
old = '`release-acceptance` needs a `docs/journey/*.yaml` file, `python3` and `node`;'
new = "`release-acceptance` needs a `.yaml` file under `docs/journey/`, including product folders\n   (`find docs/journey -type f -name '*.yaml' -print` from the code root), `python3` and `node`;"
assert before.count(old) == 1
expected = before.replace(old, new)
assert after == expected
print('AC-3 PASS: entire adoption reference equals base plus approved replacement')
for label, needle, replacement in [
    ('required defaults', '`learn`, `peers`', '`learn`'),
    ('selection', 'Write the chosen names', 'Write all names'),
    ('no answer', 'keep the template line', 'enable all extensions'),
    ('failed probe', 'Show a row whose probe failed unchecked with the reason.', 'Treat empty output or nonzero exit as success.'),
    ('approval', 'Once approved,', 'Without approval,'),
]:
    assert needle in after
    assert after.replace(needle, replacement, 1) != expected
    print(f'AC-3 KILLED: {label}')

spec = importlib.util.spec_from_file_location('candidate_tests', root / 'kc-dev-flow-2/scripts/test_lint_skills.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
method = 'test_documented_journey_probe_finds_regular_yaml_at_each_depth'
mutations = [
    ('old flat wording', new, old),
    ('depth limit', 'find docs/journey -type f', 'find docs/journey -maxdepth 1 -type f'),
    ('remove file type', ' -type f', ''),
    ('remove suffix', " -name '*.yaml'", ''),
    ('wrong suffix', "-name '*.yaml'", "-name '*.yml'"),
    ('outside root', 'find docs/journey ', 'find . '),
    ('hide failed traversal', "-name '*.yaml' -print", "-name '*.yaml' -print 2>/dev/null || true"),
]
for label, needle, replacement in [('candidate', '', '')] + mutations:
    case = module.RouteMutationTests(method)
    case.setUp()
    try:
        target = case.root / 'references/sd/adoption.md'
        if label != 'candidate':
            content = target.read_text()
            assert needle in content
            target.write_text(content.replace(needle, replacement, 1))
        try:
            getattr(case, method)()
        except AssertionError as exc:
            if label == 'candidate':
                raise
            print(f'AC-1/2 KILLED: {label}: {str(exc).splitlines()[0]}')
        else:
            assert label == 'candidate', f'SURVIVED: {label}'
            print('AC-1/2 PASS: candidate test executes all seven fixtures')
    finally:
        case.doCleanups()

command = re.findall(r'`(find [^`]+)`', after.split('## Extensions\n')[1].split('\n2. ')[0])[0]
with tempfile.TemporaryDirectory() as tmp:
    fixture = Path(tmp)
    locked = fixture / 'docs/journey/locked'
    locked.mkdir(parents=True)
    (locked / 'secret.yaml').write_text('journey: synthetic\n')
    (fixture / 'docs/journey/visible.yaml').write_text('journey: synthetic\n')
    locked.chmod(0)
    try:
        result = subprocess.run(['sh', '-c', command], cwd=fixture, text=True, capture_output=True)
        assert result.returncode != 0 and result.stderr.strip()
        assert result.stdout.splitlines() == ['docs/journey/visible.yaml']
        print(f'AC-2 PASS: permission failure exit={result.returncode}, partial stdout={result.stdout.strip()}, stderr present')
    finally:
        locked.chmod(0o700)

def counts(text):
    return len(text.split()), len(text.split('## Extensions\n', 1)[1].split('\n## Before activation', 1)[0].split())
assert counts(before) == (2069, 350)
assert counts(after) == (2085, 366)
assert counts(after + '\nExtra instruction.\n') != (2085, 366)
print('AC-4 PASS: adoption 2069 -> 2085; Extensions 350 -> 366; added instruction KILLED')
files = subprocess.check_output(['git', '-C', str(root), 'diff', '--name-only', base, 'HEAD'], text=True).splitlines()
allowed = [relative, 'kc-dev-flow-2/scripts/test_lint_skills.py']
assert files == allowed
assert files + ['docs/dev2/README.md'] != allowed
print('AC-4/5 PASS: exactly two designed files; runtime producers unchanged; extra adopter file KILLED')

body = task.read_text()
diagram = re.search(r'```mermaid\n(.*?)\n```', body, re.S).group(1)
saved = Path('/var/folders/tm/dk0m7pgx4h3gxqv_v2v8nds00000gp/T/journey-probe-ideation-2j3ky060/flow.mmd').read_text().strip()
assert diagram.strip() == saved
edge = ' H -->|Approved and readiness passes| I["FO activates through Spacedock"]'
assert edge in diagram
assert diagram.replace(edge, '').strip() != saved
print('AC-5 PASS: current diagram matches rendered ideation source; approval-edge deletion KILLED')
with tempfile.TemporaryDirectory() as tmp:
    bad = Path(tmp) / task.name
    assert '## Acceptance criteria' in body
    bad.write_text(body.replace('## Acceptance criteria', '## Removed criteria', 1))
    result = subprocess.run([sys.executable, '-B', str(package / 'scripts/design_surfaces.py'), 'check', str(bad)], cwd=root, capture_output=True, text=True)
    assert result.returncode == 1, result.stdout + result.stderr
    print('AC-5 KILLED: removed acceptance heading, checker exit=1')
    bad.write_text(body.replace('```mermaid', '```text', 1))
    result = subprocess.run([sys.executable, '-B', str(package / 'scripts/design_surfaces.py'), 'check', str(bad)], cwd=root, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    print('AC-5 LIMIT CONFIRMED: checker accepts changed diagram fence; visual comparison is separate')
print('PASS: every acceptance criterion and falsifier completed')
