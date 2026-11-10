import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

wt, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
out.mkdir(parents=True, exist_ok=True)
expected_head = '72216e2e947e962737a17c6e61ef3800f9d639c4'
assert subprocess.check_output(['git', '-C', str(wt), 'rev-parse', 'HEAD'], text=True).strip() == expected_head
for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_COMMON_DIR'):
    os.environ.pop(key, None)
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
sys.path.insert(0, str(wt / 'kc-dev-flow-2/scripts'))
from test_laws_check import Repo, task, laws, L4Test
from design_surfaces import move_defects

scenarios = []


def body(ids, marked=True, payload=True):
    live = ''.join(f'**AC-{n}** live criterion {n}.\n' for n in ids)
    live += '**AC-9** ' + ('Amended by Captain, amendment 1: ' if marked else '') + 'replacement.\n'
    text = task(body='## Acceptance criteria\n' + live +
                '\n## Captain amendments\n\n### Amendment 1 — 2026-11-10, chat\n'
                'Captain: replace these three criteria\nSupersedes: AC-1, AC-2, AC-3\n')
    if payload:
        text += '\nSuperseded text:\n\n**AC-1** old one.\n**AC-2** old two.\n**AC-3** old three.\n'
    return text


def proposed_delta(previous, current):
    """Analysis-only per-id delta; this does not replace the candidate runner."""
    added = []
    for defect in current:
        if defect[0] == 'reused':
            prior_ids = {ident for old in previous if old[:2] == defect[:2] for ident in old[2]}
            fresh = tuple(ident for ident in defect[2] if ident not in prior_ids)
            if fresh:
                added.append((*defect[:2], fresh))
        elif defect not in previous:
            added.append(defect)
    return added


class ReusedIdEvents(unittest.TestCase):
    def transition(self, old_ids, new_ids, old_marked=True, new_marked=True):
        tmp = tempfile.TemporaryDirectory(prefix='amendment-f1-')
        self.addCleanup(tmp.cleanup)
        repo = Repo(Path(tmp.name) / 'state')
        readme = Path(tmp.name) / 'README.md'
        readme.write_text('---\nextensions: []\n---\n')
        base = repo.commit('record only', t=body((1, 2, 3), marked=False, payload=False))
        old_text, new_text = body(old_ids, old_marked), body(new_ids, new_marked)
        if new_text == old_text:
            new_text += '\n## Notes\nUnrelated note.\n'
        before = repo.commit('introduce moved criteria', t=old_text)
        intro = laws(repo.path, '--before', base, '--after', before, '--readme', readme)
        after = repo.commit('edit live criteria only', t=new_text)
        result = laws(repo.path, '--before', before, '--after', after, '--readme', readme)
        previous, current = move_defects(old_text.splitlines()), move_defects(new_text.splitlines())
        rows = [line for line in result[1].splitlines() if line.startswith('violation: L4 ')]
        self.assertIn('L3 amendment-append-only: 1 events judged', result[1])
        self.assertRegex(result[1], r'L3 amendment-append-only: [^\n]+, 0 violated')
        scenarios.append({'test': self.id(), 'before': before, 'after': after, 'intro_exit': intro[0],
                          'intro_output': intro[1], 'exit': result[0], 'output': result[1],
                          'previous_defects': previous, 'current_defects': current,
                          'proposed_delta': proposed_delta(previous, current)})
        return result[0], rows, after

    def test_partial_repair_adds_no_event(self):
        code, lines, _ = self.transition((1, 2), (2,))
        self.assertEqual((code, lines), (0, []))

    def test_growth_reports_only_the_added_id(self):
        code, lines, commit = self.transition((1, 2), (1, 2, 3))
        self.assertEqual(code, 1)
        self.assertEqual(lines, [f'violation: L4 amendment-moves-use-fresh-ids task=t.md commit={commit[:12]} amendment=1 reused ids: AC-3'])

    def test_mixed_repair_and_addition_reports_only_the_added_id(self):
        code, lines, commit = self.transition((1, 2), (2, 3))
        self.assertEqual(code, 1)
        self.assertEqual(lines, [f'violation: L4 amendment-moves-use-fresh-ids task=t.md commit={commit[:12]} amendment=1 reused ids: AC-3'])

    def test_reordering_ids_adds_no_event(self):
        code, lines, _ = self.transition((1, 2), (2, 1))
        self.assertEqual((code, lines), (0, []))

    def test_complete_repair_adds_no_event(self):
        code, lines, _ = self.transition((1, 2), ())
        self.assertEqual((code, lines), (0, []))

    def test_persistent_unmarked_replacement_adds_no_event(self):
        code, lines, _ = self.transition((), (), False, False)
        self.assertEqual((code, lines), (0, []))

    def test_partial_reuse_repair_does_not_repeat_unmarked(self):
        _, lines, _ = self.transition((1, 2), (2,), False, False)
        self.assertFalse(any('unmarked replacement' in line for line in lines))

    def test_new_unmarked_replacement_is_reported(self):
        code, lines, commit = self.transition((), (), True, False)
        self.assertEqual(code, 1)
        self.assertEqual(lines, [f'violation: L4 amendment-moves-use-fresh-ids task=t.md commit={commit[:12]} amendment=1 unmarked replacement'])

    def test_repaired_unmarked_replacement_adds_no_event(self):
        code, lines, _ = self.transition((), (), False, True)
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


suite = unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(ReusedIdEvents),
                           L4Test('test_repaired_heading_reports_previously_unjudged_defect')])
with (out / 'tests.log').open('w') as stream:
    result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=RecordedResult).run(suite)
(out / 'tests.json').write_text(json.dumps(result.rows, indent=2) + '\n')
(out / 'scenarios.json').write_text(json.dumps(scenarios, indent=2) + '\n')
identity = {'candidate': expected_head, 'tests_run': result.testsRun, 'failures': len(result.failures),
            'errors': len(result.errors), 'product_status': subprocess.check_output(['git', '-C', str(wt), 'status', '--porcelain'], text=True),
            'source_sha256': {p: hashlib.sha256((wt / p).read_bytes()).hexdigest() for p in
                              ('kc-dev-flow-2/scripts/laws_check.py', 'kc-dev-flow-2/scripts/design_surfaces.py', 'kc-dev-flow-2/scripts/test_laws_check.py')}}
(out / 'identity.json').write_text(json.dumps(identity, indent=2) + '\n')
assert not identity['product_status']
print(f'{result.testsRun} tests, {len(result.failures)} assertion failures, {len(result.errors)} errors; product worktree unchanged')
sys.exit(0 if result.wasSuccessful() else 1)
