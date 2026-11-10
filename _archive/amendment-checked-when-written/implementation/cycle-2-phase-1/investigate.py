import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from proposal import proposed_source, write_diff

wt, out = Path(sys.argv[1]).resolve(), Path(__file__).resolve().parent
head = 'd7502656c765e36ce3d24be8602862ccc2551254'
git = lambda *args: subprocess.check_output(['git', '-C', str(wt), *args], text=True).strip()
assert git('rev-parse', 'HEAD') == head
assert git('branch', '--show-current') == 'spacedock-ensign/amendment-checked-when-written'
assert not git('status', '--porcelain')
for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_COMMON_DIR'):
    os.environ.pop(key, None)
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
sys.path.insert(0, str(wt / 'kc-dev-flow-2/scripts'))
from test_laws_check import Repo, task, laws
import design_surfaces as ds

source, changed = proposed_source(wt)
write_diff(wt, out)
probes, comparisons = [], []


def body(fence=None, marked=False, moved=False, waived=False, example=False):
    live = '**AC-2** old outcome.\n' if not moved else ('' if waived else '**AC-5** ' +
           ('Amended by Captain, amendment 1: ' if marked else '') + 'replacement outcome.\n')
    code = f'{fence}md\n**AC-9** Amended by Captain, amendment 1: example only.\n{fence}\n' if example else ''
    return task(body='## Scope\nNon-goals: unrelated work\nBudget: one task\nStop condition: unapproved scope\n'
                '\n## FO alignment\nSurfaces: none\nVisible change: none\n'
                '\n## Acceptance criteria\n' + live + code +
                '\n## Captain amendments\n### Amendment 1 — 2026-11-10, chat\n'
                'Captain: replace old outcome\nSupersedes: AC-2' +
                (' (no replacement: moved to another task)' if waived else '') + '\n' +
                ('\nSuperseded text:\n\n**AC-2** old outcome.\n' if moved else ''))


class F3Tests(unittest.TestCase):
    variant = 'candidate'
    runner = wt / 'kc-dev-flow-2/scripts/laws_check.py'
    design = wt / 'kc-dev-flow-2/scripts/design_surfaces.py'

    def transition(self, fence, *, marked=False, moved=True, waived=False):
        tmp = tempfile.TemporaryDirectory(prefix='amendment-f3-')
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        repo = Repo(root / 'state')
        readme = root / 'README.md'
        readme.write_text('---\nextensions: []\n---\n')
        before = repo.commit('record only', t=body(waived=waived))
        text = body(fence, marked, moved, waived, True)
        event = repo.commit('worker writes replacement and example', t=text)
        code, stdout = laws(repo.path, '--before', before, '--after', event, '--readme', readme, runner=self.runner)
        parsed, issues = ds.parse_amendments(text.splitlines())
        self.assertEqual(issues, [])
        self.assertEqual(len(parsed), 1)
        self.assertRegex(stdout, r'L3 amendment-append-only: [^\n]+, 0 violated')
        row = {'variant': self.variant, 'test': self.id(), 'fence': fence, 'marked': marked,
               'moved': moved, 'waived': waived, 'before': before, 'event': event,
               'exit': code, 'output': stdout, 'parse_issues': issues}
        probes.append(row)
        gates = []
        for label, script in (('candidate', wt / 'kc-dev-flow-2/scripts/design_surfaces.py'), ('proposal', proposal_design)):
            for mode in ([], ['--seed']):
                result = subprocess.run([sys.executable, '-B', str(script), 'check', *mode, str(repo.path / 't.md')],
                                        capture_output=True, text=True)
                gates.append({'implementation': label, 'mode': 'seed' if mode else 'check',
                              'exit': result.returncode, 'output': result.stdout + result.stderr})
        for mode in ('check', 'seed'):
            a, b = [r for r in gates if r['mode'] == mode]
            self.assertEqual((a['exit'], a['output']), (b['exit'], b['output']))
        comparisons.append({'test': self.id(), 'variant': self.variant, 'fence': fence,
                            'marked': marked, 'moved': moved, 'waived': waived, 'verdicts': gates})
        return code, [line for line in stdout.splitlines() if line.startswith('violation: L4 ')], event

    def test_tilde_example_does_not_supply_live_marker(self):
        code, lines, event = self.transition('~~~')
        self.assertEqual((code, lines), (1, [f'violation: L4 amendment-moves-use-fresh-ids task=t.md commit={event[:12]} amendment=1 unmarked replacement']))

    def test_backtick_example_does_not_supply_live_marker(self):
        code, lines, event = self.transition('```')
        self.assertEqual((code, lines), (1, [f'violation: L4 amendment-moves-use-fresh-ids task=t.md commit={event[:12]} amendment=1 unmarked replacement']))

    def test_real_marked_replacement_stays_green(self):
        for fence in ('```', '~~~'):
            with self.subTest(fence=fence):
                code, lines, _ = self.transition(fence, marked=True)
                self.assertEqual((code, lines), (0, []))

    def test_waived_move_stays_green(self):
        for fence in ('```', '~~~'):
            with self.subTest(fence=fence):
                code, lines, _ = self.transition(fence, waived=True)
                self.assertEqual((code, lines), (0, []))

    def test_record_only_stays_green(self):
        for fence in ('```', '~~~'):
            with self.subTest(fence=fence):
                code, lines, _ = self.transition(fence, moved=False)
                self.assertEqual((code, lines), (0, []))


class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rows = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.rows.append({'name': test.id(), 'status': 'passed'})

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.rows.append({'name': test.id(), 'status': 'failed', 'message': self._exc_info_to_string(err, test)})

    def addError(self, test, err):
        super().addError(test, err)
        self.rows.append({'name': test.id(), 'status': 'failed', 'message': self._exc_info_to_string(err, test)})


with tempfile.TemporaryDirectory(prefix='amendment-f3-proposed-package-') as tmp:
    pkg = Path(tmp)
    shutil.copytree(wt / 'kc-dev-flow-2/scripts', pkg / 'scripts', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    (pkg / 'references/sd').mkdir(parents=True)
    shutil.copy(wt / 'kc-dev-flow-2/references/sd/laws.md', pkg / 'references/sd/laws.md')
    proposal_design = pkg / 'scripts/design_surfaces.py'
    proposal_design.write_text(changed)
    assert not list(pkg.rglob('*.pyc'))
    results = {}
    for variant, runner in (('candidate', wt / 'kc-dev-flow-2/scripts/laws_check.py'), ('proposal', pkg / 'scripts/laws_check.py')):
        F3Tests.variant, F3Tests.runner = variant, runner
        with (out / f'{variant}-tests.log').open('w') as log:
            result = unittest.TextTestRunner(stream=log, verbosity=2, resultclass=RecordedResult).run(
                unittest.defaultTestLoader.loadTestsFromTestCase(F3Tests))
        results[variant] = {'tests': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors)}
        (out / f'{variant}-tests.json').write_text(json.dumps(result.rows, indent=2) + '\n')
    with (out / 'proposal-existing-l4.log').open('w') as log:
        existing = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'test_laws_check.L4Test'],
                                  cwd=pkg / 'scripts', stdout=log, stderr=subprocess.STDOUT)
    assert existing.returncode == 0, (out / 'proposal-existing-l4.log').read_text()
    assert not list(pkg.rglob('*.pyc'))

assert results == {'candidate': {'tests': 5, 'failures': 1, 'errors': 0},
                   'proposal': {'tests': 5, 'failures': 0, 'errors': 0}}, results
(out / 'probes.json').write_text(json.dumps(probes, indent=2) + '\n')
(out / 'gate-comparison.json').write_text(json.dumps(comparisons, indent=2) + '\n')
assert not git('status', '--porcelain') and git('rev-parse', 'HEAD') == head
identity = {'candidate': head, 'product_status': 'clean', 'product_tree': git('rev-parse', 'HEAD^{tree}'),
            'results': results, 'proposal_existing_l4_exit': existing.returncode,
            'source_sha256': {str(p.relative_to(wt)): hashlib.sha256(p.read_bytes()).hexdigest() for p in
                             (wt / 'kc-dev-flow-2/scripts/design_surfaces.py', wt / 'kc-dev-flow-2/scripts/laws_check.py',
                              wt / 'kc-dev-flow-2/scripts/test_laws_check.py')},
            'proposal_applied_to_product': False}
(out / 'identity.json').write_text(json.dumps(identity, indent=2) + '\n')
print('Candidate: 5 tests, one F3 assertion failure, no errors. Unapplied proposal copy: all 5 controls and 14 existing L4 regressions pass. Product remains unchanged.')
sys.exit(1)
